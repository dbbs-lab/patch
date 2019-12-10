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
