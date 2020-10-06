from mpi4py import MPI
from .exceptions import *
import os, sys, pkg_resources, types
from .core import transform, transform_arc, transform_netcon, transform_record


_p = None


class PythonHocModule(types.ModuleType):
    from .interpreter import PythonHocInterpreter
    from . import objects, interpreter, exceptions, error_handler, core

    transform = staticmethod(transform)
    transform_netcon = staticmethod(transform_netcon)
    transform_record = staticmethod(transform_record)
    transform_arc = staticmethod(transform_arc)

    __version__ = "2.2.0"

    @property
    def p(self):
        global _p
        if _p is None:
            _p = PythonHocModule.PythonHocInterpreter()
        return _p

    def connection(self, source, target, strict=True):
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

    def get_data_file(self, *dirs):  # pragma: nocover
        """
            Retrieve a file from the data directory that is installed together with the
            package.
        """
        path = os.path.join("data", *dirs)
        if not pkg_resources.resource_exists(__package__, path):
            raise FileNotFoundError("Data file '{}' not found".format(path))
        return pkg_resources.resource_filename(__package__, path)

    # Define all for `from patch import *` statements
    __all__ = list(set(vars().keys()) - {"__module__", "__qualname__"})


# Register a PythonHocModule instance as this module
sys.modules[__name__] = PythonHocModule(__name__)
