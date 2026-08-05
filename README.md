# SpiffyPlots

[![Tests](https://github.com/JRBCH/spiffyplots/actions/workflows/test.yaml/badge.svg)](https://github.com/JRBCH/spiffyplots/actions/workflows/test.yaml)
[![Documentation Status](https://readthedocs.org/projects/spiffyplots/badge/?version=latest)](https://spiffyplots.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/spiffyplots.svg)](https://badge.fury.io/py/spiffyplots)
[![GitHub last commit](https://img.shields.io/github/last-commit/JRBCH/spiffyplots.svg?style=flat)]()
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

A collection of matplotlib style sheets and plotting tools for publication-ready figures.

Requires Python 3.10 or newer and Matplotlib 3.8 or newer.

* Free software: GPL-3 license
* Documentation: https://spiffyplots.readthedocs.io.

#### Simple style example:
![style example](examples/multipanel_spiffy.png)

## Installation

Install the latest release:

`pip install spiffyplots`

or install the latest commit directly from GitHub:

`pip install git+https://github.com/JRBCH/spiffyplots.git`

For local development, install `uv` and run:

```console
uv sync
uv run ruff check .
uv run pytest
```

## Using the style sheets

The style sheets ship inside the package and register themselves with
matplotlib when `spiffyplots` is imported:

```python
import spiffyplots  # registers the styles
import matplotlib.pyplot as plt

plt.style.use("spiffy")  # base style
plt.style.use(["spiffy", "muted"])  # base style plus a Paul Tol color scheme
```

Import `spiffyplots` **before** calling `plt.style.use`. If you would rather
not depend on import order, the same sheets are reachable by their
package-relative name, which needs no import at all:

```python
plt.style.use("spiffyplots.styles.spiffy")
```

Available styles: `spiffy`, the color schemes `bright`, `high-vis`, `muted`,
`retro` and `vibrant`, and the modifiers `latex`, `minor-ticks`, `right-axis`,
`top-axis` and `heatmap`.

The base `spiffy` style keeps vector text publication-ready and editable. PDF
and PostScript output embeds TrueType fonts rather than Type 3 fonts, while SVG
output retains `<text>` elements instead of converting glyphs to paths.

If for some reason you want to restore
Matplotlib's default outlined SVG behavior, set `plt.rcParams["svg.fonttype"] = "path"`.

## Features

* Matplotlib style sheets
    * General style sheets for quick and beautiful out-of-the-box plotting
    * Color style sheets for [Paul Tol's color schemes](https://personal.sron.nl/~pault/)

* Multi-panel figures
    * Easy and flexible wrapper of matplotlib's GridSpec
    * Automatic labelling of sub-panels
    * Support for custom panel arrangements and labels
    * Figure sizes in inches, centimetres or millimetres

## Roadmap

* Named access to the bundled color palettes and helpers for ramps and
  colormaps
* Verified journal-specific figure sizes and style sheets

## Credits

 * This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

 * The idea for easy-to-use and pypi-deployable matplotlib stylesheets stems from John Garrett's
 [SciencePlots](https://github.com/garrettj403/SciencePlots) package.
