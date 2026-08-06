"""Tests for `spiffyplots.panels` module."""

import unittest

import matplotlib
import matplotlib.pyplot as plt

import spiffyplots.panels as pn
from spiffyplots import label_panels

matplotlib.use("Agg")


class TestGetLetters(unittest.TestCase):
    def test_lowercase(self):
        out = pn.get_letters(case="lowercase")
        self.assertEqual(out[2], "c")
        self.assertEqual(out[-1], "z")

    def test_uppercase(self):
        out = pn.get_letters(case="uppercase")
        self.assertEqual(out[2], "C")
        self.assertEqual(out[-1], "Z")

    def test_more_than_one_alphabet(self):
        out = pn.get_letters(count=29)
        self.assertEqual(out[-4:], ["z", "aa", "ab", "ac"])

    def test_unknown_case_raises(self):
        with self.assertRaises(ValueError):
            pn.get_letters(case="titlecase")


class TestLabelPanels(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_subplots_reading_order(self):
        """Rows top to bottom, left to right within a row."""
        fig, axs = plt.subplots(3, 3)
        texts = label_panels(fig)

        self.assertEqual([t.get_text() for t in texts], pn.get_letters(count=9))
        # First row is a, b, c across, not down.
        for expected, ax in zip("abc", axs[0]):
            self.assertEqual(ax.texts[0].get_text(), expected)
        self.assertEqual(axs[1][0].texts[0].get_text(), "d")

    def test_creation_order_differs_from_reading_order(self):
        """Axes added bottom-right first still label in reading order."""
        fig = plt.figure()
        bottom_right = fig.add_subplot(2, 2, 4)
        top_left = fig.add_subplot(2, 2, 1)
        top_right = fig.add_subplot(2, 2, 2)

        label_panels(fig)

        self.assertEqual(top_left.texts[0].get_text(), "a")
        self.assertEqual(top_right.texts[0].get_text(), "b")
        self.assertEqual(bottom_right.texts[0].get_text(), "c")

    def test_mosaic_spanning_panel(self):
        fig, axs = plt.subplot_mosaic([["a", "a"], ["b", "c"]])
        label_panels(fig)

        self.assertEqual(axs["a"].texts[0].get_text(), "a")
        self.assertEqual(axs["b"].texts[0].get_text(), "b")
        self.assertEqual(axs["c"].texts[0].get_text(), "c")

    def test_unequal_heights_stay_one_row(self):
        """Panels whose tops are level but heights differ are a single row."""
        fig = plt.figure()
        tall = fig.add_axes((0.1, 0.1, 0.3, 0.8))
        short = fig.add_axes((0.5, 0.6, 0.3, 0.3))

        label_panels(fig)

        self.assertEqual(tall.texts[0].get_text(), "a")
        self.assertEqual(short.texts[0].get_text(), "b")

    def test_colorbar_axes_skipped(self):
        fig, axs = plt.subplots(1, 2)
        image = axs[0].imshow([[1, 2], [3, 4]])
        colorbar = fig.colorbar(image, ax=axs[0])

        texts = label_panels(fig)

        self.assertEqual(len(texts), 2)
        self.assertEqual(len(colorbar.ax.texts), 0)
        self.assertEqual(axs[0].texts[0].get_text(), "a")
        self.assertEqual(axs[1].texts[0].get_text(), "b")

    def test_inset_axes_skipped(self):
        """Insets are children of their parent axes, not of the figure."""
        fig, ax = plt.subplots()
        inset = ax.inset_axes((0.5, 0.5, 0.3, 0.3))

        texts = label_panels(fig)

        self.assertEqual(len(texts), 1)
        self.assertEqual(len(inset.texts), 0)

    def test_subfigures(self):
        """Subfigure axes sort against each other, not within their subfigure."""
        fig = plt.figure()
        left, right = fig.subfigures(1, 2)
        left_ax = left.subplots()
        right_ax = right.subplots()

        label_panels(fig)

        self.assertEqual(left_ax.texts[0].get_text(), "a")
        self.assertEqual(right_ax.texts[0].get_text(), "b")

    def test_explicit_axes_subset_and_order(self):
        fig, axs = plt.subplots(1, 3)
        texts = label_panels(fig, axes=[axs[2], axs[0]])

        self.assertEqual(len(texts), 2)
        self.assertEqual(axs[2].texts[0].get_text(), "a")
        self.assertEqual(axs[0].texts[0].get_text(), "b")
        self.assertEqual(len(axs[1].texts), 0)

    def test_explicit_labels(self):
        fig, axs = plt.subplots(1, 3)
        label_panels(fig, labels=["A", "B", "C"])

        self.assertEqual([ax.texts[0].get_text() for ax in axs], ["A", "B", "C"])

    def test_uppercase(self):
        fig, axs = plt.subplots(1, 2)
        label_panels(fig, case="uppercase")

        self.assertEqual([ax.texts[0].get_text() for ax in axs], ["A", "B"])

    def test_label_count_mismatch_raises(self):
        fig, _ = plt.subplots(1, 3)
        with self.assertRaises(ValueError):
            label_panels(fig, labels=["A", "B"])

    def test_returns_text_artists(self):
        fig, axs = plt.subplots(1, 2)
        texts = label_panels(fig)

        texts[0].set_color("red")
        self.assertEqual(axs[0].texts[0].get_color(), "red")

    def test_offset_in_points_from_corner(self):
        fig, ax = plt.subplots()
        (text,) = label_panels(fig, axes=[ax], offset=(-24, 6))

        self.assertEqual(text.xy, (0, 1))
        self.assertEqual(text.xyann, (-24, 6))
        self.assertEqual(text.get_anncoords(), "offset points")

    def test_text_kwargs_override_defaults(self):
        """family and usetex are defaults here, not hardcoded."""
        fig, ax = plt.subplots()
        (text,) = label_panels(fig, axes=[ax], family="serif", style="italic")

        self.assertEqual(text.get_fontfamily(), ["serif"])
        self.assertEqual(text.get_fontstyle(), "italic")

    def test_style_defaults_are_not_overridden_by_size_none(self):
        """size=None and color=None leave the rcParams defaults in place."""
        fig, ax = plt.subplots()
        with matplotlib.rc_context({"font.size": 17, "text.color": "blue"}):
            (text,) = label_panels(fig, axes=[ax])

        self.assertEqual(text.get_fontsize(), 17)
        self.assertEqual(text.get_color(), "blue")

    def test_size_none_follows_axes_labelsize(self):
        """Panel letters follow axes.labelsize, not font.size."""
        fig, ax = plt.subplots()
        with matplotlib.rc_context({"font.size": 6.0, "axes.labelsize": 7.0}):
            (text,) = label_panels(fig, axes=[ax])

        self.assertEqual(text.get_fontsize(), 7.0)

    def test_weight_and_size(self):
        fig, ax = plt.subplots()
        (text,) = label_panels(fig, axes=[ax], size=14, weight="normal", color="green")

        self.assertEqual(text.get_fontsize(), 14)
        self.assertEqual(text.get_fontweight(), "normal")
        self.assertEqual(text.get_color(), "green")

    def test_empty_figure(self):
        fig = plt.figure()
        self.assertEqual(label_panels(fig), [])


if __name__ == "__main__":
    unittest.main()
