import unittest, sys, os, gc


class NeuronTestCase(unittest.TestCase):
    def tearDown(self):
        gc.collect()
