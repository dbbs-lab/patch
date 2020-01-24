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
