# SpiffyPlots

[![Build Status](https://travis-ci.com/JRBCH/spiffyplots.svg?token=i92PyxWJ7xxe45sHGGQE&branch=master)](https://travis-ci.com/JRBCH/spiffyplots)
[![codecov](https://codecov.io/gh/JRBCH/spiffyplots/branch/master/graph/badge.svg)](https://codecov.io/gh/JRBCH/spiffyplots)
[![Documentation Status](https://readthedocs.org/projects/spiffyplots/badge/?version=latest)](https://spiffyplots.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/spiffyplots.svg)](https://badge.fury.io/py/spiffyplots)
[![GitHub last commit](https://img.shields.io/github/last-commit/google/skia.svg?style=flat)]()
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

A collection of matplotlib style sheets and plotting tools for publication-ready figures.

* Free software: GPL-3 license
* Documentation: https://spiffyplots.readthedocs.io.

#### Simple style example:
![style example](examples/multipanel_spiffy.png)

## Installation

Install the latest release:

`pip install spiffyplots`

or install the latest commit directly from GitHub:

`pip install git+https://github.com/JRBCH/spiffyplots.git`

## Features

* Matplotlib style sheets
    * General style sheets for quick and beautiful out-of-the-box plotting
    * Color style sheets for [Paul Tol's color schemes](https://personal.sron.nl/~pault/)

* Multi-panel figures
    * Easy and flexible wrapper of matplotlib's GridSpec
    * Automatic labelling of sub-panels
    * Support for custom panel arrangements and labels

## Future Plans

* Journal-specific style sheets
* Automatic optimization of figure size for multipanel figures
* `color` module for quick access to colors and cmaps
* `panel` wrapper class for matplotlib axes objects with custom plotting methods for often used plots.

## Credits

 * This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

 * The idea for easy-to-use and pypi-deployable matplotlib stylesheets stems from John Garrett's
 [SciencePlots](https://github.com/garrettj403/SciencePlots) package.
