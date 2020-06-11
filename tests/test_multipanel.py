
"""Tests for `spiffyplots` package."""


import unittest
from spiffyplots.multipanel import *
from spiffyplots import MultiPanel
import matplotlib.pyplot as plt

class TestSpiffyplots(unittest.TestCase):
    """Tests for `spiffyplots` package."""

    def setUp(self):
        """
        Set up test fixtures for spiffyplots.multipanel
        """
        self.data = {
            'scatter-x': np.random.randn(200),
            'scatter-y': np.random.randn(200),
            'hist-gauss': np.random.randn(500),
            'hist-gamma': np.random.gamma(5, 8, 500),
            'heatmap': np.random.rand(100).reshape(10,10),
            'timeseries': np.array([np.sin(np.arange(0, 25, 0.1)) + np.random.randn(250) for _ in range(20)]),
            'timeseries-true': np.sin(np.arange(0, 25, 0.1)),
        }


    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_001_panel_default(self):
        """Test something."""
