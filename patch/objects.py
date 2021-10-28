from .core import transform, transform_record, _is_sequence
from .error_handler import catch_hoc_error, CatchRecord


_registration_queue = []


def _safe_call(method):
    """
    Internal decorator to defer a method to the underlying NEURON object,
    unpacking all args and returning the result to the decorated method.
    """

    def caller(self, *args, **kwargs):
        call_result = self._safe_call(method.__name__, *args, **kwargs)
        return method(self, call_result, *args, **kwargs)

    return caller


class PythonHocObject:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        try:
            from .interpreter import PythonHocInterpreter
        except ImportError:
            _registration_queue.append(cls)
            return

        PythonHocInterpreter.register_hoc_object(cls)

    def __init__(self, interpreter, ptr):
        # Initialize ourselves with a reference to our own "pointer"
        # and prepare a list for other references.
        self._neuron_ptr = transform(ptr)
        self._references = []
        self._interpreter = interpreter

    def __getattr__(self, attr):
        # Return underlying attributes that aren't explicitly set on the wrapper
        return getattr(self.__dict__["_neuron_ptr"], attr)

    def __setattr__(self, attr, value):
        # Set attributes on the underlying pointer, and set on self if they don't
        # exist on the underlying pointer. This allows you to set arbitrary values
        # on the NEURON objects as you would be able to with a real Pythonic object.
        try:
            setattr(self._neuron_ptr, attr, value)
        except (LookupError, AttributeError) as _:
            self.__dict__[attr] = value

    def __call__(self, *args, **kwargs):
        # Relay calls to self to the underlying pointer
        return self._neuron_ptr(*args, **kwargs)

    def __iter__(self):
        # Create an iterator from ourselves.
        ptr = self.__neuron__()
        if type(ptr).__name__ == "Section":
            # Iter on section isn't a full iterator.
            return ptr
        # Relay iteration to the underlying pointer
        try:
            return iter(ptr)
        except TypeError:
            raise

    def __bool__(self):
        return True

    def __len__(self):
        # Relay length to pointer
        return len(self.__neuron__())

    def __eq__(self, other):
        return transform(self) is transform(other)

    def __repr__(self):
        ostr = object.__repr__(self)
        return ostr[: ostr.rindex("at")] + "pointing to '" + str(self.__neuron__()) + "'>"

    def __hash__(self):
        return object.__hash__(self)

    def __neuron__(self):
        # Magic method that allows duck typing of this object as something that
        # needs to be represented differently when passed to NEURON.
        return self._neuron_ptr

    def __ref__(self, obj):
        # Magic method that will store a strong reference to another object.
        if obj not in self._references:
            self._references.append(obj)

    def __deref__(self, obj):
        # Magic method that will remove a strong reference to another object.
        try:
            self._references.remove(obj)
            return True
        except ValueError:
            return False

    def _safe_call(self, func_name, *args, **kwargs):
        """
        Unpacks all arguments to their NEURON variant and retrieves the naked
        function from the HocObject then calls it.
        """
        func = getattr(transform(self), func_name)
        args = [transform(a) for a in args]
        kwargs = {k: transform(v) for k, v in kwargs.items()}
        return func(*args, **kwargs)


class connectable:
    def __init__(self):
        # Prepare a dictionary that lists which other NEURON parts this is connected to
        self._connections = {}


