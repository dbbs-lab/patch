# noinspection PyUnresolvedReferences, PyPackageRequirements
# Import mpi4py before importing patch during the tests.
import gc
import unittest

import mpi4py.MPI


class NeuronTestCase(unittest.TestCase):
    def tearDown(self):
        gc.collect()
