"""Top-level package for SpiffyPlots."""

from pathlib import Path

import matplotlib
import matplotlib.style

from . import cmap, colors
from ._units import CM, MM, figsize
from .lineplots import multiline
from .multipanel import MultiPanel
from .random_data import populate_random_data

__author__ = """Julian Rossbroich"""
__email__ = "julian.rossbroich@tum.de"
__version__ = "0.6.1"

STYLES_PATH = Path(__file__).parent / "styles"

__all__ = [
    "CM",
    "MM",
    "STYLES_PATH",
    "MultiPanel",
    "cmap",
    "colors",
    "figsize",
    "multiline",
    "populate_random_data",
]


def _register_styles() -> dict:
    """Add the bundled style sheets to matplotlib's style library.

    Styles register under their bare filename, so nested folders such as
    ``styles/color`` are flattened: ``plt.style.use("muted")``, not
    ``plt.style.use("color/muted")``.

    Goes through ``matplotlib.style`` rather than ``matplotlib.pyplot`` so
    registration does not itself require a backend. Importing this package
    still pulls in pyplot via :class:`~spiffyplots.multipanel.MultiPanel`.

    """
    sheets = {
        path.stem: matplotlib.rc_params_from_file(path, use_default_template=False)
        for path in sorted(STYLES_PATH.rglob("*.mplstyle"))
    }
    matplotlib.style.library.update(sheets)
    matplotlib.style.available[:] = sorted(matplotlib.style.library)
    return sheets


_register_styles()
