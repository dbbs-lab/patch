from contextlib import contextmanager
from .exceptions import *
import os, sys


def transform(obj):
    """
    Transform an object to its NEURON representation, if the ``__neuron__`` magic
    method is present.
    """
    if hasattr(obj, "__neuron__"):
        return obj.__neuron__()
    return obj


def transform_netcon(obj):
    """
    Transform an object into the pointer that should be connected, if the ``__netcon__``
    magic method is present.
    """
    if hasattr(obj, "__netcon__"):
        return obj.__netcon__()
    return transform(obj)


def transform_record(obj):
    """
    Transform an object into the pointer that should be recorded, if the ``__record__``
    magic method is present.
    """
    if hasattr(obj, "__record__"):
        return obj.__record__()
    return transform(obj)


def transform_arc(obj, *args, **kwargs):
    """
    Get an arclength object on a NEURON object. Calls the ``__arc__`` magic method
    on the callable object if present, otherwise returns the transformed object.
    """
    if hasattr(obj, "__arc__"):
        return transform(obj(obj.__arc__(*args, **kwargs)))
    else:
        return transform(obj)


def _is_sequence(obj):
    t = type(obj)
    return hasattr(t, "__len__") and hasattr(t, "__getitem__")


def assert_connectable(obj, label=None):
    """
    Assert whether an object could be used as a :class:`~.objects.Connectable`.

    :param label: Optional label to display to describe the object if the assertion fails.
    :type label: str
    """
    if not hasattr(obj, "_connections"):
        raise NotConnectableError(
            (label if label is not None else str(obj))
            + " is not connectable."
            + "It lacks attribute `_connections` required to form NetCons."
        )


def is_section(obj):
    """
    Check if the class name of an object is ``Section``.
    """
    return type(transform(obj)).__name__ == "Section"


def is_point_process(name):
    """
    Check if a PointProcess with ``name`` exists on the ``HocInterpreter``.

    :param name: Name of the PointProcess to look for. Needs to be a known attribute of
      ``neuron.h``.
    :type name: str
    :returns: Whether an attribute with ``name`` exists on ``neuron.h`` and has functions
      matching those expected to be present on a ``PointProcess``.
    :rtype: bool
    """
    from neuron import h

    try:
        d = dir(getattr(h, name))
    except Exception:
        return False
    return all(k in d for k in ["get_loc", "has_loc", "loc", "get_segment"])
