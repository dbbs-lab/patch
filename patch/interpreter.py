from .objects import PythonHocObject

class PythonHocInterpreter:
  def __init__(self):
    from neuron import h
    self.__h = h
    # Wrapping should occur around all calls to functions that share a name with
    # child classes of the PythonHocObject like h.Section, h.NetStim, h.NetCon
    self.__object_classes = PythonHocObject.__subclasses__().copy()
    self.__requires_wrapping = [cls.__name__ for cls in self.__object_classes]

  def __getattr__(self, attr_name):
    # Get the missing attribute from h, if it requires wrapping return a wrapped
    # object instead.
    attr = getattr(self.__h, attr_name)
    if self.__requires_wrapping:
      return self.wrap(attr)
    else:
      return attr

  def wrap(self, factory):
    def wrapper(*args, **kwargs):
      obj = factory(*args, **kwargs)
      return PythonHocObject(self.__h, obj)
    return wrapper

  def NetCon(self, source, target, *args, **kwargs):
    connection = NetCon(self, self.__h.NetCon(nrn_source, nrn_target, *args, **kwargs))
    connection.__ref__(self)
    connection.__ref__(target)
    source._connections[target] = connection
    target._connections[source] = connection
