from errr.tree import make_tree as _make_tree, exception as _e

_make_tree(globals(), PatchError=_e(
    NotConnectableError=_e(),
    NotConnectedError=_e(),
    TransformError=_e(),
    HocError=_e(
        HocConnectError=_e(),
        HocRecordError=_e(),
        HocSectionAccessError=_e()
    ),
    SimulationError=_e(),
    UninitializedError=_e(),
    ErrorHandlingError=_e(),
    ParallelError=_e(ParallelConnectError=_e(), BroadcastError=_e(),),
))
