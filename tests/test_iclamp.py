import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import patch
from patch import p
from patch.exceptions import *


class TestClamps(unittest.TestCase):
    """
        Test the current and voltage clamp mechanisms
    """

    def setUp(self):
        pass

    @unittest.expectedFailure
    def test_iclamp(self):
        s0 = p.Section()
        s0.record()
        s1 = p.Section()
        s1.record()
        s2 = p.Section()
        s2.record()
        s3 = p.Section()
        s3.record()
        s4 = p.Section()
        s4.record()
        p.time

        s1.iclamp(amplitude=10, delay=5)
        c = p.IClamp(sec=s2)
        c.amp = 10
        c.dur = 10
        c2 = s3.iclamp(amplitude=10)
        s4.iclamp(amplitude=[-10 for _ in range(int(10 / p.dt))])

        p.finitialize()
        p.continuerun(10)

        self.assertGreater(
            max(s1.recordings[0.5]),
            max(s0.recordings[0.5]),
            "No injected current detected",
        )
        self.assertGreater(
            max(s2.recordings[0.5]),
            max(s0.recordings[0.5]),
            "No injected current detected",
        )
        self.assertGreater(
            max(s3.recordings[0.5]),
            max(s0.recordings[0.5]),
            "No injected current detected",
        )
        self.assertGreater(
            max(s3.recordings[0.5]),
            max(s1.recordings[0.5]),
            "Half of injected charge not smaller than full charge",
        )
        self.assertGreater(
            max(s0.recordings[0.5]),
            max(s4.recordings[0.5]),
            "No negative injected current detected",
        )

        # from plotly import graph_objs as go
        # go.Figure(
        #     [
        #         go.Scatter(x=list(p.time), y=list(s.recordings[0.5]), name="s" + str(i + 1))
        #         for i, s in enumerate([s1,s2,s3,s4])
        #     ]
        # ).show()
