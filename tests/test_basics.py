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

    def test_attributes(self):
        # Test Hoc attributes
        self.assertTrue(p.E - 2.7 < 0.2, 'Can\'t read attributes from HocInterpreter')
        p.celsius = 11.004
        self.assertEqual(p._PythonHocInterpreter__h.celsius, 11.004, 'Can\'t set attributes on HocInterpreter')
        # Test python hoc attributes
        p.something_else = 15.4
        self.assertEqual(p.__dict__['something_else'], 15.4, 'Can\'t set attributes on PythonHocInterpreter')
        # Test nonsense attributes
        self.assertRaises(AttributeError, lambda: p.doesnt_exist)
        # Test object attributes
        s = p.Section()
        s.nseg = 5
        self.assertEqual(s.__neuron__().nseg, 5, 'Couldn\'t set attributes on HocObject')
        s.nseggg = 55
        self.assertRaises(AttributeError, lambda: s.__neuron__().nseggg)
        self.assertEqual(s.__dict__['nseggg'], 55, 'Couldn\'t set attributes on PythonHocObject')

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
