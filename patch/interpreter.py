from .objects import PythonHocObject, NetCon, PointProcess, VecStim
from .core import transform, transform_netcon, _suppress_stdout
from .exceptions import *
import io


class PythonHocInterpreter:
    def __init__(self):
        from neuron import h

        self.__dict__["_PythonHocInterpreter__h"] = h
        # Wrapping should occur around all calls to functions that share a name with
        # child classes of the PythonHocObject like h.Section, h.NetStim, h.NetCon
        self.__object_classes = PythonHocObject.__subclasses__().copy()
        self.__requires_wrapping = [cls.__name__ for cls in self.__object_classes]
        self.__loaded_extensions = []

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
        with io.StringIO() as error_stream:
            try:
                with _suppress_stdout(error_stream):
                    connection = NetCon(
                        self, self.__h.NetCon(nrn_source, nrn_target, *args, **kwargs)
                    )
            except RuntimeError as e:
                error = error_stream.getvalue()
                if error.find("must be a point process or NULLObject") != -1:
                    if error.find("arg 1") != -1:
                        raise HocConnectError(
                            "Source is not a point process. Transformed type: '{}'".format(
                                type(nrn_source)
                            )
                        ) from None
                    if error.find("arg 2") != -1:
                        raise HocConnectError(
                            "Target is not a point process. Transformed type: '{}'".format(
                                type(nrn_target)
                            )
                        ) from None
                raise HocError(error) from None
        connection.__ref__(self)
        connection.__ref__(target)
        if not hasattr(source, "_connections"):
            raise NotConnectableError(
                "Source "
                + str(source)
                + " is not connectable. It lacks attribute _connections required to form NetCons."
            )
        if not hasattr(target, "_connections"):
            raise NotConnectableError(
                "Target "
                + str(target)
                + " is not connectable. It lacks attribute _connections required to form NetCons."
            )
        source._connections[target] = connection
        target._connections[source] = connection
        return connection

    def PointProcess(self, factory, target, *args, **kwargs):
        """
      Creates a point process from a h.MyMechanism factory.

      :param factory: A point process method from the HocInterpreter.
      :type factory: function
      :param target: The Segment this point process has to be inserted into.
      :type target: :class:`.objects.Segment`
    """
        if hasattr(target, "__arc__"):
            target = target(target.__arc__())
        nrn_target = transform(target)
        point_process = factory(nrn_target, *args, **kwargs)
        return PointProcess(self, point_process)

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

    @property
    def time(self):
        if not hasattr(self, "_time"):
            t = self.Vector()
            # Fix for upstream NEURON bug. See https://github.com/neuronsimulator/nrn/issues/416
            try:
                t.record(self._ref_t)
            except RuntimeError as e:
                self.__dud_section = self.Section(name="this_is_here_to_record_time")
                # Recurse to try again.
                return self.time
            self._time = t
        return self._time

    def load_extension(self, extension):
        if extension in self.__loaded_extensions:
            return
        from . import get_data_file

        hoc_file = get_data_file("extensions", extension + ".hoc").replace("\\", "/")
        self.__h.load_file(hoc_file)
        self.__loaded_extensions.append(extension)
