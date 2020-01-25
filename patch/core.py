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


@contextmanager
def _suppress_stdout(stream=None):
    """
        Makes NEURON shut the fuck up.
    """
    close = False
    if stream is None:
        stream = open(os.devnull, "w")
        close = True
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stream
    sys.stderr = stream
    try:
        yield
    finally:
        if close:
            stream.close()
        sys.stdout = old_stdout
        sys.stderr = old_stderr
