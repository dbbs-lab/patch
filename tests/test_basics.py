import unittest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p

class TestPatch(unittest.TestCase):
    '''
        Check Patch basics like object wrapping and the standard interface.
    '''

    def setUp(self):
        pass

    def test_wrapping(self):
        net_con = type(p.NetCon(p.NetStim(), p.NetStim()))
        net_stim = type(p.NetStim())
        section = type(p.Section())
        self.assertEqual(section, patch.objects.Section, 'Incorrect Section wrapping: ' + str(section))
        self.assertEqual(net_stim, patch.objects.NetStim, 'Incorrect NetStim wrapping: ' + str(net_stim))
        self.assertEqual(net_con, patch.objects.NetCon, 'Incorrect NetCon wrapping: ' + str(net_con))

    def test_transform(self):
        from patch.core import transform
        from neuron import h
        nrn_section1 = transform(p.Section())
        self.assertEqual("nrn", type(nrn_section1).__module__, 'Transform on a Patch object did not return a NEURON object.')
        self.assertIs(nrn_section1, transform(nrn_section1), 'Transform on a NEURON object did not return the object.')

    def test_section_call(self):
        s = p.Section()
        s.nseg = 5
        seg = s(0.5)
        self.assertEqual(patch.objects.Segment, type(seg), 'Section call did not return a Segment')

    def test_section_iter(self):
        s = p.Section()
        s.nseg = 5
        count = 0
        for seg in s:
            count += 1
            self.assertEqual(patch.objects.Segment, type(seg), 'Section iteration did not return a Segment')
        self.assertEqual(count, 5, 'Section iteration did not return `nseg` segments.')
        # Test that other HocObjects aren't iterable.
        self.assertRaises(TypeError, iter, p.NetStim())
