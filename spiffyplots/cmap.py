"""Colormaps by attribute access.

Returns colormaps. :mod:`spiffyplots.colors` returns discrete colours.

``cmap.<name>`` resolves in order: the aliases ``sequential`` and ``diverging``,
then Tol's maps by short name, then matplotlib's registry, then ``cmcrameri``
and ``colorcet`` if installed. A trailing ``_r`` reverses.

Matplotlib wins bare-name ties on purpose: ``cmap.gray`` is matplotlib's gray,
not colorcet's. Use the qualified name for the other one, ``cmap.cet_gray``, or
``cmap.get("cmc.batlow")`` for cmcrameri, whose ``cmc.`` prefix has a dot in it
and so cannot be an attribute.

Tol's maps register as ``tol.<name>``, so they also work as strings:
``ax.imshow(data, cmap="tol.nightfall")``. The prefix is not optional; Tol's
``YlOrBr`` and ``PRGn`` differ from matplotlib's builtins of the same name, and
matplotlib will not let you re-register a builtin.

    >>> import spiffyplots as spiffy
    >>> spiffy.cmap.sequential.name
    'tol.iridescent'
    >>> spiffy.cmap.diverging_r.name
    'tol.nightfall_r'
    >>> spiffy.cmap.viridis.name
    'viridis'
"""

import importlib

import matplotlib
from matplotlib.colors import (
    Colormap,
    LinearSegmentedColormap,
    ListedColormap,
    to_hex,
    to_rgb,
)

from . import _tol_data

__all__ = ["discrete_rainbow", "from_base", "from_colors", "get"]

#: Prefix Tol's colormaps register under.
PREFIX = "tol."

#: Semantic names for the house defaults.
ALIASES = {"sequential": "iridescent", "diverging": "nightfall"}

# Optional companions, and the prefix each uses in matplotlib's registry.
_COMPANIONS = {"cmcrameri": "cmc.{}", "colorcet": "cet_{}"}

_companion_available: dict[str, bool] = {}


def _register() -> list[str]:
    """Register Tol's colormaps, forward and reversed.

    Unregisters first so a reload stays quiet: ``register(force=True)`` warns
    about overwriting.
    """
    registered = []
    for name, entry in _tol_data.CMAPS.items():
        cmap = LinearSegmentedColormap.from_list(PREFIX + name, entry["colors"])
        # with_extremes, not set_bad: 3.11 marks set_bad for deprecation.
        cmap = cmap.with_extremes(bad=entry["bad"])
        for variant in (cmap, cmap.reversed(name=f"{PREFIX}{name}_r")):
            if variant.name in matplotlib.colormaps:
                matplotlib.colormaps.unregister(variant.name)
            matplotlib.colormaps.register(variant, name=variant.name)
            registered.append(variant.name)
    return registered


def _companion(module: str) -> bool:
    """Import an optional colormap package once; is it there?"""
    if module not in _companion_available:
        try:
            importlib.import_module(module)
        except ImportError:
            _companion_available[module] = False
        else:
            _companion_available[module] = True
    return _companion_available[module]


def get(name: str | Colormap) -> Colormap:
    """Return a colormap by name, for when the name is in a variable.

    A ``Colormap`` passes straight through, so this doubles as a coercion
    helper. Raises ``KeyError`` if the name resolves nowhere.

    >>> from spiffyplots import cmap
    >>> cmap.get("iridescent").name
    'tol.iridescent'
    >>> cmap.get("YlOrBr").name
    'tol.YlOrBr'
    """
    if isinstance(name, Colormap):
        return name

    stem, suffix = (name[:-2], "_r") if name.endswith("_r") else (name, "")
    stem = ALIASES.get(stem, stem)

    for candidate in (f"{PREFIX}{stem}{suffix}", name):
        if candidate in matplotlib.colormaps:
            return matplotlib.colormaps[candidate]

    missing = []
    for module, template in _COMPANIONS.items():
        if not _companion(module):
            missing.append(module)
            continue
        for candidate in (template.format(stem) + suffix, name):
            if candidate in matplotlib.colormaps:
                return matplotlib.colormaps[candidate]

    detail = f"Looked in spiffyplots' {PREFIX}* schemes and matplotlib's registry"
    if missing:
        detail += (
            f"; {' and '.join(missing)} are not installed"
            ' (pip install "spiffyplots[colormaps]")'
        )
    raise KeyError(f"No colormap named {name!r}. {detail}.")


