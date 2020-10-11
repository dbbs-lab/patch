from .objects import PythonHocObject, NetCon, PointProcess, VecStim, Section, IClamp, SectionRef
from .core import (
    transform,
    transform_netcon,
    assert_connectable,
    is_section,
    transform_arc,
)
from .exceptions import *
from .error_handler import catch_hoc_error, CatchNetCon, CatchSectionAccess, _suppress_nrn


class PythonHocInterpreter:
    def __init__(self):
        from neuron import h

        self.__dict__["_PythonHocInterpreter__h"] = h
        # Wrapping should occur around all calls to functions that share a name with
        # child classes of the PythonHocObject like h.Section, h.NetStim, h.NetCon
        self.__object_classes = PythonHocObject.__subclasses__().copy()
        self.__requires_wrapping = [cls.__name__ for cls in self.__object_classes]
        self.__loaded_extensions = []
        self.load_file("stdrun.hoc")
        self.runtime = 0

    def __getattr__(self, attr_name):
        # Get the missing attribute from h, if it requires wrapping return a wrapped
        # object instead.
        attr = getattr(self.__h, attr_name)
        if attr_name in self.__requires_wrapping:
            return self.wrap(attr, attr_name)
        else:
            return attr

    def __setattr__(self, attr, value):
        if hasattr(self.__h, attr):
            setattr(self.__h, attr, value)
        else:
            self.__dict__[attr] = value

    def wrap(self, factory, name):
        def wrapper(*args, **kwargs):
            obj = factory(*args, **kwargs)
            cls = next((c for c in self.__object_classes if c.__name__ == name), None)
            return cls(self, obj)

        return wrapper

    def NetCon(self, source, target, *args, **kwargs):
        nrn_source = transform_netcon(source)
        nrn_target = transform_netcon(target)
        # Change the NetCon signature so that weight, delay and threshold become
        # independent optional keyword arguments.
        setters = {}
        # Set sensible defaults: NetCons appear not to work sometimes if they're not set.
        defaults = {"weight": 0.1, "delay": 0, "threshold": -20}
        setter_keys = ["weight", "delay", "threshold"]
        for key in setter_keys:
            if key not in kwargs:
                kwargs[key] = defaults[key]
            setters[key] = kwargs[key]
            del kwargs[key]
        if is_section(source):
            kwargs["sec"] = transform(source)
        # Execute HOC NetCon and wrap result into `connection`
        with catch_hoc_error(CatchNetCon, nrn_source=nrn_source, nrn_target=nrn_target):
            connection = NetCon(
                self, self.__h.NetCon(nrn_source, nrn_target, *args, **kwargs),
            )
        # Set the weight, delay and threshold independently
        for k, v in setters.items():
            if k == "weight":
                if hasattr(type(v), "__iter__"):  # pragma: nocover
                    for i, w in enumerate(v):
                        connection.weight[i] = w
                else:
                    connection.weight[0] = v
            else:
                setattr(connection, k, v)
        # Have the NetCon reference source and target
        connection.__ref__(source)
        connection.__ref__(target)
        # If target is None, this NetCon is used as a spike detector.
        if target is not None:
            # Connect source and target.
            assert_connectable(source, label="Source")
            assert_connectable(target, label="Target")
            source._connections[target] = connection
            target._connections[source] = connection
        elif hasattr(source, "__ref__"):
            # Since the connection isn't established, make sure that the source and NetCon
            # reference eachother both ways
            source.__ref__(connection)

        return connection

    def ParallelCon(self, a, b, output=True, *args, **kwargs):
        a_int = isinstance(a, int)
        b_int = isinstance(b, int)
        gid = a if a_int else b
        if a_int != b_int:
            if b_int:
                source = a
                nc = self.NetCon(source, None, *args, **kwargs)
                self.parallel.set_gid2node(gid, self.parallel.id())
                self.parallel.cell(gid, nc)
                if output:
                    self.parallel.outputcell(gid)
                return nc
            else:
                target = b
                nrn_target = transform_netcon(target)
                nrn_nc = self.parallel.gid_connect(gid, nrn_target)
                # Wrap the gid_connect NetCon
                nc = NetCon(self, nrn_nc)
                nc.__ref__(b)
                b.__ref__(nc)
                if "delay" in kwargs:
                    nc.delay = kwargs["delay"]
                if "weight" in kwargs:
                    nc.weight[0] = kwargs["weight"]
                nc.threshold = kwargs["threshold"] if "threshold" in kwargs else -20.0
                return nc
        else:
            raise ParallelConnectError(
                "Exactly one of the first or second arguments has to be a GID."
            )

    def SectionRef(self, *args, sec=None):
        if len(args) > 1:
            raise TypeError(f"SectionRef takes 1 positional argument but {len(args)} given.")
        if sec is None:
            if args:
                sec = args[0]
            else:
                sec = self.cas()
                if not sec:
                    raise RuntimeError("SectionRef() failed as there is no currently accessed section available. Please specify a Section.")
        ref = SectionRef(self, self.__h.SectionRef(sec=transform(sec)))
        if transform(sec) is sec:
            sec = Section(self, sec)
        ref.__ref__(sec)
        ref.__dict__["sec"] = sec
        ref.section = sec
        return ref


    def ParallelContext(self):
        return self.parallel

    def PointProcess(self, factory, target, *args, **kwargs):
        """
          Creates a point process from a h.MyMechanism factory.

          :param factory: A point process method from the HocInterpreter.
          :type factory: function
          :param target: The object this point process has to be inserted into.
          :type target: :class:`.objects.PythonHocObject`
        """
        og_target = target
        if hasattr(target, "__arc__"):
            target = target(target.__arc__(), ephemeral=True)
        nrn_target = transform(target)
        point_process = factory(nrn_target, *args, **kwargs)
        pp = PointProcess(self, point_process)
        og_target.__ref__(pp)
        pp.__ref__(og_target)
        return pp

    def VecStim(self, pattern=None, *args, **kwargs):
        import glia as g

        mod_name = g.resolve("VecStim")
        vec_stim = VecStim(self, getattr(self.__h, mod_name)(*args, **kwargs))
        if pattern is not None:
            pattern_vector = self.Vector(pattern)
            vec_stim.play(pattern_vector.__neuron__())
            self._vector = pattern_vector
            self._pattern = pattern
        return vec_stim

    def IClamp(self, x=0.5, sec=None):
        sec = sec if sec is not None else self.cas()
        clamp = IClamp(self, self.__h.IClamp(x, sec=transform(sec)))
        clamp.__ref__(sec)
        if hasattr(sec, "__ref__"):
            sec.__ref__(clamp)
        return clamp

    @property
    def time(self):
        if not hasattr(self, "_time"):
            t = self.Vector()
            # Fix for upstream NEURON bug. See https://github.com/neuronsimulator/nrn/issues/416
            try:
                with catch_hoc_error(CatchSectionAccess):
                    t.record(self._ref_t)
            except HocSectionAccessError as e:
                self.__dud_section = self.Section(name="this_is_here_to_record_time")
                # Recurse to try again.
                return self.time
            self._time = t
        return self._time

    def load_extension(self, extension):  # pragma: nocover
        if extension in self.__loaded_extensions:
            return
        from . import get_data_file

        hoc_file = get_data_file("extensions", extension + ".hoc").replace("\\", "/")
        self.__h.load_file(hoc_file)
        self.__loaded_extensions.append(extension)

    def finitialize(self, initial=None):
        if initial is not None:
            self.__h.finitialize(initial)
        else:
            self.__h.finitialize()
        self.runtime = 0
        self._finitialized = True

    def continuerun(self, time_stop, add=False):
        if not hasattr(self, "_finitialized"):  # pragma: nocover
            raise UninitializedError(
                "Cannot start NEURON simulation without first using `p.finitialize`."
            )
        if add:
            self.__h.continuerun(self.runtime + time_stop)
            self.runtime += time_stop
        else:
            self.__h.continuerun(time_stop)
            self.runtime = time_stop

    def run(self):
        if not hasattr(self, "_finitialized"):  # pragma: nocover
            raise UninitializedError(
                "Cannot start NEURON simulation without first using `p.finitialize`."
            )
        self.__h.run()

    def cas(self):
        # Currently error won't be triggered as h.cas() exits on undefined section acces:
        # https://github.com/neuronsimulator/nrn/issues/769
        try:
            with catch_hoc_error(CatchSectionAccess):
                return Section(self, self.__h.cas())
        except HocSectionAccessError: # pragma: nocover
            return None

    def _init_pc(self):
        if not hasattr(self, "_PythonHocInterpreter__pc"):
            # Completely rely on mpi4py to initialize MPI. See
            # https://github.com/neuronsimulator/nrn/issues/581
            # When it is fixed we can remove mpi4py as a dependency.
            from mpi4py import MPI

            # Check whether MPI and NEURON agree on the ParallelContext.
            # If not, make sure to help the user rectify this problem.
            if MPI.COMM_WORLD.size != self.__h.ParallelContext().nhost():
                raise RuntimeError(
                    "MPI could not be initialized. You're using NEURON {},"
                    + " please upgrade to NEURON 7.7+"
                    + " or make sure that you import `mpi4py` before importing"
                    + " either NEURON or Patch."
                )
            self.__pc = ParallelContext(self, self.__h.ParallelContext())

    @property
    def parallel(self):
        self._init_pc()
        return self.__pc

    def record(self, target):
        v = self.Vector()
        v.record(target)
        return v


