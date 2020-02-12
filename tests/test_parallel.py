import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p, connection
from patch.objects import NetCon
from patch.exceptions import *


class TestSingleHostParallel(unittest.TestCase):
    """
        Test parallel network approach functioning on a single MPI node.
    """

    def test_pc_singleton(self):
        pc = p.pc
        pc2 = p.pc
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


@unittest.skipIf(p.pc.nhost() == 1, "Cannot test parallel networks on a single MPI node.")
class TestParallelNetworks(unittest.TestCase):
    """
        Test true functioning of parallel networks on multiple MPI nodes.
    """

    def test_parallel_con(self):
        pass
