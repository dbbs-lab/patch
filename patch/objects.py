from .core import transform, transform_record, is_sequence

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

  def __netcon__(self):
    return self(0.5).__netcon__()

  def __call__(self, *args, **kwargs):
    v = super().__call__(*args, **kwargs)
    if type(v).__name__ != "Segment":  # pragma: no cover
      raise TypeError("Section call did not return a Segment.")
    return Segment(self._interpreter, v)

  def __iter__(self, *args, **kwargs):
    iter = super().__iter__(*args, **kwargs)
    for v in iter:
      if type(v).__name__ != "Segment":  # pragma: no cover
        raise TypeError("Section iteration did not return a Segment.")
      yield Segment(self._interpreter, v)

  def insert(self, *args, **kwargs):
    # Catch nrn.Section return value, always seems to be self.
    # So if Neuron doesn't raise an error, return self.
    # Probably for method chaining?
    self.__neuron__().insert(*args, **kwargs)
    return self

  def connect_points(self, target, x=0.5):
    segment = self(x)
    self.push()
    self._interpreter.NetCon(segment, target)
    self._interpreter.pop_section()

  def set_dimensions(self, length, diameter):
    self.L = length
    self.diam = diameter

  def set_segments(self, segments):
    self.nseg = segments

  def add_3d(self, points, diameters=None):
    '''
      Add a new 3D point to this section xyz data.

      :param points: A 2D array of xyz points.
      :param diameters: A scalar or array of diameters corresponding to the points. Default value is the section diameter.
      :type diameters: float or array
    '''
    if diameters is None:
        diameters = [self.diam for _ in range(len(points))]
    if not is_sequence(diameters):
        diameters = [diameter for _ in range(len(points))]
    self.__neuron__().push()
    for point, diameter in zip(points, diameters):
        self._interpreter.pt3dadd(*point, diameter)
    self._interpreter.pop_section()

  def wholetree(self):
    return [Section(self._interpreter, s) for s in self.__neuron__().wholetree()]

  def record(self, x=0.5):
    if not hasattr(self, "recordings"):
      self.recordings = {}
    if not x in self.recordings:
      recorder = self._interpreter.Vector()
      recorder.record(self(x))
      self.recordings[x] = recorder
      return recorder

class Vector(PythonHocObject):
  def record(self, target):
    nrn_target = transform_record(target)
    self.__neuron__().record(nrn_target)
    self.__ref__(target)

class NetStim(PythonHocObject, connectable):
  def __init__(self, *args, **kwargs):
    PythonHocObject.__init__(self, *args, **kwargs)
    connectable.__init__(self)


class NetCon(PythonHocObject):
  pass


class Segment(PythonHocObject, connectable):
  def __init__(self, *args, **kwargs):
    PythonHocObject.__init__(self, *args, **kwargs)
    connectable.__init__(self)

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

  def stimulate(self, **kwargs):
    stimulus = self._interpreter.NetStim()
    for kw, value in kwargs.items():
      setattr(stimulus.__neuron__(), kw, value)
    self._interpreter.NetCon(stimulus, self)
    return stimulus