def from_colors(colors, *, name: str | None = None, discrete: bool = False) -> Colormap:
    """Build a colormap from two or more colours. A ColorSet works directly.

    ``discrete=True`` steps instead of interpolating, one flat band per colour.
    The other direction is :func:`spiffyplots.colors.from_cmap`.

    >>> from spiffyplots import cmap, colors
    >>> cmap.from_colors(colors.tol_muted, discrete=True).N
    11
    """
    colors = list(colors)
    if len(colors) < 2:
        raise ValueError(
            f"Need at least two colours to build a colormap, got {len(colors)}."
        )
    name = name or "spiffy_from_colors"
    if discrete:
        return ListedColormap(colors, name=name)
    return LinearSegmentedColormap.from_list(name, colors)


def from_base(
    color,
    *,
    light: str = "#FFFFFF",
    dark: float = 0.35,
    name: str | None = None,
) -> Colormap:
    """A sequential colormap ramping white -> base colour -> darker.

    For a one-condition-vs-baseline heatmap: shade it in the colour that
    condition already has in the line plots, so there is only one colour code to
    read. ``dark`` is how far past the base colour to go, toward black.

    >>> from spiffyplots import cmap, colors
    >>> from matplotlib.colors import to_hex
    >>> to_hex(cmap.from_base(colors.tol_vibrant.red)(0.0))
    '#ffffff'
    """
    if not 0 <= dark < 1:
        raise ValueError(f"dark must be in [0, 1), got {dark!r}.")
    stops = [light, color] if dark == 0 else [light, color, _darken(color, dark)]
    return from_colors(stops, name=name or f"spiffy_{to_hex(color).lstrip('#')}")


def discrete_rainbow(n: int = 22, *, name: str | None = None) -> ListedColormap:
    """Tol's discrete rainbow with ``n`` colours, 1 to 23.

    Tol specifies a different subset for every ``n``, so the sizes are not
    nested. Raises rather than clamping the way his code does, which would
    quietly hand a figure fewer colours than it has categories.

    Not called ``rainbow``, so it does not shadow matplotlib's colormap of that
    name (still there as ``cmap.get("rainbow")``).

    >>> from spiffyplots import cmap
    >>> cmap.discrete_rainbow(3).colors
    ['#1965B0', '#F7F056', '#DC050C']
    """
    if not 1 <= n <= 23:
        raise ValueError(
            f"Tol's discrete rainbow is defined for 1 to 23 colours, got {n}."
        )
    colors = [_tol_data.RAINBOW_COLORS[i] for i in _tol_data.RAINBOW_INDEXES[n - 1]]
    cmap = ListedColormap(colors, name=name or f"{PREFIX}rainbow{n}")
    bad = _tol_data.RAINBOW_BAD_MAX if n == 23 else _tol_data.RAINBOW_BAD
    return cmap.with_extremes(bad=bad)


def _darken(color, amount: float) -> tuple[float, float, float]:
    """Scale toward black. Monotone in luminance, unlike an HSV shift."""
    factor = 1.0 - amount
    return tuple(channel * factor for channel in to_rgb(color))


def __getattr__(name: str) -> Colormap:
    """Resolve ``cmap.<name>`` through :func:`get`."""
    if name.startswith("_"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        return get(name)
    except KeyError as error:
        # str(KeyError) is the repr of its argument, which double-quotes the
        # message. The argument itself is the sentence we want.
        raise AttributeError(error.args[0]) from None


def __dir__() -> list[str]:
    """Offer resolvable names to tab completion."""
    short = {
        name.removeprefix(PREFIX)
        for name in matplotlib.colormaps
        if name.startswith(PREFIX)
    }
    return sorted({*globals(), *ALIASES, *short, *matplotlib.colormaps})


#: Names registered with matplotlib when this module is imported.
REGISTERED = _register()
