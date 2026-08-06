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
import spiffyplots  # registers the styles and colormaps
import matplotlib.pyplot as plt

plt.style.use("spiffy")  # base style
plt.style.use(["spiffy", "tol-muted"])  # base style plus a color scheme
```

Import `spiffyplots` **before** calling `plt.style.use`. The base style names a
colormap that this package registers, and a style sheet naming an unregistered
colormap applies silently and then fails at draw time.

Available styles:

| | |
|---|---|
| base | `spiffy` |
| color | `tol-bright`, `tol-high-contrast`, `tol-light`, `tol-medium-contrast`, `tol-muted`, `tol-vibrant`, `okabe-ito` |
| modifiers | `latex`, `minor-ticks`, `right-axis`, `top-axis` |

The base `spiffy` style keeps vector text editable. PDF
and PostScript embeds TrueType fonts, and SVG retains `<text>` elements instead of converting glyphs to paths.

If for some reason you want to restore
Matplotlib's default outlined SVG behavior, set `plt.rcParams["svg.fonttype"] = "path"`.

## Colors and colormaps

Style sheets only set the default cycle. For the colors themselves, use
`spiffyplots.colors` for discrete colors and `spiffyplots.cmap` for colormaps.

```python
import spiffyplots as spiffy

scheme = spiffy.colors.tol_vibrant
color_exc = scheme.red  # '#CC3311'
color_inh = scheme.blue  # '#0077BB'

spiffy.colors.from_cmap(spiffy.cmap.sequential, 6)  # 6 equally spaced colors
spiffy.colors.shades(color_exc, 5)  # 5 shades of one base color
```

Schemes: `tol_bright`, `tol_high_contrast`, `tol_vibrant`, `tol_muted`,
`tol_medium_contrast`, `tol_light`, `tol_pale`, `tol_dark` and `okabe_ito`.
Each is a tuple you can index, slice and iterate, whose colors are also
reachable by name. Each runs in its author's recommended order, then black,
then grey.

```python
cmap = spiffy.cmap.sequential  # Paul Tol's iridescent
cmap = spiffy.cmap.diverging  # Paul Tol's nightfall
cmap = spiffy.cmap.iridescent_r  # any of Tol's, by short name
cmap = spiffy.cmap.viridis  # falls through to matplotlib
cmap = spiffy.cmap.batlow  # falls through to cmcrameri
cmap = spiffy.cmap.kbc  # falls through to colorcet

cmap = spiffy.cmap.from_base(color_exc)  # white -> color -> darker
cmap = spiffy.cmap.from_colors(spiffy.colors.tol_muted)
cmap = spiffy.cmap.discrete_rainbow(8)
```

### Perceptually uniform colormaps
[cmcrameri](https://github.com/callumrollo/cmcrameri) and
[colorcet](https://github.com/holoviz/colorcet) do that very well, and
`spiffy.cmap` reaches their colormaps too once either is installed.
To install them together with `spiffyplots`:

```console
pip install "spiffyplots[colormaps]"
```


```python
import spiffyplots as spiffy

cmap = spiffy.cmap.batlow  # cmcrameri, registered as `cmc.batlow`
cmap = spiffy.cmap.kbc  # colorcet, registered as `cet_kbc`
```


* Matplotlib style sheets
    * General style sheets for quick and beautiful out-of-the-box plotting
    * Color style sheets for [Paul Tol's color schemes](https://sronpersonalpages.nl/~pault/)
      and [Okabe-Ito](https://jfly.uni-koeln.de/color/), all color-blind safe

* Colors
    * Easy access to colors and colormaps
    * Ramps and shades derived from one base color, e.g. for heatmaps

* Multi-panel figures
    * Easy and flexible wrapper of matplotlib's GridSpec
    * Automatic labelling of sub-panels
    * Support for custom panel arrangements and labels
    * Figure sizes in inches, centimetres or millimetres

## Credits

 * This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

 * Most color schemes are [Paul Tol's](https://sronpersonalpages.nl/~pault/),
 redistributed under the 3-clause BSD license
