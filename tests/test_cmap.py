"""Public colormap behavior."""

import matplotlib
import pytest
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_hex

from spiffyplots import _tol_data, cmap, colors


def test_tol_colormaps_register_with_short_and_reversed_names():
    for name, data in _tol_data.CMAPS.items():
        forward = getattr(cmap, name)
        backward = getattr(cmap, f"{name}_r")

        assert forward.name == f"tol.{name}"
        assert backward.name == f"tol.{name}_r"
        assert to_hex(forward(0.0)) == to_hex(backward(1.0))
        assert to_hex(forward.get_bad()) == data["bad"].lower()


def test_colormap_resolution_prefers_spiffy_aliases_then_matplotlib():
    assert cmap.sequential.name == "tol.iridescent"
    assert cmap.diverging_r.name == "tol.nightfall_r"
    assert cmap.get("viridis").name == "viridis"
    selected = cmap.sequential
    assert cmap.get(selected) is selected

    with pytest.raises(KeyError, match="not_a_colormap"):
        cmap.get("not_a_colormap")
    with pytest.raises(AttributeError, match="not_a_colormap"):
        _ = cmap.not_a_colormap


def test_optional_colormap_packages_resolve_by_short_name():
    pytest.importorskip("cmcrameri")
    pytest.importorskip("colorcet")

    assert cmap.batlow.name == "cmc.batlow"
    assert cmap.kbc.name == "cet_kbc"
    assert cmap.gray.name == "gray"


def test_colormap_builders_preserve_their_semantics():
    continuous = cmap.from_colors(["white", "black"])
    discrete = cmap.from_colors(colors.tol_bright[:3], discrete=True)
    ramp = cmap.from_base(colors.tol_vibrant.blue)

    assert isinstance(continuous, LinearSegmentedColormap)
    assert isinstance(discrete, ListedColormap)
    assert discrete.colors == list(colors.tol_bright[:3])
    assert to_hex(ramp(0.0)) == "#ffffff"
    assert _luminance(ramp(1.0)) < _luminance(colors.tol_vibrant.blue)

    with pytest.raises(ValueError, match="at least two"):
        cmap.from_colors(["white"])
    with pytest.raises(ValueError, match="dark"):
        cmap.from_base("blue", dark=1)


def test_discrete_rainbow_returns_the_requested_palette_or_raises():
    rainbow = cmap.discrete_rainbow(3)

    assert rainbow.colors == ["#1965B0", "#F7F056", "#DC050C"]
    assert cmap.get("rainbow").name == "rainbow"
    for invalid in (0, 24):
        with pytest.raises(ValueError, match="1 to 23"):
            cmap.discrete_rainbow(invalid)


def _luminance(color) -> float:
    red, green, blue = matplotlib.colors.to_rgb(color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue
