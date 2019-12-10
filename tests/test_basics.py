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
