"""Public example-data behavior."""

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_rgba

from spiffyplots import populate_random_data


def test_random_data_cycles_plot_types_colors_and_is_reproducible():
    _, first_axes = plt.subplots(1, 3)
    _, second_axes = plt.subplots(1, 3)

    populate_random_data(first_axes, colors=["red", "blue"], seed=4)
    populate_random_data(second_axes, colors=["red", "blue"], seed=4)

    assert first_axes[0].patches[0].get_facecolor() == to_rgba("red")
    assert first_axes[1].collections[0].get_facecolor()[0] == pytest.approx(
        to_rgba("blue", alpha=0.6)
    )
    assert len(first_axes[2].lines) == 2
    assert len(first_axes[2].collections) == 1
    np.testing.assert_allclose(
        first_axes[2].lines[0].get_ydata(),
        second_axes[2].lines[0].get_ydata(),
    )


def test_random_data_rejects_an_empty_color_cycle():
    _, axis = plt.subplots()

    with pytest.raises(ValueError, match="at least one color"):
        populate_random_data([axis], colors=[])
