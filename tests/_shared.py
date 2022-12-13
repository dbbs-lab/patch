# noinspection PyUnresolvedReferences, PyPackageRequirements
# Import mpi4py before importing patch during the tests.
import mpi4py.MPI
import gc
import unittest


class NeuronTestCase(unittest.TestCase):
    def tearDown(self):
        gc.collect()
