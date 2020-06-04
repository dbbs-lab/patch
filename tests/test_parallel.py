import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p, connection
from patch.objects import NetCon
from patch.exceptions import *


@unittest.skipIf(
    p.parallel.nhost() != 1, "Single host tests should run only on 1 MPI node."
)
class TestSingleHostParallel(unittest.TestCase):
    """
        Test parallel network approach functioning on a single MPI node.
    """

    def test_pc_singleton(self):
        pc = p.parallel
        pc2 = p.parallel
        self.assertEqual(pc, pc2)
        self.assertEqual(pc.id(), 0)

    def test_parallel_con(self):
        s = p.Section()
        gid = 1
        s.push()
        p.ParallelCon(s, 1)
        p.pop_section()
        syn = p.Section().synapse(p.ExpSyn)
        p.ParallelCon(1, syn)


@unittest.skipIf(
    p.parallel.nhost() == 1, "Cannot test parallel networks on a single MPI node."
)
class TestParallelNetworks(unittest.TestCase):
    """
        Test true functioning of parallel networks on multiple MPI nodes.
    """

    def test_parallel_con(self):
        pass

    def test_broadcasting(self):
        # Try sending a string
        x = p.parallel.broadcast("Arbitrary")
        self.assertEqual(
            x,
            "Arbitrary",
            msg="Arbitrary data mangled on node {}".format(p.parallel.id()),
        )

        class Local:
            pass

        self.assertRaises(BroadcastError, p.parallel.broadcast, Local())
        # Try sending from a different node
        if p.parallel.id() == 0:
            x = 5
        else:
            x = 12
        y = p.parallel.broadcast(x, root=1)
        self.assertEqual(y, 12, msg="Node specification ignored in broadcast.")
