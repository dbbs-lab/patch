from contextlib import contextmanager
from .exceptions import *
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


def transform_arc(obj, *args, **kwargs):
    """
        Get an arclength object on a NEURON object. Calls the __arc__ magic method
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
    if not hasattr(obj, "_connections"):
        raise NotConnectableError(
            label + " "
            if label is not None
            else ""
            + str(obj)
            + " is not connectable. It lacks attribute _connections required to form NetCons."
        )


def is_section(obj):
    return transform(obj).__class__.__name__ == "Section"
