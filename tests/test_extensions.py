import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p
from patch.exceptions import *


class TestExtensions(unittest.TestCase):
    """
        Test whether the extension system functions.
    """

    def test_vecstim(self):
        vc = p.VecStim(pattern=[1, 2, 3])
