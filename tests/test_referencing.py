import unittest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from patch import p

class TestReferencing(unittest.TestCase):
    '''
        Test whether references to other objects are created and removed at the
        proper moments.
    '''

    def setUp(self):
        pass

    def test_section_ref(self):
        '''
            Test whether connected sections keep eachother alive
        '''
        from neuron import h
        # Test whether NEURON is still broken.
        s1 = h.Section()
        def closure():
            s2 = h.Section()
            s2.connect(s1)
        closure()
        self.assertEqual(0, len(s1.children()), 'NEURON has seen the light and created strong references.')

        # Test whether we solve the weak referencing automatically

        s3 = p.Section()
        def patched_closure():
            s4 = p.Section()
            s4.connect(s3)
        patched_closure()
        self.assertEqual(1, len(s3.children()), 'Referencing failure, child section garbage collected.')
