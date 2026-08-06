"""Tests for `spiffyplots.colors`.

Colour values are checked against the upstream tables by hand, not against a
copy of what the code produced, so a transcription slip fails here.
"""

import matplotlib.pyplot as plt
import pytest
from matplotlib.colors import to_rgb

from spiffyplots import cmap, colors

# transcribed by hand from https://sronpersonalpages.nl/~pault/.
UPSTREAM = {
    "tol_bright": {"blue": "#4477AA", "red": "#EE6677", "grey": "#BBBBBB"},
    "tol_high_contrast": {"blue": "#004488", "yellow": "#DDAA33", "red": "#BB5566"},
    "tol_vibrant": {"orange": "#EE7733", "blue": "#0077BB", "teal": "#009988"},
    "tol_muted": {"rose": "#CC6677", "indigo": "#332288", "purple": "#AA4499"},
    "tol_medium_contrast": {"light_blue": "#6699CC", "dark_red": "#994455"},
    "tol_light": {"light_blue": "#77AADD", "olive": "#AAAA00"},
    "tol_pale": {"pale_blue": "#BBCCEE", "pale_grey": "#DDDDDD"},
    "tol_dark": {"dark_blue": "#222255", "dark_grey": "#555555"},
    "okabe_ito": {"orange": "#E69F00", "vermillion": "#D55E00", "black": "#000000"},
}

SCHEMES = sorted(UPSTREAM)

EXPECTED_LENGTHS = {
    "tol_bright": 8,
    "tol_high_contrast": 4,
    "tol_vibrant": 8,
    "tol_muted": 11,
    "tol_medium_contrast": 7,
    "tol_light": 10,
    "tol_pale": 7,
    "tol_dark": 7,
    "okabe_ito": 8,
}

# Every scheme that has a grey ends black, grey. high-contrast and
# medium-contrast have none, so they just end on black.
EXPECTED_TAILS = {
    "tol_bright": ("black", "grey"),
    "tol_high_contrast": ("black",),
    "tol_vibrant": ("black", "grey"),
    "tol_muted": ("black", "pale_grey"),
    "tol_medium_contrast": ("black",),
    "tol_light": ("black", "pale_grey"),
    "tol_pale": ("black", "pale_grey"),
    "tol_dark": ("black", "dark_grey"),
    "okabe_ito": ("black",),
}


@pytest.mark.parametrize("scheme", SCHEMES)
def test_hex_values_match_upstream(scheme):
    """Named colours carry the values their authors published."""
    colorset = getattr(colors, scheme)
    for name, expected in UPSTREAM[scheme].items():
        assert getattr(colorset, name) == expected


@pytest.mark.parametrize("scheme", SCHEMES)
def test_scheme_length(scheme):
    assert len(getattr(colors, scheme)) == EXPECTED_LENGTHS[scheme]


@pytest.mark.parametrize("scheme", SCHEMES)
def test_neutrals_come_last(scheme):
    """Black second to last, grey last, so the real colours come first."""
    colorset = getattr(colors, scheme)
    tail = EXPECTED_TAILS[scheme]
    assert colorset.names[-len(tail) :] == tail
    assert colorset[-len(tail)] == "#000000"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_colours_are_valid_and_distinct(scheme):
    """No duplicates, and every value parses as a colour."""
    colorset = getattr(colors, scheme)
    assert len(set(colorset)) == len(colorset)
    for color in colorset:
        to_rgb(color)


@pytest.mark.parametrize("scheme", SCHEMES)
def test_black_appears_once(scheme):
    """Tol appends black to some schemes and pale/dark list none; either way
    the ordering must not drop it or double it."""
    assert list(getattr(colors, scheme)).count("#000000") == 1


@pytest.mark.parametrize("scheme", SCHEMES)
def test_order_follows_the_authors_recommendation(scheme):
    """Paul Tol's recommended order for each scheme.
    I usually stick to this, except in the vibrant case, where `spiffyplots`
    changes the order."""
    recommended = {
        "tol_bright": ("blue", "red", "green", "yellow", "cyan", "purple"),
        "tol_high_contrast": ("blue", "yellow", "red"),
        "tol_vibrant": ("blue", "red", "teal", "cyan", "orange", "magenta"),
        "tol_muted": (
            "rose", "indigo", "sand", "green", "cyan", "wine", "teal", "olive",
            "purple",
        ),
        "tol_medium_contrast": (
            "light_blue", "dark_blue", "light_yellow", "dark_red", "dark_yellow",
            "light_red",
        ),
        "tol_light": (
            "light_blue", "orange", "light_yellow", "pink", "light_cyan", "mint",
            "pear", "olive",
        ),
        "tol_pale": (
            "pale_blue", "pale_red", "pale_green", "pale_yellow", "pale_cyan",
        ),
        "tol_dark": (
            "dark_blue", "dark_red", "dark_green", "dark_yellow", "dark_cyan",
        ),
        "okabe_ito": (
            "orange", "sky_blue", "bluish_green", "yellow", "blue", "vermillion",
            "reddish_purple",
        ),
    }[scheme]  # fmt: skip
    head = len(recommended)
    assert getattr(colors, scheme).names[:head] == recommended


def test_spiffy_cycle_is_vibrant():
    assert colors.SPIFFY_CYCLE is colors.tol_vibrant


class TestColorSet:
    def test_is_a_tuple(self):
        assert isinstance(colors.tol_bright, tuple)
        assert colors.tol_bright[1] == colors.tol_bright.red

    def test_slicing_preserves_names(self):
        subset = colors.tol_muted[:3]
        assert isinstance(subset, colors.ColorSet)
        assert subset.names == ("rose", "indigo", "sand")
        assert subset.rose == colors.tol_muted.rose

    def test_pick_reorders(self):
        picked = colors.tol_vibrant.pick("red", "blue")
        assert list(picked) == [colors.tol_vibrant.red, colors.tol_vibrant.blue]
        assert picked.names == ("red", "blue")

    def test_pick_rejects_unknown_names(self):
        with pytest.raises(KeyError, match="chartreuse"):
            colors.tol_vibrant.pick("blue", "chartreuse")

    def test_unknown_attribute_lists_what_is_available(self):
        with pytest.raises(AttributeError, match="magenta"):
            _ = colors.tol_vibrant.chartreuse

    def test_cycler_feeds_prop_cycle(self):
        with plt.rc_context({"axes.prop_cycle": colors.tol_muted.cycler()}):
            assert plt.rcParams["axes.prop_cycle"].by_key()["color"] == list(
                colors.tol_muted
            )

    def test_repr_round_trips_the_names(self):
        assert repr(colors.tol_high_contrast) == (
            "ColorSet('tol_high_contrast', blue='#004488', "
            "yellow='#DDAA33', red='#BB5566', black='#000000')"
        )


class TestFromCmap:
    def test_returns_n_distinct_colours(self):
        sampled = colors.from_cmap(cmap.sequential, 6)
        assert len(sampled) == 6
        assert len(set(sampled)) == 6

    def test_spans_the_full_range_by_default(self):
        first, *_, last = colors.from_cmap(cmap.sequential, 5)
        assert to_rgb(first) == pytest.approx(cmap.sequential(0.0)[:3], abs=1 / 255)
        assert to_rgb(last) == pytest.approx(cmap.sequential(1.0)[:3], abs=1 / 255)

    def test_lo_and_hi_trim_the_ends(self):
        trimmed = colors.from_cmap(cmap.sequential, 4, lo=0.3, hi=0.7)
        assert to_rgb(trimmed[0]) == pytest.approx(
            cmap.sequential(0.3)[:3], abs=1 / 255
        )
        assert to_rgb(trimmed[-1]) == pytest.approx(
            cmap.sequential(0.7)[:3], abs=1 / 255
        )

    def test_single_colour_takes_the_midpoint(self):
        assert colors.from_cmap(cmap.sequential, 1) == colors.from_cmap(
            cmap.sequential, 1, lo=0.5, hi=0.5000001
        )

    def test_accepts_a_colormap_name(self):
        assert colors.from_cmap("viridis", 3) == colors.from_cmap(
            cmap.get("viridis"), 3
        )

    @pytest.mark.parametrize(
        "kwargs",
        [{"lo": -0.1}, {"hi": 1.1}, {"lo": 0.8, "hi": 0.2}, {"lo": 0.5, "hi": 0.5}],
    )
    def test_rejects_a_bad_range(self, kwargs):
        with pytest.raises(ValueError, match="lo"):
            colors.from_cmap(cmap.sequential, 3, **kwargs)

    def test_rejects_n_below_one(self):
        with pytest.raises(ValueError, match="at least one"):
            colors.from_cmap(cmap.sequential, 0)


class TestShades:
    def test_darkens_monotonically(self):
        """A sweep only reads as a sweep if the shades order by luminance."""
        luminances = [_luminance(shade) for shade in colors.shades("#0077BB", 6)]
        assert luminances == sorted(luminances, reverse=True)

    def test_skips_the_invisible_light_end(self):
        """The lightest shade still has to read as a line against white."""
        assert _luminance(colors.shades("#0077BB", 5)[0]) < 0.95

    def test_shades_are_distinct(self):
        shades = colors.shades("#CC3311", 8)
        assert len(set(shades)) == 8


def _luminance(color) -> float:
    red, green, blue = to_rgb(color)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue
