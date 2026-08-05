"""Tests for `spiffyplots.multipanel` module."""

import unittest
import warnings
from itertools import product
from pathlib import Path
from unittest.mock import patch

import matplotlib
import numpy as np

import spiffyplots.multipanel as mp


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
        self.assertEqual(fig._labels, ["a", "b", "c", "d"])
        self.assertIs(fig.panels.a, fig.panels[0])
        self.assertEqual(fig.shape, (2, 2))

    def test_init_002_grid_intlist(self):
        """
        Test initialization of MultiPanel object.

        002 - Initialization based on ``grid`` being a list of integers that define the number of panels in each row.
        """

        grid = (3, 4, 4, 1)  # 12 panels
        fig = mp.MultiPanel(grid=grid)

        self.assertEqual(fig.panels.__len__(), 12)
        self.assertEqual(fig._labels, list("abcdefghijkl"))
        self.assertEqual(fig.shape, (4, 12))

        grid2 = (2, 1)  # 3 panels with location tuple test
        fig2 = mp.MultiPanel(grid=grid2)

        self.assertEqual(fig2.panels.__len__(), 3)
        self.assertEqual(fig2._labels, ["a", "b", "c"])
        self.assertEqual(fig2.shape, (2, 2))
        self.assertEqual(fig2._locations, [(0, 0), (0, 1), (1, range(2))])

    def test_init_003_grid_tuples(self):
        """
        Test initialization of MultiPanel object.

        003 - Initialization based on ``grid`` being a list of location tuples.
        """

        grid = [(0, 0), (0, 1), (range(1, 3), 0), (range(1, 3), 1)]
        fig = mp.MultiPanel(grid=grid)

        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(fig._labels, ["a", "b", "c", "d"])
        self.assertEqual(fig.shape, (3, 2))
        self.assertEqual(fig._locations, grid)

    def test_init_grid_accepts_iterable_spans(self):
        for span in ([0, 1], np.arange(2)):
            with self.subTest(span=span):
                figure = mp.MultiPanel(grid=[(0, 0), (0, 1), (span, 2)])

                self.assertEqual(len(figure.panels), 3)
                figure.close()

    def test_init_grid_accepts_numpy_integer_coordinates(self):
        figure = mp.MultiPanel(grid=[(np.int64(0), np.int64(0))])

        self.assertEqual(len(figure.panels), 1)
        figure.close()

    def test_init_004_labels_dict(self):
        """
        Test initialization of MultiPanel object.

        004 - Initialization based on ``labels`` being a dictionary
        mapping panel labels to locations.
        """

        labels = {
            "A1": (0, 0),
            "A2": (0, 1),
            "B": (range(1, 3), 0),
            "C": (range(1, 3), 1),
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

        labels = ["A1", "A2", "B1", "B2"]
        fig = mp.MultiPanel(labels=labels)
        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(fig._labels, labels)

    def test_init_label_grid_accepts_nested_lists(self):
        figure = mp.MultiPanel(labels=[["A", "A"], ["B", "C"]])

        self.assertEqual(figure._labels, ["A", "B", "C"])
        self.assertEqual(figure.shape, (2, 2))
        self.assertIs(figure.panels["A"], figure.panels[0])
        self.assertIs(figure.panels.A, figure.panels[0])
        figure.close()

    def test_string_sequence_remains_flat_labels(self):
        labels = ["AAB", "CCB"]
        figure = mp.MultiPanel(shape=(1, 2), labels=labels)

        self.assertEqual(figure._labels, labels)
        self.assertIs(figure.panels["CCB"], figure.panels[1])
        figure.close()

    def test_panels_accept_arbitrary_labels(self):
        labels = ["A 1", "B-2"]
        figure = mp.MultiPanel(shape=(1, 2), labels=labels)

        self.assertIs(figure.panels["A 1"], figure.panels[0])
        self.assertIs(figure.panels["B-2"], figure.panels[1])
        with self.assertRaises(TypeError):
            figure.panels[0] = figure.panels[1]
        figure.close()

    def test_default_labels_extend_beyond_alphabet(self):
        figure = mp.MultiPanel(shape=(1, 28), labels=True)

        self.assertEqual(figure._labels[-3:], ["z", "aa", "ab"])
        self.assertIs(figure.panels.aa, figure.panels[26])
        self.assertIs(figure.panels["ab"], figure.panels[27])
        figure.close()

    def test_init_006_labels_array(self):
        """
        Test initialization of MultiPanel object.

        004 - Initialization based on ``labels`` being a numpy array label grid
        """

        labels = np.array([["A1", "A2"], ["B1", "B2"]])
        fig = mp.MultiPanel(labels=labels)
        self.assertEqual(fig.panels.__len__(), 4)
        self.assertEqual(set(fig._locations), set(product([0, 1], [0, 1])))

        labels = np.array([["A", "A"], ["B", "B"]])
        fig = mp.MultiPanel(labels=labels)
        self.assertEqual(set(fig._locations), {(0, range(2)), (1, range(2))})

        labels = np.array([["A", "B", "B"], ["C", "C", "C"], ["C", "C", "C"]])
        fig = mp.MultiPanel(labels=labels)

    def test_init_single_panel(self):
        for kwargs in ({"shape": (1, 1)}, {"grid": [(0, 0)]}):
            with self.subTest(**kwargs):
                figure = mp.MultiPanel(**kwargs)

                self.assertEqual(len(figure.panels), 1)
                figure.close()

    def test_savefig_forwards_to_matplotlib_figure(self):
        figure = mp.MultiPanel()

        with patch.object(figure.fig, "savefig", return_value="saved") as savefig:
            result = figure.savefig("figure.svg", dpi=300)

        savefig.assert_called_once_with("figure.svg", dpi=300)
        self.assertEqual(result, "saved")
        figure.close()

    def test_save_forwards_to_savefig(self):
        figure = mp.MultiPanel()

        with patch.object(figure, "savefig", return_value="saved") as savefig:
            result = figure.save("figure.svg", dpi=300)

        savefig.assert_called_once_with("figure.svg", dpi=300)
        self.assertEqual(result, "saved")
        figure.close()

    def test_label_defaults_and_alignment(self):
        cm = 1 / 2.54
        figsize_alignment = (15.24 * cm, 7.62 * cm)
        with matplotlib.style.context("spiffy"):
            figure = mp.MultiPanel(grid=[3, 2], figsize=figsize_alignment, labels=True)
            figure.fig.canvas.draw()

        label_artists = [panel.texts[0] for panel in figure.panels]
        renderer = figure.fig.canvas.get_renderer()
        label_bounds = [label.get_window_extent(renderer) for label in label_artists]

        self.assertEqual(figure._labels, ["a", "b", "c", "d", "e"])
        self.assertEqual(len(figure.fig.axes), len(figure.panels))
        self.assertEqual(label_artists[0].get_position(), (-20, 6))
        self.assertEqual(label_artists[0].get_family(), ["sans-serif"])
        self.assertEqual(label_artists[0].get_weight(), "bold")
        self.assertEqual(label_artists[0].get_fontsize(), 12)

        # Labels share an x position when panels share a left edge.
        self.assertAlmostEqual(label_bounds[0].x0, label_bounds[3].x0)
        # Labels share a baseline when panels share a top edge.
        self.assertAlmostEqual(label_bounds[0].y0, label_bounds[1].y0)
        self.assertAlmostEqual(label_bounds[1].y0, label_bounds[2].y0)
        figure.close()

    def test_label_options(self):
        uppercase = mp.MultiPanel(shape=(1, 2), labels=True, label_case="uppercase")
        self.assertEqual(uppercase._labels, ["A", "B"])
        uppercase.close()

        with self.assertWarns(DeprecationWarning):
            legacy = mp.MultiPanel(
                shape=(1, 2), labels=True, label_location=(-0.2, 1.0)
            )
        self.assertEqual(legacy.panels[0].texts[0].get_position(), (-0.2, 1.0))
        legacy.close()

        with self.assertRaises(TypeError):
            mp.MultiPanel(
                shape=(1, 2),
                labels=True,
                label_offset=(-20, 6),
                label_location=(-0.2, 1.0),
            )

    def test_kwargs(self):
        """
        Test if different keyword arguments work as expected
        """

        # Add keyword arguments for label generator
        kwargs = {
            "label_case": "lowercase",
            "label_size": 10,
            "label_weight": "normal",
            "label_location": (-0.2, 1),
            # Add keyword arguments for figure size
            "figsize": (8, 8),
            # Add keyword arguments for gridspec
            "left": 0.1,
            "bottom": 0.1,
            "right": 1,
            "top": 1,
            "wspace": 0.1,
            "hspace": 0.1,
            "width_ratios": (1, 2),
            "height_ratios": (1, 2),
        }

        fig = mp.MultiPanel(**kwargs)

        self.assertEqual(fig._labels, ["a", "b", "c", "d"])

    def test_unknown_kwargs_raise_before_creating_figure(self):
        figures_before = set(mp.plt.get_fignums())

        with self.assertRaisesRegex(
            TypeError, r"unexpected keyword arguments: figsizee, labelsize"
        ):
            mp.MultiPanel(labelsize=20, figsizee=(12, 9))

        self.assertEqual(set(mp.plt.get_fignums()), figures_before)

    def test_figsize_units_are_converted_to_inches(self):
        sizes = (("in", (1, 2)), ("cm", (2.54, 5.08)), ("mm", (25.4, 50.8)))
        for units, size in sizes:
            with self.subTest(units=units):
                figure = mp.MultiPanel(
                    shape=(1, 1), figsize=size, units=units, labels=False
                )

                np.testing.assert_allclose(figure.fig.get_size_inches(), (1, 2))
                figure.close()

    def test_unknown_figsize_units_raise_before_creating_figure(self):
        figures_before = set(mp.plt.get_fignums())

        with self.assertRaisesRegex(ValueError, "expected 'in', 'cm', or 'mm'"):
            mp.MultiPanel(figsize=(1, 2), units="pt")

        self.assertEqual(set(mp.plt.get_fignums()), figures_before)

    def test_gridspec_geometry_warns_with_constrained_layout(self):
        with (
            matplotlib.style.context("spiffy"),
            self.assertWarnsRegex(
                UserWarning, r"`left`, `hspace`.*mutually exclusive"
            ) as caught,
        ):
            figure = mp.MultiPanel(shape=(2, 2), left=0.4, hspace=0.9)

        self.assertEqual(Path(caught.filename), Path(__file__))
        self.assertTrue(figure.fig.get_constrained_layout())
        figure.close()

    def test_gridspec_kwargs_without_constrained_layout(self):
        with (
            matplotlib.style.context("spiffy"),
            matplotlib.rc_context({"figure.constrained_layout.use": False}),
            warnings.catch_warnings(),
        ):
            warnings.simplefilter("error")
            figure = mp.MultiPanel(
                shape=(2, 2), left=0.4, hspace=0.9, width_ratios=(1, 2)
            )
            figure.fig.canvas.draw()

        self.assertAlmostEqual(figure.panels[0].get_position().x0, 0.4)
        self.assertEqual(figure.gridspec.get_width_ratios(), (1, 2))
        figure.close()

    def test_gridspec_ratios_work_with_constrained_layout(self):
        with (
            matplotlib.style.context("spiffy"),
            warnings.catch_warnings(),
        ):
            warnings.simplefilter("error")
            figure = mp.MultiPanel(shape=(1, 2), width_ratios=(1, 2))

        self.assertTrue(figure.fig.get_constrained_layout())
        self.assertEqual(figure.gridspec.get_width_ratios(), (1, 2))
        figure.close()

    def test_width_ratios_follow_computed_grid_shape(self):
        width_ratios = (1, 1, 2, 2, 1, 1)
        figure = mp.MultiPanel(grid=[3, 2], width_ratios=width_ratios)

        self.assertEqual(figure.shape, (2, 6))
        self.assertEqual(figure.gridspec.get_width_ratios(), width_ratios)
        figure.close()

    def test_errors_invalid_inputs(self):
        """
        Test TypeErrors if invalid inputs are given
        """
        self.assertRaises(TypeError, mp.MultiPanel, grid=[1, 2, "string"])

        self.assertRaises(TypeError, mp.MultiPanel, shape=(1, (2, 4)))

        self.assertRaises(TypeError, mp.MultiPanel, labels=123)

        # Too few labels for the number of panels
        self.assertRaises(AssertionError, mp.MultiPanel, grid=(1, 3), labels=["ABC"])

    def test_warnings(self):
        """
        Test Warnings if some conditions are met
        """

        # If parameters given are ignored
        self.assertWarns(
            Warning, mp.MultiPanel, labels={"A1": (0, 0), "A2": (0, 1)}, shape=(3, 2)
        )

        # If panels overlap
        self.assertWarns(
            Warning, mp.MultiPanel, labels={"A1": (0, 0), "A2": (0, range(2))}
        )

    def test_overlap_warning_reports_coordinates_and_caller(self):
        with self.assertWarnsRegex(
            UserWarning, r"panel coordinates overlap: \[\(0, 0\)\]"
        ) as caught:
            figure = mp.MultiPanel(grid=[(0, 0), (0, 0)])

        self.assertEqual(Path(caught.filename), Path(__file__))
        figure.close()


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
        self.assertEqual(out[2], "c")
        self.assertEqual(out[-1], "z")

    def test_more_than_one_alphabet(self):
        out = mp._get_letters(count=29)
        self.assertEqual(out[-4:], ["z", "aa", "ab", "ac"])


class Test_is_iter_of_iters(unittest.TestCase):
    def test_default(self):
        """Test _is_iter_of_iters"""
        self.assertTrue(mp._is_iter_of_iters([[1]]))
        self.assertTrue(mp._is_iter_of_iters([[1], [2]]))
        self.assertTrue(mp._is_iter_of_iters(["ABC", "DEF"]))
        self.assertTrue(mp._is_iter_of_iters([]))
        self.assertFalse(mp._is_iter_of_iters(1))


class Test_decode_label_array(unittest.TestCase):
    def test_simple_array(self):
        grid_dict = mp._decode_label_array([["A", "B", "C"], ["D", "D", "D"]])
        self.assertTrue(grid_dict["D"] == (1, range(3)))

        grid_dict = mp._decode_label_array([["A", "C", "E"], ["B", "D", "E"]])
        self.assertTrue(grid_dict["E"] == (range(2), 2))

        grid_dict = mp._decode_label_array([["A", "C", "C"], ["B", "C", "C"]])
        self.assertTrue(grid_dict["C"] == (range(2), range(1, 3)))

        grid_dict = mp._decode_label_array(
            [["A", "B", "B"], ["C", "C", "C"], ["C", "C", "C"]]
        )
        self.assertTrue(grid_dict["C"] == (range(1, 3), range(3)))

        # discontiguous labels
        self.assertRaises(TypeError, mp._decode_label_array, [["A", "B"], ["B", "A"]])
        self.assertRaises(
            TypeError, mp._decode_label_array, [["A", "B", "C"], ["C", "B", "A"]]
        )

        # different types of iterable inputs
        grid_dict = mp._decode_label_array(["ABC", "DDD"])
        self.assertTrue(grid_dict["D"] == (1, range(3)))

        grid_dict = mp._decode_label_array(np.array([["A", "B", "C"], ["D", "D", "D"]]))
        self.assertTrue(grid_dict["D"] == (1, range(3)))

        # should raise on invalid input
        self.assertRaises(TypeError, mp._decode_label_array, 1)


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
        tuple = (range(2), 1)
        out = mp._get_grid_location(tuple, self.grid)

        self.assertEqual(out, self.grid[0:2, 1])

    def test_int_colrange(self):
        tuple = (1, range(3))
        out = mp._get_grid_location(tuple, self.grid)

        self.assertEqual(out, self.grid[1, 0:3])

    def test_ranges(self):
        tuple = (range(2), range(3))
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
            (0, range(3)),
            (0, range(3, 6)),
            (1, range(2)),
            (1, range(2, 4)),
            (1, range(4, 6)),
            (2, range(6)),
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

    def test_large_subplots(self):
        grid_dict = mp._decode_label_array(
            [["A", "B", "B"], ["C", "C", "C"], ["C", "C", "C"]]
        )
        self.assertEqual(mp._find_max_tuple(grid_dict.values()), (3, 3))


class Test_panel_overlap(unittest.TestCase):
    def test_default(self):
        self.assertEqual(mp._panel_overlap([]), set())
        self.assertEqual(mp._panel_overlap([(0, 0)]), set())
        self.assertFalse(mp._panel_overlap([(0, 0), (0, 1)]))
        self.assertFalse(mp._panel_overlap([(0, 0), (1, 0), (0, 1), (1, 1)]))
        self.assertTrue(mp._panel_overlap([(0, 0), (1, 0), (0, 1), (1, 0)]))
        self.assertFalse(mp._panel_overlap([(0, range(10)), (1, range(10))]))
        self.assertTrue(mp._panel_overlap([(0, range(2)), (0, range(1, 2))]))
        self.assertFalse(
            mp._panel_overlap([(range(2), range(2)), (range(2, 4), range(2, 4))])
        )
        self.assertTrue(
            mp._panel_overlap([(range(2), range(2)), (range(1, 4), range(1, 4))])
        )

    def test_large_subplots(self):
        grid_dict = mp._decode_label_array(
            [["A", "B", "B"], ["C", "C", "C"], ["C", "C", "C"]]
        )
        self.assertFalse(mp._panel_overlap(grid_dict.values(), (3, 3)))

    def test_iterable_spans(self):
        self.assertEqual(
            mp._panel_overlap([([0, 1], 2), (np.arange(1, 3), 2)]), {(1, 2)}
        )