class Section(PythonHocObject, connectable):
    def __init__(self, *args, **kwargs):
        PythonHocObject.__init__(self, *args, **kwargs)
        connectable.__init__(self)

    def connect(self, target, *args, **kwargs):
        """
        Connect this section to another one as child section.
        """
        nrn_target = transform(target)
        self.__neuron__().connect(nrn_target, *args, **kwargs)
        if hasattr(target, "__ref__"):
            target.__ref__(self)
        self.__ref__(target)

    def __arc__(self):
        """
        Return the default arc-position (a point in the closed interval [0, 1]
        that represents the position between start and end of the Section).

        Defaults to 0.5
        """
        return 0.5

    def __netcon__(self):
        """
        Return the default pointer to connect to a NetCon.

        Defaults to ``self(0.5)._ref_v``
        """
        return self(self.__arc__()).__netcon__()

    def __record__(self):
        """
        Return the default pointer to record.

        Defaults to ``self(0.5)._ref_v``
        """
        return self(self.__arc__()).__record__()

    def __call__(self, x, ephemeral=False, *args, **kwargs):
        v = super().__call__(x, *args, **kwargs)
        if type(v).__name__ != "Segment":  # pragma: no cover
            raise TypeError("Section call did not return a Segment.")
        seg = Segment(self._interpreter, v, self)
        if not ephemeral:
            # By default store references to segments, but allow for them to be
            # garbage collected if `ephemeral=True`
            seg.__ref__(self)
            self.__ref__(seg)
        return seg

    def __iter__(self, *args, **kwargs):
        iter = super().__iter__(*args, **kwargs)
        for v in iter:
            if type(v).__name__ != "Segment":  # pragma: no cover
                raise TypeError("Section iteration did not return a Segment.")
            yield Segment(self._interpreter, v, self)

    def insert(self, *args, **kwargs):
        """
        Insert a mechanism into the Section.
        """
        # Catch nrn.Section return value, always seems to be self.
        # So if Neuron doesn't raise an error, return self.
        # Probably for method chaining?
        self.__neuron__().insert(*args, **kwargs)
        return self

    def connect_points(self, target, x=None, **kwargs):
        """
        Connect a Segment of this Section to a target. Usually used to connect
        the membrane potential to a point process.
        """
        if x is None:
            x = self.__arc__()
        segment = self(x)
        self.push()
        nc = self._interpreter.NetCon(segment, target, **kwargs)
        self._interpreter.pop_section()
        return nc

    def set_dimensions(self, length, diameter):
        """
        Set the length and diameter of the piece of cable this Section will
        represent in the simulation.
        """
        self.L = length
        self.diam = diameter

    def set_segments(self, segments):
        """
        Set the number of discrete points where equations are solved during simulation.
        """
        self.nseg = segments

    def add_3d(self, points, diameters=None):
        """
        Add a new 3D point to this section xyz data.

        :param points: A 2D array of xyz points.
        :param diameters: A scalar or array of diameters corresponding to the points. Default value is the section diameter.
        :type diameters: float or array
        """
        if diameters is None:
            diameters = [self.diam for _ in range(len(points))]
        if not _is_sequence(diameters):
            diameters = [diameters for _ in range(len(points))]
        self.__neuron__().push()
        for point, diameter in zip(points, diameters):
            self._interpreter.pt3dadd(*point, diameter)
        self._interpreter.pop_section()

    @property
    def points(self):
        """
        Return the 3d point information associated to this section.
        """
        import numpy

        return numpy.column_stack(
            (
                [self.x3d(n) for n in range(self.n3d())],
                [self.y3d(n) for n in range(self.n3d())],
                [self.z3d(n) for n in range(self.n3d())],
            )
        )

    def wholetree(self):
        return [Section(self._interpreter, s) for s in self.__neuron__().wholetree()]

    def record(self, x=None):
        """
        Record the Section at a certain point.

        :param x: Arcpoint, defaults to ``__arc__`` if omitted.
        :type x: float
        """
        if x is None:
            x = self.__arc__()
        if not hasattr(self, "recordings"):
            self.recordings = {}
        if not x in self.recordings:
            recorder = self._interpreter.Vector()
            recorder.record(self(x))
            self.recordings[x] = recorder
            return recorder
        return self.recordings[x]

    def synapse(self, factory, *args, store=False, **kwargs):
        """
        Insert a synapse into the Section.

        :param factory: Callable that creates a point process, is given the
          Section as first argument and passes on all other args.
        :type factory: callable
        :param store: Store the synapse on the Section in a ``synapses``
          attribute.
        :type store: bool
        """
        synapse = factory(self, *args, **kwargs)
        if store:
            if not hasattr(self, "synapses"):
                self.synapses = []
            self.synapses.append(synapse)
        return synapse

    def iclamp(self, x=0.5, delay=0, duration=100, amplitude=0):
        """
        Create a current clamp on the section.
        """
        clamp = self._interpreter.IClamp(x=x, sec=self)
        clamp.delay = delay
        clamp.dur = duration
        if _is_sequence(amplitude):
            # If its a sequence play it as a vector into the clamp
            dt = self._interpreter.dt
            t = self._interpreter.Vector([delay + dt * i for i in range(len(amplitude))])
            v = self._interpreter.Vector(amplitude, t)
            v.play(clamp._ref_amp, t.__neuron__())
            clamp.__ref__(v)
            clamp.__ref__(t)
        else:
            clamp.amp = amplitude
        return clamp

    def vclamp(self, x=0.5, delay=0, duration=100, after=0, voltage=-70, holding=-70):
        """
        Create a voltage clamp on the section.

        :param x: Location along the segment from 0 to 1.
        :type x: float
        :param delay: Duration of the pre-step holding interval, from `0` to `delay` ms.
        :type delay: float
        :param duration: Duration of the step interval, from `delay` to `delay + duration` ms.
        :type duration: float
        :param after: Duration of the post-step holding interval, from `delay + duration`
          to `delay + duration + after` ms.
        :type after: float
        :param voltage: Can be a single value to define the voltage during the step
          (`delay` to `delay + duration` ms), or 3 values to define the pre-step, step and
          post-step voltages altogether.
        :type voltage: Union[float, List[float]]
        :param holding: If `voltage` is a single value, `holding` is used for the pre-step
          and post-step voltages.
        :type holding: float
        :returns: A single electrode voltage clamp placed in the section.
        :rtype: :class:`.objects.SEClamp`
        """
        clamp = self._interpreter.SEClamp(x=x, sec=self)
        clamp.dur1 = delay
        clamp.dur2 = duration
        clamp.dur3 = after
        try:
            voltage = iter(voltage)
        except TypeError:
            clamp.amp1 = holding
            clamp.amp2 = voltage
            clamp.amp3 = holding
        else:
            voltage = list(voltage)
            clamp.amp1 = voltage[0]
            clamp.amp2 = voltage[1]
            clamp.amp3 = voltage[2]
        return clamp

    def push(self):
        """
        Return a context manager that pushes this Section onto the section stack
        and takes it off when the context is exited.
        """
        transform(self).push()

        return _SectionStackContextManager(self)

    def pop(self):
        """
        Pop this section off the section stack.
        """
        if self == self._interpreter.cas():
            self._interpreter.pop_section()
        else:
            raise RuntimeError(
                "Cannot pop this section as it is not on top of the section stack"
            )


