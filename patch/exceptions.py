class PatchError(Exception):
    pass


class NotConnectableError(PatchError):
    pass


class NotConnectedError(PatchError):
    pass


class TransformError(PatchError):
    pass


class HocError(PatchError):
    pass


class HocConnectError(HocError):
    pass


class HocSectionAccessError(HocError):
    pass


class SimulationError(PatchError):
    pass


class UninitializedError(SimulationError):
    pass


class ErrorHandlingError(PatchError):
    pass


class ParallelError(PatchError):
    pass


class ParallelConnectError(PatchError):
    pass


class BroadcastError(ParallelError):
    pass
