def transform(obj):
  '''
    Transforms an object to its NEURON representation, if the __neuron__ magic
    method is present.
  '''
  if hasattr(obj, "__neuron__"):
    return obj.__neuron__()
  return obj

def is_sequence(obj):
    t = type(obj)
    return hasattr(t, '__len__') and hasattr(t, '__getitem__')
