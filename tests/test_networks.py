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
