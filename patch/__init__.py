from .exceptions import NotConnectableError, NotConnectedError
from .interpreter import PythonHocInterpreter
from .core import (
    transform,
    transform_arc,
    transform_netcon,
    transform_record,
    is_point_process,
    is_density_mechanism,
    is_section,
    is_segment,
    is_nrn_scalar,
)

try:
    from functools import cached_property, cache
except ImportError:  # pragma: nocover
    import functools

    def cached_property(f):
        return property(functools.lru_cache()(f))

    functools.cache = functools.lru_cache()
    functools.cached_property = cached_property

__version__ = "4.0.0a4"
p: "PythonHocInterpreter"
h: "PythonHocInterpreter"


def __getattr__(attr):
    if attr == "p" or attr == "h":
        return _get_interpreter()
    else:
        raise AttributeError(f"module {__name__} has no attribute {attr}.")


@cache
def _get_interpreter():
    p = PythonHocInterpreter()
    PythonHocInterpreter._process_registration_queue()
    return p


def connection(source, target, strict=True):
    if not hasattr(source, "_connections"):
        raise NotConnectableError(
            f"Source {source} is not connectable. It lacks attribute _connections "
            "required to form NetCons."
        )
    if not hasattr(target, "_connections"):
        raise NotConnectableError(
            f"Target {target} is not connectable. It lacks attribute _connections "
            "required to form NetCons."
        )
    reverse = source in target._connections
    if target not in source._connections:
        if reverse and not strict:
            return target._connections[source]
        raise NotConnectedError("Source is not connected to target.")
    return source._connections[target]
