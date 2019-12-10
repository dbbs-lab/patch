import unittest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p

class TestInterplay(unittest.TestCase):
    '''
        Test whether mixing h and p together causes issues.
    '''

    def setUp(self):
        pass

    def test_section_connect(self):
        from neuron import h
        # Connect 2 Sections
        s = p.Section()
        s2 = p.Section()
        s.connect(s2)

        # Connect a Section to a neuron Section
        s = p.Section()
        nrn_s = h.Section()
        nrn_s.connect(s.__neuron__())

        # Connect a neuron section to a section
        s = p.Section()
        nrn_s = h.Section()
        s.connect(nrn_s)
