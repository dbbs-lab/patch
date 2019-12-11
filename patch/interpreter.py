from .objects import PythonHocObject, NetCon, PointProcess
from .core import transform
from .exceptions import *

class PythonHocInterpreter:
  def __init__(self):
    from neuron import h
    self.__dict__["_PythonHocInterpreter__h"] = h
    # Wrapping should occur around all calls to functions that share a name with
    # child classes of the PythonHocObject like h.Section, h.NetStim, h.NetCon
    self.__object_classes = PythonHocObject.__subclasses__().copy()
    self.__requires_wrapping = [cls.__name__ for cls in self.__object_classes]

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
      return cls(self.__h, obj)
    return wrapper

  def NetCon(self, source, target, *args, **kwargs):
    nrn_source = transform(source)
    nrn_target = transform(target)
    connection = NetCon(self, self.__h.NetCon(nrn_source, nrn_target, *args, **kwargs))
    connection.__ref__(self)
    connection.__ref__(target)
    if not hasattr(source, "_connections"):
      raise NotConnectableError('Source ' + str(source) + ' is not connectable. It lacks attribute _connections required to form NetCons.')
    if not hasattr(target, "_connections"):
      raise NotConnectableError('Target ' + str(target) + ' is not connectable. It lacks attribute _connections required to form NetCons.')
    source._connections[target] = connection
    target._connections[source] = connection
    return connection

  def PointProcess(self, factory, *args, **kwargs):
    point_process = factory(*args, **kwargs)
    return PointProcess(self, point_process)
