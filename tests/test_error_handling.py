import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p
from neuron import h
from patch.exceptions import *
from patch.error_handler import *


class TestErrorHandling(unittest.TestCase):
    """
        Test whether the error handling system functions.
    """

    def test_hoc_handler(self):
        def test():
            with catch_hoc_error():
                v = p.Vector()
                v.__neuron__().record(p.Section())

        with self.assertRaises(HocError, msg="Did not capture `RuntimeError: hoc error`"):
            test()

    def test_handler_requirements(self):
        def test():
            with catch_hoc_error(CatchNetCon):
                h.NetCon(5, 12)

        with self.assertRaises(
            ErrorHandlingError, msg="Did not complain about missing handler requirements"
        ):
            test()

        class UndefinedRequirements(ErrorHandler):
            def catch(self, error, context):
                pass

        def test_undef():
            with catch_hoc_error(UndefinedRequirements):
                h.NetCon(5, 12)

        with self.assertRaises(
            ErrorHandlingError,
            msg="Did not complain about undefined handler requirements",
        ):
            test_undef()

    def test_netcon_errors(self):
        s = p.Section()
        t = p.Vector()
        with self.assertRaises(HocConnectError, msg="Didn't catch NetCon error"):
            p.NetCon(s, t)

    def test_suppress(self):
        with _suppress_nrn():
            print('ERROR! SUPPRESSION FAILED!')
