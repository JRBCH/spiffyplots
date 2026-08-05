"""Populate axes with reproducible example data."""

from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes


def populate_random_data(
    axes: Iterable[Axes], colors: Iterable | None = None, seed: int | None = 0
) -> None:
    """Populate axes with a repeating mix of random example plots.

    Plot types cycle through a histogram, scatter plot, and time series. Data
    are generated independently for every panel.

    Args:
        axes: Axes to populate.
        colors: Colors to cycle through. Defaults to the active Matplotlib
            color cycle.
        seed: Seed for the random number generator. Defaults to 0.
    """
    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    colors = tuple(colors)
    if not colors:
        raise ValueError("colors must contain at least one color")

    rng = np.random.default_rng(seed)
    time = np.arange(250) * 0.1

    for index, axis in enumerate(axes):
        color = colors[index % len(colors)]
        plot_type = index % 3

        if plot_type == 0:
            values = rng.normal(
                loc=rng.uniform(-0.5, 0.5),
                scale=rng.uniform(0.6, 1.2),
                size=500,
            )
            axis.hist(values, color=color)
            axis.set_xlabel("value")
            axis.set_ylabel("frequency")

        elif plot_type == 1:
            x_values = rng.standard_normal(200)
            y_values = 0.4 * x_values + rng.standard_normal(200)
            axis.scatter(x_values, y_values, color=color, alpha=0.6)
            axis.set_xlabel("variable 1")
            axis.set_ylabel("variable 2")

        else:
            reference = np.sin(time + rng.uniform(0, 2 * np.pi))
            samples = reference + rng.standard_normal((20, time.size))
            mean = samples.mean(axis=0)
            std = samples.std(axis=0)
            axis.plot(time, mean, color=color)
            axis.plot(time, reference, color="black")
            axis.fill_between(
                time,
                mean - std,
                mean + std,
                color=color,
                alpha=0.3,
            )
            axis.set_xlabel("time (s)")
            axis.set_ylabel("value")
