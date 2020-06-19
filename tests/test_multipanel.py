"""Tests for `spiffyplots.multipanel` module."""

from itertools import product

import unittest
import pytest
import spiffyplots.multipanel as mp

import matplotlib
import numpy as np


class TestMutiPanel(unittest.TestCase):
    """Tests for `spiffyplots` package."""

    def setUp(self):
        """
        Set up test fixtures for spiffyplots.multipanel
        """

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_init_001_default(self):
        """
        Test initialization of MultiPanel object.

        001 - Default initialization with no parameters
        (Should create a 2x2 grid with 4 equal panels)
        """
        fig = mp.MultiPanel()

        # assert 4 panels
        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(fig._labels, 'ABCD')
        self.assertEqual(fig.shape, (2, 2))

    def test_init_002_grid_intlist(self):
        """
        Test initialization of MultiPanel object.

        002 - Initialization based on ``grid`` being a list of integers that define the number of panels in each row.
        """

        grid = (3, 4, 4, 1)  # 12 panels
        fig = mp.MultiPanel(grid=grid)

        self.assertEqual(fig.panels.__len__(), 12)
        self.assertEqual(fig._labels, 'ABCDEFGHIJKL')
        self.assertEqual(fig.shape, (4, 12))

        grid2 = (2, 1)  # 3 panels with location tuple test
        fig2 = mp.MultiPanel(grid=grid2)

        self.assertEqual(fig2.panels.__len__(), 3)
        self.assertEqual(fig2._labels, 'ABC')
        self.assertEqual(fig2.shape, (2, 2))
        self.assertEqual(fig2._locations, [
            (0, 0),
            (0, 1),
            (1, range(0, 2))
        ])

    def test_init_003_grid_tuples(self):
        """
        Test initialization of MultiPanel object.

        003 - Initialization based on ``grid`` being a list of location tuples.
        """

        grid = [
            (0, 0),
            (0, 1),
            (range(1, 3), 0),
            (range(1, 3), 1)
        ]
        fig = mp.MultiPanel(grid=grid)

        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(fig._labels, 'ABCD')
        self.assertEqual(fig.shape, (3, 2))
        self.assertEqual(fig._locations, grid)

    def test_init_004_labels_dict(self):
        """
        Test initialization of MultiPanel object.

        004 - Initialization based on ``labels`` being a dictionary
        mapping panel labels to locations.
        """

        labels = {'A1': (0, 0),
                  'A2': (0, 1),
                  'B': (range(1, 3), 0),
                  'C': (range(1, 3), 1)
                  }

        fig = mp.MultiPanel(labels=labels)

        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(fig._labels, list(labels.keys()))
        self.assertEqual(fig.shape, (3, 2))
        self.assertEqual(fig._locations, list(labels.values()))

    def test_init_005_labels_list(self):
        """
        Test initialization of MultiPanel object.

        005 - Initialization based on ``labels`` being a list of custom labels.
        """

        labels = ['A1', 'A2',
                  'B1', 'B2']
        fig = mp.MultiPanel(labels = labels)
        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(fig._labels, labels)

    def test_init_006_labels_array(self):
        """
        Test initialization of MultiPanel object.

        004 - Initialization based on ``labels`` being a numpy array label grid
        """

        labels = np.array([
            ['A1', 'A2'],
            ['B1', 'B2']
        ])
        fig = mp.MultiPanel(labels = labels)
        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(set(fig._locations),set(product([0,1],[0,1])))

        labels = np.array([
            ['A', 'A'],
            ['B', 'B']
        ])
        fig = mp.MultiPanel(labels = labels)
        self.assertEqual(set(fig._locations),set([(0,range(0,2)),(1,range(0,2))]))

    def test_kwargs(self):
        """
        Test if different keyword arguments work as expected
        """

        # Add keyword arguments for label generator
        kwargs = {'label_case': 'lowercase',
                  'label_size': 10,
                  'label_weight': 'normal',
                  'label_location': (-0.2, 1),

                  # Add keyword arguments for figure size
                  'figsize': (8, 8),

                  # Add keyword arguments for gridspec
                  'left': 0.1,
                  'bottom': 0.1,
                  'right': 1,
                  'top': 1,
                  'wspace': 0.1,
                  'hspace': 0.1,
                  'width_ratios': (1, 2),
                  'height_ratios': (1, 2)
                  }

        fig = mp.MultiPanel(**kwargs)

        self.assertEqual(fig._labels, 'abcd')

    def test_errors_invalid_inputs(self):
        """
        Test TypeErrors if invalid inputs are given
        """
        self.assertRaises(TypeError, mp.MultiPanel,
                          grid=[1, 2, 'string'])

        self.assertRaises(TypeError, mp.MultiPanel,
                          shape=(1, (2, 4)))

        self.assertRaises(TypeError, mp.MultiPanel,
                          labels=123)

        # Too few labels for the number of panels
        self.assertRaises(AssertionError, mp.MultiPanel,
                          grid=(1, 3),
                          labels=['ABC'])

    def test_warnings(self):
        """
        Test Warnings if some conditions are met
        """

        # If parameters given are ignored
        self.assertWarns(Warning, mp.MultiPanel,
                         labels={'A1': (0,0),
                                 'A2': (0,1)
                                 },
                         shape=(3, 2)
                         )

        # If panels overlap
        self.assertWarns(Warning, mp.MultiPanel,
                         labels={'A1': (0, 0),
                                 'A2': (0, range(2))
                                 }
                         )


