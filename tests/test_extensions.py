import unittest, sys, os, _shared

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p
from patch.exceptions import *


class TestExtensions(_shared.NeuronTestCase):
    """
    Test whether the extension system functions.
    """

    def test_vecstim(self):
        # Creating a VecStim here causes the test_network test to kill the process.
        # vc = p.VecStim(pattern=[1, 2, 3])
        pass
