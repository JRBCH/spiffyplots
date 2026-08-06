"""Colors and color palettes.

Returns discrete colours. :mod:`spiffyplots.cmap` returns colormaps.

Schemes are Paul Tol's plus Okabe-Ito, all colour-blind safe. Each one runs in
its author's recommended order, then black, then grey, so the real colours come
first and the neutrals are there if you run out. The colour style sheets are
generated from these constants.

    >>> from spiffyplots import colors
    >>> colors.tol_vibrant.blue
    '#0077BB'
    >>> colors.tol_vibrant[:2]
    ColorSet('tol_vibrant', blue='#0077BB', red='#CC3311')
"""

import matplotlib
from matplotlib.colors import to_hex

from . import _tol_data, cmap

__all__ = [
    "SPIFFY_CYCLE",
    "ColorSet",
    "from_cmap",
    "okabe_ito",
    "shades",
    "tol_bright",
    "tol_dark",
    "tol_high_contrast",
    "tol_light",
    "tol_medium_contrast",
    "tol_muted",
    "tol_pale",
    "tol_vibrant",
]

BLACK = "#000000"


class ColorSet(tuple):
    """A tuple of colours whose entries also have names.

    >>> from spiffyplots import colors
    >>> colors.tol_bright.cyan
    '#66CCEE'
    >>> colors.tol_bright[:2]
    ColorSet('tol_bright', blue='#4477AA', red='#EE6677')
    """

    def __new__(cls, name, colors):
        mapping = dict(colors)
        instance = super().__new__(cls, mapping.values())
        instance._name = name
        instance._names = tuple(mapping)
        return instance

    @property
    def names(self) -> tuple[str, ...]:
        """The colour names, in order."""
        return self._names

    def pick(self, *names: str) -> "ColorSet":
        """Return a new set with just these colours, in this order.

        >>> from spiffyplots import colors
        >>> colors.tol_bright.pick("red", "blue")
        ColorSet('tol_bright', red='#EE6677', blue='#4477AA')
        """
        unknown = [name for name in names if name not in self._names]
        if unknown:
            raise KeyError(
                f"{self._name} has no {', '.join(map(repr, unknown))}. "
                f"Available: {', '.join(self._names)}."
            )
        return ColorSet(self._name, {name: getattr(self, name) for name in names})

    def cycler(self):
        """A cycler for ``axes.prop_cycle``."""
        return matplotlib.cycler("color", list(self))

    def __getitem__(self, key):
        if isinstance(key, slice):
            return ColorSet(self._name, dict(zip(self._names[key], tuple(self)[key])))
        return super().__getitem__(key)

    def __getattr__(self, key: str) -> str:
        # Guard privates, or a lookup arriving before __new__ finishes recurses
        # through _names forever.
        if key.startswith("_"):
            raise AttributeError(key)
        if key in self._names:
            return self[self._names.index(key)]
        raise AttributeError(
            f"{self._name} has no {key!r}. Available: {', '.join(self._names)}."
        )

    def __repr__(self) -> str:
        pairs = ", ".join(f"{n}={c!r}" for n, c in zip(self._names, self))
        return f"ColorSet({self._name!r}, {pairs})"


# Cycle order per scheme: Tol's recommended order, then black, then grey.
# Vibrant is the exception and uses spiffy's order, since it is the base cycle.
_ORDER = {
    "bright": ("blue", "red", "green", "yellow", "cyan", "purple", "black", "grey"),
    "high_contrast": ("blue", "yellow", "red", "black"),
    "vibrant": ("blue", "red", "teal", "cyan", "orange", "magenta", "black", "grey"),
    "muted": (
        "rose", "indigo", "sand", "green", "cyan", "wine", "teal", "olive",
        "purple", "black", "pale_grey",
    ),
    "medium_contrast": (
        "light_blue", "dark_blue", "light_yellow", "dark_red", "dark_yellow",
        "light_red", "black",
    ),
    "light": (
        "light_blue", "orange", "light_yellow", "pink", "light_cyan", "mint",
        "pear", "olive", "black", "pale_grey",
    ),
    "pale": (
        "pale_blue", "pale_red", "pale_green", "pale_yellow", "pale_cyan",
        "black", "pale_grey",
    ),
    "dark": (
        "dark_blue", "dark_red", "dark_green", "dark_yellow", "dark_cyan",
        "black", "dark_grey",
    ),
}  # fmt: skip


