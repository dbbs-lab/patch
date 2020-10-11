from .core import transform, transform_record, _is_sequence
from .error_handler import catch_hoc_error, CatchRecord


class PythonHocObject:
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
        except TypeError as _:
            raise

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
        except ValueError as _:
            return False


class connectable:
    def __init__(self):
        # Prepare a dictionary that lists which other NEURON parts this is connected to
        self._connections = {}


class Section(PythonHocObject, connectable):
    def __init__(self, *args, **kwargs):
        PythonHocObject.__init__(self, *args, **kwargs)
        connectable.__init__(self)

    def connect(self, target, *args, **kwargs):
        nrn_target = transform(target)
        self.__neuron__().connect(nrn_target, *args, **kwargs)
        if hasattr(target, "__ref__"):
            target.__ref__(self)
        self.__ref__(target)

    def __arc__(self):
        return 0.5

    def __netcon__(self):
        return self(self.__arc__()).__netcon__()

    def __record__(self):
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
        # Catch nrn.Section return value, always seems to be self.
        # So if Neuron doesn't raise an error, return self.
        # Probably for method chaining?
        self.__neuron__().insert(*args, **kwargs)
        return self

    def connect_points(self, target, x=None, **kwargs):
        if x is None:
            x = self.__arc__()
        segment = self(x)
        self.push()
        nc = self._interpreter.NetCon(segment, target, **kwargs)
        self._interpreter.pop_section()
        return nc

    def set_dimensions(self, length, diameter):
        self.L = length
        self.diam = diameter

    def set_segments(self, segments):
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

    def wholetree(self):
        return [Section(self._interpreter, s) for s in self.__neuron__().wholetree()]

    def record(self, x=None):
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

    def synapse(self, factory, store=False, *args, **kwargs):
        synapse = self._interpreter.PointProcess(factory, self, *args, **kwargs)
        if store:
            if not hasattr(self, "synapses"):
                self.synapses = []
            self.synapses.append(synapse)
        return synapse

    def iclamp(self, x=0.5, delay=0, duration=100, amplitude=0):
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

    def push(self):
        transform(self).push()

        class SectionStackContextManager:
            def __enter__(this):
                pass

            def __exit__(*args):
                self.pop()

        return SectionStackContextManager()

    def pop(self):
        if self == self._interpreter.cas():
            self._interpreter.pop_section()
        else:
            raise RuntimeError(
                "Cannot pop this section as it is not on top of the section stack"
            )


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


class IClamp(PythonHocObject):
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
        Wrapper for all point processes (membrane and synapse mechanisms). Use
        ``PythonHocInterpreter.PointProcess`` to construct these objects.
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
