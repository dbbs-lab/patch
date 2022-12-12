import mpi4py.MPI
import unittest, _shared
from patch import p, connection
from patch.exceptions import BroadcastError, ParallelConnectError


@unittest.skipIf(
    p.parallel.nhost() != 1, "Single host tests should run only on 1 MPI node."
)
class TestSingleHostParallel(_shared.NeuronTestCase):
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
        p.ParallelCon(s, 202020)
        p.pop_section()
        syn = p.Section().synapse(p.ExpSyn)
        p.ParallelCon(1, syn, 5, 1)
        with self.assertRaises(ParallelConnectError):
            p.ParallelCon(None, None)

    def test_parallel_con_props(self):
        s = p.Section()
        gid = 1
        pc = p.ParallelCon(s, 202021, delay=5, weight=3)
        self.assertEqual(5, pc.delay, "Delay not set")
        self.assertEqual(3, pc.weight[0], "Weight not set")

    def test_parallel_context(self):
        pc1 = p.ParallelContext()
        pc2 = p.parallel
        self.assertEqual(pc1.nhost(), pc2.nhost(), "nhost mismatch")

    def test_single_bcast(self):
        arr = p.parallel.broadcast([1, 2, 3])
        self.assertEqual([1, 2, 3], arr, "single node broadcast failed")
        v = p.parallel.broadcast(p.Vector([1, 2, 3]))
        self.assertEqual([1, 2, 3], list(v), "single node vector broadcast failed")
        with self.assertRaises(BroadcastError):
            p.parallel.broadcast(p.NetStim())


@unittest.skipIf(
    p.parallel.nhost() == 1, "Cannot test parallel networks on a single MPI node."
)
class TestParallelNetworks(_shared.NeuronTestCase):
    """
    Test true functioning of parallel networks on multiple MPI nodes.
    """

    def test_parallel_prop(self):
        self.assertEqual(p.parallel, p.ParallelContext(), "PC should be a singleton")

    def test_parallel_con(self):
        pc = p.parallel
        if pc.id():
            section = p.Section()
            section.synapse(
                p.ExpSyn,
            )

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
        self.assertRaises(BroadcastError, p.parallel.broadcast, p.NetStim())
        self.assertRaises(BroadcastError, p.parallel.broadcast, p.Section())