def _tol(name: str) -> ColorSet:
    table = dict(_tol_data.CSETS[name])
    table.setdefault("black", BLACK)  # pale and dark do not list it
    return ColorSet(f"tol_{name}", {key: table[key] for key in _ORDER[name]})


#: Tol bright, 8 colours.
tol_bright = _tol("bright")

#: Tol high-contrast, 4 colours. Best for two- and three-condition comparisons.
tol_high_contrast = _tol("high_contrast")

#: Tol vibrant, 8 colours. The base cycle.
tol_vibrant = _tol("vibrant")

#: Tol muted, 11 colours. The largest qualitative scheme here.
tol_muted = _tol("muted")

#: Tol medium-contrast, 7 colours in light/dark pairs that survive monochrome
#: printing. Good for before/after.
tol_medium_contrast = _tol("medium_contrast")

#: Tol light, 10 colours for fills and shaded bands.
tol_light = _tol("light")

#: Tol pale, 7 colours light enough to sit behind black text.
tol_pale = _tol("pale")

#: Tol dark, 7 colours dark enough to sit behind white text.
tol_dark = _tol("dark")

#: Okabe-Ito, 8 colours. The standard CVD-safe palette in biology. Matplotlib
#: ships these as a colormap from 3.11 but never as a cycle, and the floor here
#: is 3.8.
okabe_ito = ColorSet(
    "okabe_ito",
    {
        "orange": "#E69F00",
        "sky_blue": "#56B4E9",
        "bluish_green": "#009E73",
        "yellow": "#F0E442",
        "blue": "#0072B2",
        "vermillion": "#D55E00",
        "reddish_purple": "#CC79A7",
        "black": BLACK,
    },
)

#: The spiffy default cycle (Tol's vibrant scheme, re-ordered).
SPIFFY_CYCLE = tol_vibrant


def from_cmap(colormap, n: int, *, lo: float = 0.0, hi: float = 1.0) -> list[str]:
    """Sample ``n`` equally spaced colours from a colormap.

    Args:
        colormap: A colormap, or any name :func:`spiffyplots.cmap.get` resolves.
        n: How many colours. ``n == 1`` takes the midpoint.
        lo: Where to start. Trimming the light end of a sequential map matters:
            a line at ``0.0`` is usually too pale to see.
        hi: Where to stop.

    >>> from spiffyplots import cmap, colors
    >>> colors.from_cmap(cmap.sequential, 3)
    ['#fefbe9', '#81c4e7', '#46353a']
    """
    if n < 1:
        raise ValueError(f"Need at least one colour, got n={n}.")
    if not 0 <= lo < hi <= 1:
        raise ValueError(f"Need 0 <= lo < hi <= 1, got lo={lo!r}, hi={hi!r}.")
    colormap = cmap.get(colormap)
    if n == 1:
        positions = [(lo + hi) / 2]
    else:
        positions = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    return [to_hex(colormap(position)) for position in positions]


def shades(
    color,
    n: int,
    *,
    lo: float = 0.15,
    hi: float = 1.0,
    dark: float = 0.35,
) -> list[str]:
    """``n`` shades of one base colour, light to dark.

    For sweeps: one line per parameter value, all in that parameter's colour.
    Pair it with a colorbar from :func:`spiffyplots.cmap.from_base`.

    Args:
        color: The base colour.
        n: How many shades.
        lo: Where to start in the ramp. The default skips the near-white end.
        hi: Where to stop.
        dark: How far past the base colour to go, as a fraction toward black.

    >>> from spiffyplots import colors
    >>> colors.shades(colors.tol_vibrant.blue, 3)
    ['#b3d6eb', '#0071b1', '#004d7a']
    """
    return from_cmap(cmap.from_base(color, dark=dark), n, lo=lo, hi=hi)