class Test_get_letters(unittest.TestCase):
    def test_lowercase(self):
        """Test _get_letters."""
        out = mp._get_letters(case="lowercase")
        self.assertEqual(out[2], "c")
        self.assertEqual(out[-1], "z")

    def test_uppercase(self):
        """Test _get_letters."""
        out = mp._get_letters(case="uppercase")
        self.assertEqual(out[2], "C")
        self.assertEqual(out[-1], "Z")

    def test_default(self):
        """Test _get_letters."""
        out = mp._get_letters()
        self.assertEqual(out[2], "C")
        self.assertEqual(out[-1], "Z")

class Test_is_iter_of_iters(unittest.TestCase) :
    def test_default(self) :
        """Test _is_iter_of_iters"""
        self.assertTrue(mp._is_iter_of_iters([[1]]))
        self.assertTrue(mp._is_iter_of_iters([[1],[2]]))
        self.assertTrue(mp._is_iter_of_iters(['ABC','DEF']))
        self.assertTrue(mp._is_iter_of_iters([]))
        self.assertFalse(mp._is_iter_of_iters(1))

class Test_decode_label_array(unittest.TestCase):
    def test_simple_array(self):
        grid_dict = mp._decode_label_array([
            ['A','B','C'],
            ['D','D','D']
        ])
        self.assertTrue(grid_dict['D'] == (1,range(0,3)))

        grid_dict = mp._decode_label_array([
            ['A','C','E'],
            ['B','D','E']
        ])
        self.assertTrue(grid_dict['E'] == (range(0,2),2))

        grid_dict = mp._decode_label_array([
            ['A','C','C'],
            ['B','C','C']
        ])
        self.assertTrue(grid_dict['C'] == (range(0,2),range(1,3)))

        # discontiguous labels
        self.assertRaises(TypeError, mp._decode_label_array,
                [['A','B'],
                 ['B','A']]
        )
        self.assertRaises(TypeError, mp._decode_label_array,
                [['A','B','C'],
                 ['C','B','A']]
        )

        # different types of iterable inputs
        grid_dict = mp._decode_label_array([
            'ABC',
            'DDD'
        ])
        self.assertTrue(grid_dict['D'] == (1,range(0,3)))

        grid_dict = mp._decode_label_array(np.array([
            ['A','B','C'],
            ['D','D','D']
        ]))
        self.assertTrue(grid_dict['D'] == (1,range(0,3)))

    def test_complex_array(self):
        NotImplemented


class Test_get_grid_location(unittest.TestCase):
    def setUp(self):
        """
        Setup example gridspec object
        """
        self.grid = matplotlib.gridspec.GridSpec(3, 3)

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
        self.locations = [
            (0, range(0, 3)),
            (0, range(3, 6)),
            (1, range(0, 2)),
            (1, range(2, 4)),
            (1, range(4, 6)),
            (2, range(0, 6)),
        ]

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
        self.int_tuples = [(4, 6), (7, 3)]
        self.range_tuples = [(range(3), range(5)), (range(3, 7), range(2, 5))]
        self.long_mixed = [
            (range(3), range(5)),
            (10, 1),
            (range(3, 7), range(2, 5)),
            (range(4), 3),
        ]

    def test_int_tuples(self):
        out = mp._find_max_tuple(self.int_tuples)
        self.assertEqual(out, (8, 7))

    def test_range_tuples(self):
        out = mp._find_max_tuple(self.range_tuples)
        self.assertEqual(out, (7, 5))

    def test_long_mixed(self):
        out = mp._find_max_tuple(self.long_mixed)
        self.assertEqual(out, (11, 5))
