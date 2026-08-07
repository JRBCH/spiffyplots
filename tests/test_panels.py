"""Public panel-label behavior."""

import matplotlib
import matplotlib.pyplot as plt
import pytest

from spiffyplots import label_panels
from spiffyplots.panels import get_letters


def test_letter_labels_continue_after_the_alphabet():
    assert get_letters(count=28)[-3:] == ["z", "aa", "ab"]
    assert get_letters(case="uppercase", count=2) == ["A", "B"]

    with pytest.raises(ValueError, match="uppercase"):
        get_letters(case="titlecase")


def test_default_axes_are_labelled_in_visual_reading_order():
    figure = plt.figure()
    lower_right = figure.add_axes((0.55, 0.1, 0.35, 0.3))
    upper_left = figure.add_axes((0.1, 0.6, 0.35, 0.3))
    lower_left = figure.add_axes((0.1, 0.1, 0.35, 0.3))
    upper_right = figure.add_axes((0.55, 0.6, 0.35, 0.3))

    label_panels(figure)

    assert upper_left.texts[0].get_text() == "a"
    assert upper_right.texts[0].get_text() == "b"
    assert lower_left.texts[0].get_text() == "c"
    assert lower_right.texts[0].get_text() == "d"


def test_automatic_labels_skip_colorbar_axes():
    figure, axes = plt.subplots(1, 2)
    image = axes[0].imshow([[1, 2], [3, 4]])
    colorbar = figure.colorbar(image, ax=axes[0])

    texts = label_panels(figure)

    assert [text.get_text() for text in texts] == ["a", "b"]
    assert not colorbar.ax.texts


def test_explicit_axes_labels_and_text_options_are_respected():
    figure, axes = plt.subplots(1, 3)
    texts = label_panels(
        figure,
        axes=[axes[2], axes[0]],
        labels=["x", "y"],
        offset=(-10, 5),
        size=11,
        color="red",
        family="serif",
    )

    assert [text.get_text() for text in texts] == ["x", "y"]
    assert texts[0] is axes[2].texts[0]
    assert texts[0].xyann == (-10, 5)
    assert texts[0].get_fontsize() == 11
    assert texts[0].get_fontfamily() == ["serif"]
    assert texts[0].get_color() == "red"
    assert not axes[1].texts


def test_default_size_uses_axes_labelsize_and_counts_must_match():
    figure, axis = plt.subplots()
    with matplotlib.rc_context({"font.size": 6, "axes.labelsize": 8}):
        (text,) = label_panels(figure, axes=[axis])

    assert text.get_fontsize() == 8
    with pytest.raises(ValueError, match="labels for 1 axes"):
        label_panels(figure, axes=[axis], labels=["a", "b"])
