"""Tests for random example-data plotting."""

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_rgba

from spiffyplots import populate_random_data


def test_populate_random_data_cycles_plot_types_and_colors():
    figure, axes = plt.subplots(2, 3)

    populate_random_data(axes.flat, colors=["red", "blue"], seed=3)

    assert axes[0, 0].patches
    assert len(axes[0, 1].collections) == 1
    assert len(axes[0, 2].lines) == 2
    assert len(axes[0, 2].collections) == 1
    assert axes[0, 0].patches[0].get_facecolor() == to_rgba("red")
    assert axes[0, 1].collections[0].get_facecolor()[0] == pytest.approx(
        to_rgba("blue", alpha=0.6)
    )
    assert axes[0, 2].lines[0].get_color() == "red"
    plt.close(figure)


def test_populate_random_data_is_reproducible():
    first_figure, first_axes = plt.subplots(1, 3)
    second_figure, second_axes = plt.subplots(1, 3)

    populate_random_data(first_axes, seed=4)
    populate_random_data(second_axes, seed=4)

    np.testing.assert_allclose(
        first_axes[2].lines[0].get_ydata(),
        second_axes[2].lines[0].get_ydata(),
    )
    plt.close(first_figure)
    plt.close(second_figure)


def test_populate_random_data_rejects_empty_colors():
    figure, axis = plt.subplots()

    with pytest.raises(ValueError, match="at least one color"):
        populate_random_data([axis], colors=[])

    plt.close(figure)
