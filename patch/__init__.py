from .interpreter import PythonHocInterpreter
from .exceptions import *
from .core import transform
import os, pkg_resources

__version__ = "1.3.2"

if not os.getenv("READTHEDOCS"):
    p = PythonHocInterpreter()


def connection(source, target, strict=True):
    if not hasattr(source, "_connections"):
        raise NotConnectableError(
            "Source "
            + str(source)
            + " is not connectable. It lacks attribute _connections required to form NetCons."
        )
    if not hasattr(target, "_connections"):
        raise NotConnectableError(
            "Target "
            + str(target)
            + " is not connectable. It lacks attribute _connections required to form NetCons."
        )
    reverse = source in target._connections
    if not target in source._connections:
        if reverse and not strict:
            return target._connections[source]
        raise NotConnectedError("Source is not connected to target.")
    return source._connections[target]


def get_data_file(*dirs):  # pragma: nocover
    """
        Retrieve a file from the data directory that is installed together with the
        package.
    """
    path = os.path.join("data", *dirs)
    if not pkg_resources.resource_exists(__package__, path):
        raise FileNotFoundError("Data file '{}' not found".format(path))
    return pkg_resources.resource_filename(__package__, path)
