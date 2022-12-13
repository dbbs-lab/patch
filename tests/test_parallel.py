import unittest
import _shared
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


class TestParallelPointProcess(_shared.NeuronTestCase):
    def _setup_synapse_parallel(self):
        section = p.Section()
        syn = section.synapse(p.ExpSyn, attributes={"tau": 2})
        if not p.parallel.id():
            syn.stimulate(start=0, number=5, interval=10, delay=1, weight=0.04)
            p.ParallelCon(section, 3030, threshold=-52, delay=1)
        else:
            p.ParallelCon(3030, syn, weight=0.04)
        return p.time, section.record()

    def _setup_synapse_patch(self):
        section = p.Section()
        syn = section.synapse(p.ExpSyn, attributes={"tau": 2})
        syn.stimulate(start=0, number=5, interval=10, delay=1, weight=0.04)
        section2 = p.Section()
        syn_r = section2.synapse(p.ExpSyn, attributes={"tau": 2})
        section.connect_synapse(syn_r, delay=1, weight=0.04, threshold=-52)

        return p.time, section2.record()

    # noinspection DuplicatedCode
    def _setup_synapse_neuron(self):
        from neuron import h

        pc = h.ParallelContext()
        if not pc.id():
            my_s = h.Section()
            syn_ = h.ExpSyn(my_s(0.5))
            syn_.tau = 2
            stim = h.NetStim()
            stim.number = 5
            stim.start = 0
            stim.interval = 10
            ncstim = h.NetCon(stim, syn_)
            ncstim.weight[0] = 0.04
            ncstim.delay = 1
            nc_emit = h.NetCon(my_s(0.5)._ref_v, None, sec=my_s)
            nc_emit.threshold = -52
            nc_emit.delay = 1
            pc.set_gid2node(3031, pc.id())
            pc.cell(3031, nc_emit)
            pc.outputcell(3031)
            self._store = [my_s, stim, syn_, ncstim, nc_emit]
        else:
            my_s = h.Section()
            syn_ = h.ExpSyn(my_s(0.5))
            syn_.tau = 2
            nc_recv = pc.gid_connect(3031, syn_)
            nc_recv.weight[0] = 0.04
            self._store = [my_s, syn_, nc_recv]

        return h.Vector().record(h._ref_t), h.Vector().record(my_s(0.5)._ref_v)

    def test_synapse(self):
        tpp, vpp = self._setup_synapse_parallel()
        tps, vps = self._setup_synapse_patch()
        tn, vn = self._setup_synapse_neuron()

        p.finitialize()
        p.parallel.psolve(100)

        if p.parallel.id():
            self.assertNotEqual(min(*vpp), max(*vpp), "No Vm diff observed")
            self.assertEqual(
                [*tpp], [*tn], "Time vector differences in synaptic comparison"
            )
            self.assertEqual([*vpp], [*vn], "Outcome differences in synaptic comparison")
            self.assertEqual(
                [*tpp], [*tps], "Time vector differences in serial/parallel comparison"
            )
            self.assertEqual(
                [*vpp], [*vps], "Outcome differences in serial/parallel comparison"
            )
