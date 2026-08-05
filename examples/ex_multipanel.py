"""Generate equivalent Matplotlib and Spiffyplots multi-panel examples."""

import string
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from spiffyplots import MultiPanel

# Part 1: generate common data and define shared plotting helpers.
SEED = 0
N_SCATTER = 200
N_HISTOGRAM = 500
N_TRIALS = 20
N_TIMEPOINTS = 250
DT = 0.1
GAMMA_SHAPE = 5
GAMMA_SCALE = 8
SCATTER_ALPHA = 0.6
BAND_ALPHA = 0.3

cm = 1 / 2.54
figsize_example = (22.86 * cm, 10.16 * cm)
figure_dpi = 150
label_offset_default = (-20, 6)
label_size_default = 12
label_weight_default = "bold"
label_family_default = "sans-serif"
color_reference = "black"

output_directory = Path(__file__).resolve().parent
output_matplotlib = output_directory / "multipanel_mpl.png"
output_spiffy = output_directory / "multipanel_spiffy.png"

rng = np.random.default_rng(SEED)
time = np.arange(N_TIMEPOINTS) * DT
reference_sine = np.sin(time)
reference_cosine = np.cos(time)

data = {
    "scatter-normal-x": rng.standard_normal(N_SCATTER),
    "scatter-normal-y": rng.standard_normal(N_SCATTER),
    "scatter-uniform-x": rng.random(N_SCATTER),
    "scatter-uniform-y": rng.random(N_SCATTER),
    "hist-normal": rng.standard_normal(N_HISTOGRAM),
    "hist-gamma": rng.gamma(GAMMA_SHAPE, GAMMA_SCALE, N_HISTOGRAM),
    "timeseries-sine": reference_sine + rng.standard_normal((N_TRIALS, N_TIMEPOINTS)),
    "timeseries-cosine": reference_cosine
    + rng.standard_normal((N_TRIALS, N_TIMEPOINTS)),
}


def plot_histogram(axis, values, color):
    axis.hist(values, color=color)
    axis.set_xlabel("value")
    axis.set_ylabel("frequency")


def plot_scatter(axis, x_values, y_values, color):
    axis.scatter(x_values, y_values, alpha=SCATTER_ALPHA, facecolor=color)
    axis.set_xlabel("variable 1")
    axis.set_ylabel("variable 2")


def plot_time_series(axis, samples, reference, color):
    mean = samples.mean(axis=0)
    std = samples.std(axis=0)
    axis.plot(time, mean, color=color)
    axis.plot(time, reference, color=color_reference)
    axis.fill_between(time, mean - std, mean + std, color=color, alpha=BAND_ALPHA)
    axis.set_xlabel("time (s)")
    axis.set_ylabel("value")


# Part 2: construct the figure with Matplotlib's default style and GridSpec.
with plt.style.context("default"):
    figure_matplotlib = plt.figure(figsize=figsize_example, layout="constrained")
    gridspec = figure_matplotlib.add_gridspec(nrows=2, ncols=4)
    colors_matplotlib = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    axis_a = figure_matplotlib.add_subplot(gridspec[0, 0])
    plot_histogram(axis_a, data["hist-normal"], colors_matplotlib[0])

    axis_b = figure_matplotlib.add_subplot(gridspec[0, 1])
    plot_scatter(
        axis_b,
        data["scatter-normal-x"],
        data["scatter-normal-y"],
        colors_matplotlib[0],
    )

    axis_c = figure_matplotlib.add_subplot(gridspec[0, 2])
    plot_histogram(axis_c, data["hist-gamma"], colors_matplotlib[1])

    axis_d = figure_matplotlib.add_subplot(gridspec[0, 3])
    plot_scatter(
        axis_d,
        data["scatter-uniform-x"],
        data["scatter-uniform-y"],
        colors_matplotlib[1],
    )

    axis_e = figure_matplotlib.add_subplot(gridspec[1, 0:2])
    plot_time_series(
        axis_e,
        data["timeseries-sine"],
        reference_sine,
        colors_matplotlib[0],
    )

    axis_f = figure_matplotlib.add_subplot(gridspec[1, 2:4])
    plot_time_series(
        axis_f,
        data["timeseries-cosine"],
        reference_cosine,
        colors_matplotlib[1],
    )

    panels_matplotlib = (
        axis_a,
        axis_b,
        axis_c,
        axis_d,
        axis_e,
        axis_f,
    )

    labels_matplotlib = string.ascii_lowercase[: len(panels_matplotlib)]
    for label, axis in zip(labels_matplotlib, panels_matplotlib, strict=True):
        axis.annotate(
            label,
            xy=(0, 1),
            xycoords="axes fraction",
            xytext=label_offset_default,
            textcoords="offset points",
            size=label_size_default,
            weight=label_weight_default,
            family=label_family_default,
            horizontalalignment="left",
            verticalalignment="baseline",
            annotation_clip=False,
        )

    figure_matplotlib.savefig(output_matplotlib, dpi=figure_dpi)
    plt.close(figure_matplotlib)


# Part 3: construct the same figure with the Spiffy style and MultiPanel.
with plt.style.context("spiffy"):
    figure_spiffy = MultiPanel(
        grid=(4, 2),
        figsize=figsize_example,
        labels=True,
    )

    colors_spiffy = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    plot_histogram(
        figure_spiffy.panels.a,
        data["hist-normal"],
        colors_spiffy[0],
    )
    plot_scatter(
        figure_spiffy.panels.b,
        data["scatter-normal-x"],
        data["scatter-normal-y"],
        colors_spiffy[0],
    )
    plot_histogram(
        figure_spiffy.panels.c,
        data["hist-gamma"],
        colors_spiffy[1],
    )
    plot_scatter(
        figure_spiffy.panels.d,
        data["scatter-uniform-x"],
        data["scatter-uniform-y"],
        colors_spiffy[1],
    )
    plot_time_series(
        figure_spiffy.panels.e,
        data["timeseries-sine"],
        reference_sine,
        colors_spiffy[0],
    )
    plot_time_series(
        figure_spiffy.panels.f,
        data["timeseries-cosine"],
        reference_cosine,
        colors_spiffy[1],
    )
    figure_spiffy.fig.savefig(output_spiffy, dpi=figure_dpi)
    figure_spiffy.close()
