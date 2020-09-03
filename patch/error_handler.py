from contextlib import contextmanager
from .exceptions import *
import io, sys, os


@contextmanager
def _suppress_nrn(stream=None, close=False):
    """
        Makes NEURON shut the fuck up.
    """
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


@contextmanager
def catch_hoc_error(*args, **context):
    with io.StringIO() as error_stream:
        try:
            with _suppress_nrn(error_stream):
                yield
        except RuntimeError as e:
            error = error_stream.getvalue()
            try:
                for handler in args:
                    handler(error, context)
            except Exception as e:
                raise e from None
            # Uncaught HocError
            if str(e).find("hoc error") != -1:
                raise HocError(error) from None
            # Actual RuntimeError
            raise e from None  # pragma: nocover


class ErrorHandler:
    """

    """
    def __init__(self, error, context):
        if not hasattr(self.__class__, "required"):
            raise ErrorHandlingError(
                "Error context requirements missing for {}".format(
                    self.__class__.__name__
                )
            )
        for required_item in self.__class__.required:
            if required_item not in context:
                raise ErrorHandlingError(
                    "Required error context item '{}' for {} is missing".format(
                        required_item, self.__class__.__name__
                    )
                )
        self.__dict__.update(context)
        self.catch(error, context)

    def catch(self, error, context):
        raise ErrorHandlingError(
            "Catch method not implemented for {}".format(self.__class__.__name__)
        )


class CatchNetCon(ErrorHandler):
    required = ["nrn_source", "nrn_target"]

    def catch(self, error, context):
        if error.lower().find("must be a point process or nullobject") != -1:
            if error.find("arg 1") != -1:
                raise HocConnectError(
                    "Source is not a point process. Transformed type: '{}'".format(
                        type(self.nrn_source)
                    )
                )
            if error.find("arg 2") != -1:
                raise HocConnectError(
                    "Target is not a point process. Transformed type: '{}'".format(
                        type(self.nrn_target)
                    )
                )
        if error.find("interpreter stack type error") != -1:
            raise HocConnectError(
                "Incorrect types passed to NetCon. Source: {}, target: {}".format(
                    type(self.nrn_source), type(self.nrn_target)
                )
            )


class CatchSectionAccess(ErrorHandler):
    required = []

    def catch(self, error, context):
        if error.find("Section access unspecified") != -1:
            raise HocSectionAccessError("This operation requires a Section on the stack.")
