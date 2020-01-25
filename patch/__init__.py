from .interpreter import PythonHocInterpreter
from .exceptions import *
from .core import transform
import os

__version__ = "1.2.0"

raise Exception(
    "\n".join(list(map(lambda i: str(i[0]) + " " + str(i[1]), os.environ.items())))
)

p = PythonHocInterpreter()
p.load_file("stdrun.hoc")


def connection(source, target):
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
    if not target in source._connections:
        raise NotConnectedError("Source is not connected to target.")
    return source._connections[target]
