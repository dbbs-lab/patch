import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p
from patch.exceptions import *


class TestNetworks(unittest.TestCase):
    """
        Test network use cases such as PointProcesses, NetCon, NetStim, VecStim, ...
    """

    def test_stimulate(self):
        s = p.Section()
        se = p.PointProcess(p.ExpSyn, s)
        ns = se.stimulate()
        vs = se.stimulate(pattern=[1, 2, 3])
