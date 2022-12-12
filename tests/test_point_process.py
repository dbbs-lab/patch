from patch import p
import unittest
import _shared


@unittest.skipIf(p.parallel.nhost() != 1, "Single-node simulation test.")
class TestPointProcess(_shared.NeuronTestCase):
    def _setup_synapse_patch(self):
        section = p.Section()
        syn = section.synapse(p.ExpSyn, attributes={"tau": 2})
        syn.stimulate(start=0, number=5, interval=10, delay=1, weight=0.04)

        return p.time, section.record()

    def _setup_synapse_neuron(self):
        from neuron import h

        my_s = h.Section()
        stim = h.NetStim()
        syn_ = h.ExpSyn(my_s(0.5))
        stim.number = 5
        stim.start = 0
        stim.interval = 10
        ncstim = h.NetCon(stim, syn_)
        ncstim.delay = 1
        syn_.tau = 2
        soma_v = h.Vector().record(my_s(0.5)._ref_v)
        t = h.Vector().record(h._ref_t)
        ncstim.weight[0] = 0.04  # NetCon weight is a vector.

        self._store = [my_s, stim, syn_, ncstim]
        return t, soma_v

    def test_synapse(self):
        tp, vp = self._setup_synapse_patch()
        tn, vn = self._setup_synapse_neuron()

        p.tstop = 30
        p.finitialize()
        p.run(30)
        self.assertEqual([*tp], [*tn], "Time vector differences in synaptic comparison")
        self.assertEqual([*vp], [*vn], "Outcome differences in synaptic comparison")
