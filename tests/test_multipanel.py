
"""Tests for `spiffyplots` package."""


import unittest
import spiffyplots. multipanel as mp

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

class TestMutiPanel(unittest.TestCase):
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


class Test_get_letters(unittest.TestCase):

    def test_lowercase(self):
        """Test _get_letters."""
        out = mp._get_letters(case='lowercase')
        self.assertEqual(out[2], 'c')
        self.assertEqual(out[-1], 'z')


    def test_uppercase(self):
        """Test _get_letters."""
        out = mp._get_letters(case='uppercase')
        self.assertEqual(out[2], 'C')
        self.assertEqual(out[-1], 'Z')

    def test_default(self):
        """Test _get_letters."""
        out = mp._get_letters()
        self.assertEqual(out[2], 'C')
        self.assertEqual(out[-1], 'Z')


class Test_decode_label_array(unittest.TestCase):

    def test_simple_array(self):
        NotImplemented

    def test_complex_array(self):
        NotImplemented


class Test_get_grid_location(unittest.TestCase):

    def setUp(self):
        """
        Setup example gridspec object
        """
        self.grid = matplotlib.gridspec.GridSpec(3,3)

    def test_ints(self):
        tuple = (0, 1)
        out = mp._get_grid_location(tuple, self.grid)

        self.assertEqual(out, self.grid[0, 1])

    def test_int_rowrange(self):
        tuple = (range(0, 2), 1)
        out = mp._get_grid_location(tuple, self.grid)

        self.assertEqual(out, self.grid[0:2, 1])

    def test_int_colrange(self):
        tuple = (1, range(0, 3))
        out = mp._get_grid_location(tuple, self.grid)

        self.assertEqual(out, self.grid[1, 0:3])

    def test_ranges(self):
        tuple = (range(0, 2), range(0, 3))
        out = mp._get_grid_location(tuple, self.grid)

        self.assertEqual(out, self.grid[0:2, 0:3])

    def test_lists(self):
        tuple = ([0, 1, 2], [0, 1])
        out = mp._get_grid_location(tuple, self.grid)

        self.assertEqual(out, self.grid[0:3, 0:2])


class Test_get_subplot_raster(unittest.TestCase):

    def setUp(self):
        """
        setup example grid and corresponding panel locations
        """
        self.grid = [2, 3, 1]
        self.locations = [(0, range(0, 3)),
                          (0, range(3, 6)),
                          (1, range(0, 2)),
                          (1, range(2, 4)),
                          (1, range(4, 6)),
                          (2, range(0, 6))]

    def test_raster(self):
        out_shape, out_loc, out_panels = mp._get_subplot_raster(self.grid)

        self.assertEqual(out_shape, (3, 6))
        self.assertEqual(out_loc, self.locations)
        self.assertEqual(out_panels, 6)


class Test_lcm_of_array(unittest.TestCase):

    def setUp(self):
        """
        Setup example arrays
        """
        self.numpy = np.array([1, 2, 3, 4, 5])
        self.list = [2, 3, 1]

    def test_numpy(self):
        out = mp._lcm_of_array(self.numpy)
        self.assertEqual(out, 60)

    def test_list(self):
        out = mp._lcm_of_array(self.list)
        self.assertEqual(out, 6)


class Test_find_max_tuple(unittest.TestCase):

    def setUp(self):
        self.int_tuples = [(4, 6),
                           (7, 3)]
        self.range_tuples = [(range(3), range(5)),
                             (range(3, 7), range(2, 5))]
        self.long_mixed = [(range(3), range(5)),
                           (10, 1),
                           (range(3, 7), range(2, 5)),
                           (range(4), 3)]

    def test_int_tuples(self):
        out = mp._find_max_tuple(self.int_tuples)
        self.assertEqual(out, (8, 7))

    def test_range_tuples(self):
        out = mp._find_max_tuple(self.range_tuples)
        self.assertEqual(out, (7, 5))

    def test_long_mixed(self):
        out = mp._find_max_tuple(self.long_mixed)
        self.assertEqual(out, (11, 5))
