"""Tests for `spiffyplots.cmap`."""

import importlib
import itertools
import warnings

import matplotlib
import numpy as np
import pytest
from matplotlib.colors import (
    Colormap,
    LinearSegmentedColormap,
    ListedColormap,
    to_hex,
)

import spiffyplots
from spiffyplots import _tol_data, cmap, colors

TOL_NAMES = sorted(_tol_data.CMAPS)


@pytest.mark.parametrize("name", TOL_NAMES)
def test_registered_under_the_tol_prefix(name):
    """Reaches matplotlib's registry, forward and reversed."""
    assert f"tol.{name}" in matplotlib.colormaps
    assert f"tol.{name}_r" in matplotlib.colormaps


@pytest.mark.parametrize("name", TOL_NAMES)
def test_reachable_by_short_name(name):
    """Attribute access drops the prefix."""
    assert getattr(cmap, name).name == f"tol.{name}"
    assert getattr(cmap, f"{name}_r").name == f"tol.{name}_r"


@pytest.mark.parametrize("name", TOL_NAMES)
def test_reversed_is_actually_reversed(name):
    forward = cmap.get(name)
    backward = cmap.get(f"{name}_r")
    assert to_hex(forward(0.0)) == to_hex(backward(1.0))
    assert to_hex(forward(1.0)) == to_hex(backward(0.0))


@pytest.mark.parametrize("name", TOL_NAMES)
def test_masked_data_colour_survives_registration(name):
    """Tol gives a bad-data colour per map; it must not be lost."""
    assert to_hex(cmap.get(name).get_bad()) == _tol_data.CMAPS[name]["bad"].lower()


def test_prefix_is_not_optional():
    """Tol names collide with matplotlib builtins and amazingly, the colours differ,
    so usign the bare name would change what an existing `image.cmap: YlOrBr` means."""
    for name in ("YlOrBr", "PRGn"):
        assert name in matplotlib.colormaps
        with pytest.raises(ValueError, match="builtin"):
            matplotlib.colormaps.register(cmap.get(name), name=name, force=True)

        tol_map, builtin = cmap.get(name), matplotlib.colormaps[name]
        differences = [
            x
            for x in np.linspace(0, 1, 256)
            if to_hex(tol_map(x)) != to_hex(builtin(x))
        ]
        assert differences, f"Tol's {name} is indistinguishable from matplotlib's"


class TestResolution:
    def test_semantic_aliases(self):
        assert cmap.sequential.name == "tol.iridescent"
        assert cmap.diverging.name == "tol.nightfall"

    def test_semantic_aliases_reverse(self):
        assert cmap.sequential_r.name == "tol.iridescent_r"
        assert cmap.diverging_r.name == "tol.nightfall_r"

    def test_falls_through_to_matplotlib(self):
        assert cmap.viridis.name == "viridis"
        assert cmap.get("magma_r").name == "magma_r"

    def test_colormap_passes_through(self):
        assert cmap.get(cmap.sequential) is not None
        assert cmap.get(cmap.viridis).name == "viridis"

    def test_unknown_name_names_the_optional_packages(self):
        with pytest.raises(AttributeError, match="cmcrameri|colorcet|tol"):
            _ = cmap.not_a_colormap

    def test_get_raises_keyerror(self):
        with pytest.raises(KeyError, match="not_a_colormap"):
            cmap.get("not_a_colormap")

    def test_dunder_lookups_do_not_resolve(self):
        """Introspection asks for dunders; they must not hit the resolver."""
        with pytest.raises(AttributeError):
            _ = cmap.__wrapped__

    def test_dir_offers_the_short_names(self):
        listed = dir(cmap)
        assert "sequential" in listed
        assert "iridescent" in listed
        assert "viridis" in listed


