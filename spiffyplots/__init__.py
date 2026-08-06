"""Top-level package for SpiffyPlots."""

from pathlib import Path

import matplotlib
import matplotlib.style

from . import cmap, colors
from ._units import CM, MM, figsize
from .lineplots import multiline
from .multipanel import MultiPanel
from .panels import label_panels
from .random_data import populate_random_data

__author__ = """Julian Rossbroich"""
__email__ = "julian.rossbroich@tum.de"
__version__ = "0.6.1"

STYLES_PATH = Path(__file__).parent / "styles"

# easy aliases for the most common schemes, so you can do `plt.style.use("bright")`
STYLE_ALIASES = {
    "bright": "tol-bright",
    "muted": "tol-muted",
    "vibrant": "tol-vibrant",
}

__all__ = [
    "CM",
    "MM",
    "STYLES_PATH",
    "STYLE_ALIASES",
    "MultiPanel",
    "cmap",
    "colors",
    "figsize",
    "label_panels",
    "multiline",
    "populate_random_data",
]


def _register_styles() -> dict:
    """Add the bundled style sheets to matplotlib's style library.

    Styles register under their bare filename, so nested folders such as
    ``styles/color`` are flattened: ``plt.style.use("tol-muted")``, not
    ``plt.style.use("color/tol-muted")``. The names in :data:`STYLE_ALIASES` are
    then registered a second time as aliases.

    Goes through ``matplotlib.style`` rather than ``matplotlib.pyplot`` so
    registration does not itself require a backend. Importing this package
    still pulls in pyplot via :class:`~spiffyplots.multipanel.MultiPanel`.

    """
    sheets = {
        path.stem: matplotlib.rc_params_from_file(path, use_default_template=False)
        for path in sorted(STYLES_PATH.rglob("*.mplstyle"))
    }
    sheets.update({alias: sheets[target] for alias, target in STYLE_ALIASES.items()})
    matplotlib.style.library.update(sheets)
    matplotlib.style.available[:] = sorted(matplotlib.style.library)
    return sheets


_register_styles()