class ParallelContext(PythonHocObject):
    def cell(self, gid, nc):
        transform(self).cell(gid, transform(nc))

    def broadcast(self, data, root=0):
        """
            Broadcast either a Vector or arbitrary picklable data. If ``data`` is a
            Vector, the Vectors are resized and filled with the data from the Vector in
            the ``root`` node. If ``data`` is not a Vector, it is pickled, transmitted and
            returned from this function to all nodes.

            :param data: The data to broadcast to the nodes.
            :type data: :class:`Vector <.objects.Vector>` or any picklable object.
            :param root: The id of the node that is broadcasting the data.
            :type root: int
            :returns: None (Vectors filled) or the transmitted data
            :raises: BroadcastError if ``neuron.hoc.HocObjects`` that aren't Vectors are
              transmitted
        """
        import neuron

        data_ptr = transform(data)
        # Is anyone broadcasting a HocObject?
        if isinstance(data_ptr, neuron.hoc.HocObject):
            # Comparing dir is used as a silly equality check because all NEURON object
            # have class 'neuron.hoc.HocObject'
            if dir(data_ptr) == dir(neuron.h.Vector()):
                # If this node is broadcasting a Vector, then proceed to traditional
                # broadcasting. If all nodes are broadcasting a Vector traditional
                # broadcasting will occur, otherwise a BroadcastError is thrown.
                transform(self).broadcast(data_ptr, root=root)
            else:
                # Send an empty vector so the other nodes don't hang.
                transform(self).broadcast(transform(self._interpreter.Vector()), root)
                raise BroadcastError(
                    "NEURON HocObjects cannot be broadcasted, they need to be created on their own nodes."
                )
        else:
            # If noone is sending a HocObject we proceed with picklable data broadcasting
            return self._broadcast(data, root=root)

    def _broadcast(self, data, root=0):
        import pickle

        if self.id() == root:
            try:
                v = self._interpreter.Vector(list(pickle.dumps(data)))
            except AttributeError as e:
                # Send an empty vector so the other nodes don't hang.
                transform(self).broadcast(transform(self._interpreter.Vector()), root)
                raise BroadcastError(str(e)) from None
        else:
            v = self._interpreter.Vector()
        v = transform(v)
        transform(self).broadcast(v, root)
        try:
            return pickle.loads(bytes([int(d) for d in v]))
        except EOFError:
            raise BroadcastError(
                "Root node did not transmit. Look for root node error."
            ) from None
