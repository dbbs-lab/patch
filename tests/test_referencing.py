import unittest, sys, os, _shared

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from patch import p


class TestReferencing(_shared.NeuronTestCase):
    """
        Test whether references to other objects are created and removed at the
        proper moments.
    """

    def setUp(self):
        pass

    def test_ref_deref(self):
        s = p.Section()
        s2 = p.Section()
        s.__ref__(s2)
        self.assertIn(s2, s._references, "Referencing failure.")
        self.assertEqual(
            len(s._references), 1, "Referencing failure: added object twice."
        )
        self.assertTrue(s.__deref__(s2), "Dereferencing failure: could not find object.")
        self.assertFalse(
            s.__deref__(s2), "Dereferencing failure: found reference object twice."
        )

    def test_section_ref(self):
        """
            Test whether connected sections keep eachother alive
        """
        from neuron import h

        # Test whether NEURON is still broken.
        s1 = h.Section()

        def closure():
            s2 = h.Section()
            s2.connect(s1)

        closure()
        self.assertEqual(
            0,
            len(s1.children()),
            "NEURON has seen the light and created strong references.",
        )

        # Test whether we solve the weak referencing automatically

        s3 = p.Section()

        def patched_closure():
            s4 = p.Section()
            s4.connect(s3)

        patched_closure()
        self.assertEqual(
            1, len(s3.children()), "Referencing failure, child section garbage collected."
        )

    # TODO: Test Synapses, point processes, NetStim & NetCon
