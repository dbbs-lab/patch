from .core import transform

class PythonHocObject:
  def __init__(self, interpreter, ptr):
    # Initialize ourselves with a reference to our own "pointer"
    # and prepare a list for other references.
    self.__dict__['__ptr'] = ptr
    self.__references = []
    self.__interpreter = interpreter

  def __getattr__(self, attr):
      # Return underlying attributes that aren't explicitly set on the wrapper
      return getattr(self.__dict__['__ptr'], attr)

  def __setattr__(self, attr, value):
    # Set attributes on the underlying pointer, and set on self if they don't
    # exist on the underlying pointer. This allows you to set arbitrary values
    # on the NEURON objects as you would be able to with a real Pythonic object.
    try:
        setattr(self.__ptr, attr, value)
    except AttributeError as _:
        self.__dict__[attr] = value

  def __call__(self, *args, **kwargs):
    # Relay calls to self to the underlying pointer
    return self.__ptr(*args, **kwargs)

  def __neuron__(self):
    # Magic method that allows duck typing of this object as something that
    # needs to be represented differently when passed to NEURON.
    return self.__dict__['__ptr']

  def __ref__(self, obj):
    # Magic method that will store a strong reference to another object.
    self.__references.append(transform(obj))

  def __deref__(self, obj):
    # Magic method that will remove a strong reference to another object.
    try:
      self.__references.remove(transform(obj))
      return True
    except ValueError as _:
      return False


class Section(PythonHocObject):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Prepare a dictionary that lists which other NEURON parts this
    self._connections = {}


class NetStim(PythonHocObject):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Prepare a dictionary that lists which other NEURON parts this
    self._connections = {}


class NetCon(PythonHocObject):
  pass
