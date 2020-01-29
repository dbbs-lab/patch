from contextlib import contextmanager
import os, sys


def transform(obj):
    """
    Transforms an object to its NEURON representation, if the __neuron__ magic
    method is present.
  """
    if hasattr(obj, "__neuron__"):
        return obj.__neuron__()
    return obj


def transform_netcon(obj):
    if hasattr(obj, "__netcon__"):
        return obj.__netcon__()
    return transform(obj)


def transform_record(obj):
    if hasattr(obj, "__record__"):
        return obj.__record__()
    return transform(obj)


def _is_sequence(obj):
    t = type(obj)
    return hasattr(t, "__len__") and hasattr(t, "__getitem__")