class _SectionStackContextManager:
    def __init__(self, section):
        self._section = section

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self._section.pop()


class SectionRef(PythonHocObject):
    @property
    def child(self):
        return [Section(self._interpreter, s) for s in self.__neuron__().child]


class Vector(PythonHocObject):
    def record(self, target, *args, **kwargs):
        nrn_target = transform_record(target)
        with catch_hoc_error(CatchRecord, target=target):
            self.__neuron__().record(nrn_target, *args, **kwargs)
        self.__ref__(target)
        return self


class IClamp(PythonHocObject):
    pass


class SEClamp(PythonHocObject):
    pass


class NetStim(PythonHocObject, connectable):
    def __init__(self, *args, **kwargs):
        PythonHocObject.__init__(self, *args, **kwargs)
        connectable.__init__(self)


class VecStim(PythonHocObject, connectable):
    def __init__(self, *args, **kwargs):
        PythonHocObject.__init__(self, *args, **kwargs)
        connectable.__init__(self)

    @property
    def vector(self):
        return self._vector

    @property
    def pattern(self):
        return self._pattern.copy()


class NetCon(PythonHocObject):
    def record(self, vector=None):
        if vector is not None:
            self._neuron_ptr.record(transform(vector))
            self.recorder = vector
            if hasattr(vector, "__ref__"):
                vector.__ref__(self)
        else:
            if not hasattr(self, "recorder"):
                vector = self._interpreter.Vector()
                self._neuron_ptr.record(transform(vector))
                self.recorder = vector
                if hasattr(vector, "__ref__"):
                    vector.__ref__(self)
            return self.recorder


class Segment(PythonHocObject, connectable):
    def __init__(self, interpreter, ptr, section, **kwargs):
        PythonHocObject.__init__(self, interpreter, ptr, **kwargs)
        connectable.__init__(self)
        self.section = section

    def __netcon__(self):
        return self.__neuron__()._ref_v

    def __record__(self):
        return self.__neuron__()._ref_v


class PointProcess(PythonHocObject, connectable):
    """
    Wrapper for all point processes (membrane and synapse mechanisms).
    """

    def __init__(self, *args, **kwargs):
        PythonHocObject.__init__(self, *args, **kwargs)
        connectable.__init__(self)

    def stimulate(self, pattern=None, weight=0.04, delay=0.0, **kwargs):
        from . import connection

        if pattern is None:
            # No specific pattern given, create NetStim
            stimulus = self._interpreter.NetStim()
            for kw, value in kwargs.items():
                setattr(stimulus.__neuron__(), kw, value)
        else:
            # Specific pattern required, create VecStim
            stimulus = self._interpreter.VecStim(pattern=pattern)
        self._interpreter.NetCon(stimulus, self, weight=weight, delay=delay)
        return stimulus


def _get_obj_registration_queue():
    return _registration_queue