class TestRegistrationIsIdempotent:
    def test_reimporting_the_module_does_not_warn(self):
        """Reload happens in normal use (notebook autoreload), and
        `register(force=True)` would warn about overwriting."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            importlib.reload(cmap)
        overwrites = [
            str(entry.message) for entry in caught if "verwriting" in str(entry.message)
        ]
        assert not overwrites, overwrites
        assert "tol.iridescent" in matplotlib.colormaps

    def test_reloading_the_package_keeps_the_colormaps(self):
        importlib.reload(spiffyplots)
        assert "tol.iridescent" in matplotlib.colormaps


class TestCompanions:
    """The cmcrameri and colorcet fall-through, when they are importable."""

    @pytest.mark.parametrize(
        ("module", "name", "expected"),
        [
            ("cmcrameri", "batlow", "cmc.batlow"),
            ("cmcrameri", "batlow_r", "cmc.batlow_r"),
            ("cmcrameri", "bamO", "cmc.bamO"),
            ("colorcet", "kbc", "cet_kbc"),
            ("colorcet", "kbc_r", "cet_kbc_r"),
            ("colorcet", "CET_L1", "cet_CET_L1"),
        ],
    )
    def test_short_names_resolve(self, module, name, expected):
        pytest.importorskip(module)
        resolved = getattr(cmap, name)
        assert resolved.name == expected
        assert isinstance(resolved, Colormap)

    @pytest.mark.parametrize("name", ["gray", "coolwarm", "rainbow"])
    def test_matplotlib_wins_bare_name_ties(self, name):
        """Deliberate: a bare name means the same thing whether or not colorcet
        is installed. `cet_<name>` gets colorcet's, and works as an attribute
        because the prefix is a valid identifier, unlike cmcrameri's `cmc.`."""
        pytest.importorskip("colorcet")
        assert cmap.get(name).name == name
        assert getattr(cmap, f"cet_{name}").name == f"cet_{name}"

    def test_prefixed_namespaces_do_not_collide(self):
        pytest.importorskip("cmcrameri")
        pytest.importorskip("colorcet")
        cmap.get("batlow")  # trigger the lazy imports
        cmap.get("kbc")
        groups = [
            {n[len(p) :] for n in matplotlib.colormaps if n.startswith(p)}
            for p in ("tol.", "cmc.", "cet_")
        ]
        for first, second in itertools.combinations(groups, 2):
            assert not first & second


class TestFromColors:
    def test_interpolates_by_default(self):
        built = cmap.from_colors(["#FFFFFF", "#000000"])
        assert isinstance(built, LinearSegmentedColormap)
        assert to_hex(built(0.5)) not in {"#ffffff", "#000000"}

    def test_discrete_gives_flat_bands(self):
        built = cmap.from_colors(colors.tol_muted, discrete=True)
        assert isinstance(built, ListedColormap)
        assert built.N == len(colors.tol_muted)
        assert [to_hex(c) for c in built.colors] == [
            c.lower() for c in colors.tol_muted
        ]

    def test_accepts_a_colorset_directly(self):
        assert cmap.from_colors(colors.tol_bright).N > 0

    def test_rejects_a_single_colour(self):
        with pytest.raises(ValueError, match="at least two"):
            cmap.from_colors(["#FFFFFF"])


class TestFromBase:
    def test_starts_at_white_and_ends_darker_than_the_base(self):
        base = colors.tol_vibrant.red
        ramp = cmap.from_base(base)
        assert to_hex(ramp(0.0)) == "#ffffff"
        assert _luminance(ramp(1.0)) < _luminance(base)

    def test_passes_through_the_base_colour(self):
        base = colors.tol_vibrant.blue
        ramp = cmap.from_base(base)
        sampled = [to_hex(ramp(x / 100)) for x in range(101)]
        assert base.lower() in sampled

    def test_light_end_is_configurable(self):
        ramp = cmap.from_base("#CC3311", light="#F7F7F7")
        assert to_hex(ramp(0.0)) == "#f7f7f7"

    def test_dark_zero_stops_at_the_base(self):
        ramp = cmap.from_base("#CC3311", dark=0)
        assert to_hex(ramp(1.0)) == "#cc3311"

    @pytest.mark.parametrize("dark", [-0.1, 1.0, 2.0])
    def test_rejects_an_out_of_range_dark(self, dark):
        with pytest.raises(ValueError, match="dark"):
            cmap.from_base("#CC3311", dark=dark)

    def test_is_monotone_in_luminance(self):
        """A non-monotone sequential map misreads as two conditions."""
        levels = [
            _luminance(cmap.from_base("#0077BB")(x)) for x in np.linspace(0, 1, 32)
        ]
        assert levels == sorted(levels, reverse=True)


class TestDiscreteRainbow:
    @pytest.mark.parametrize("n", range(1, 24))
    def test_every_size_tol_defines(self, n):
        built = cmap.discrete_rainbow(n)
        assert built.N == n
        assert len(set(built.colors)) == n

    def test_is_not_a_subsample_of_one_palette(self):
        """Tol gives a different subset per size, so sizes are not nested."""
        assert cmap.discrete_rainbow(3).colors != cmap.discrete_rainbow(4).colors[:3]

    @pytest.mark.parametrize("n", [0, 24, -1])
    def test_rejects_a_size_tol_does_not_define(self, n):
        """Raise, not clamp: a silent clamp hands a figure fewer colours than it
        has categories."""
        with pytest.raises(ValueError, match="1 to 23"):
            cmap.discrete_rainbow(n)

    def test_does_not_shadow_matplotlibs_rainbow(self):
        assert cmap.get("rainbow").name == "rainbow"
        assert callable(cmap.discrete_rainbow)


def _luminance(color) -> float:
    red, green, blue = matplotlib.colors.to_rgb(color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue
