"""Public color-palette behavior."""

import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_rgb

from spiffyplots import cmap, colors

PALETTES = (
    colors.tol_bright,
    colors.tol_high_contrast,
    colors.tol_vibrant,
    colors.tol_muted,
    colors.tol_medium_contrast,
    colors.tol_light,
    colors.tol_pale,
    colors.tol_dark,
    colors.okabe_ito,
)


def test_palettes_are_named_valid_and_distinct():
    for palette in PALETTES:
        assert len(palette) == len(palette.names) == len(set(palette))
        assert "#000000" in palette
        for color in palette:
            to_rgb(color)

    assert colors.tol_vibrant.blue == "#0077BB"
    assert colors.SPIFFY_CYCLE is colors.tol_vibrant


def test_colorsets_support_named_selection_slicing_and_cycles():
    subset = colors.tol_muted[:3]
    picked = colors.tol_muted.pick("sand", "rose")

    assert subset.names == ("rose", "indigo", "sand")
    assert subset.rose == colors.tol_muted.rose
    assert picked.names == ("sand", "rose")
    with plt.rc_context({"axes.prop_cycle": picked.cycler()}):
        assert plt.rcParams["axes.prop_cycle"].by_key()["color"] == list(picked)

    with pytest.raises(KeyError, match="chartreuse"):
        colors.tol_muted.pick("chartreuse")


def test_from_cmap_samples_the_requested_range():
    sampled = colors.from_cmap(cmap.sequential, 4, lo=0.2, hi=0.8)

    assert len(sampled) == len(set(sampled)) == 4
    assert to_rgb(sampled[0]) == pytest.approx(cmap.sequential(0.2)[:3], abs=1 / 255)
    assert to_rgb(sampled[-1]) == pytest.approx(cmap.sequential(0.8)[:3], abs=1 / 255)
    assert len(colors.from_cmap("viridis", 1)) == 1

    for kwargs in ({"n": 0}, {"n": 2, "lo": 0.8, "hi": 0.2}):
        with pytest.raises(ValueError):
            colors.from_cmap(cmap.sequential, **kwargs)


def test_shades_are_distinct_and_ordered_light_to_dark():
    shades = colors.shades(colors.tol_vibrant.blue, 6)
    luminances = [_luminance(shade) for shade in shades]

    assert len(set(shades)) == 6
    assert luminances == sorted(luminances, reverse=True)


def _luminance(color) -> float:
    red, green, blue = to_rgb(color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue
