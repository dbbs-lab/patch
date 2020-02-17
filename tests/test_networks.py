import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p, connection
from patch.objects import NetCon
from patch.exceptions import *


class TestNetworks(unittest.TestCase):
    """
        Test network use cases such as PointProcesses, NetCon, NetStim, VecStim, ...
    """

    def test_connection_helper(self):
        s = p.Section()
        pp = p.PointProcess(p.ExpSyn, s)
        stim = pp.stimulate()
        self.assertEqual(
            NetCon,
            type(connection(stim, pp)),
            "connection helper did not return the expected NetCon",
        )
        self.assertRaises(NotConnectedError, connection, s, s)
        self.assertRaises(NotConnectableError, connection, p.Vector(), s)
        self.assertRaises(NotConnectableError, connection, s, p.Vector())

    def test_stimulate(self):
        from random import random

        s1 = p.Section()
        s2 = p.Section()
        s3 = p.Section()
        se = p.PointProcess(p.ExpSyn, s1)
        se2 = p.PointProcess(p.ExpSyn, s2)
        se3 = p.PointProcess(p.ExpSyn, s3)
        ns = se.stimulate(start=1, number=3, interval=1)
        vs = se2.stimulate(pattern=[1, 2, 3])
        vs2 = se3.stimulate(pattern=[random() * 2, random() + 2, random() * 2 + 3])
        rs1 = s1.record()
        rs2 = s2.record()
        rs3 = s3.record()
        t = p.time

        p.finitialize()
        p.continuerun(10)
        self.assertGreater(
            max(list(rs1)), min(list(rs1)), "Flatline where stimulation was expected."
        )
        for ns_y, vs_y in zip(rs1, rs2):
            self.assertAlmostEqual(ns_y, vs_y, delta=1e-6)
        equal = True
        for vs_y, vs2_y in zip(rs2, rs3):
            equal = abs(vs2_y - vs_y) < 1e-6
            if not equal:
                break
        equal = False
        self.assertFalse(equal, "Random and periodic VecStim yielded identical results.")
