#!/usr/bin/env python

"""Setup script for SpiffyPlots.

As this package only distributes matplotlib style sheets so far,
the setup simply copies the *.mplstyle files into the appropriate directory.

This code is based on a StackOverflow answer:
https://stackoverflow.com/questions/31559225/how-to-ship-or-distribute-a-matplotlib-stylesheet

"""

import atexit
import glob
import os
import shutil
import matplotlib

from setuptools import setup
from setuptools.command.install import install

# Get description from README
root = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

# Install requirements
requirements = ["matplotlib", "wheel", "numpy"]

# Test suite requirements
test_requirements = ["coverage", "pytest", "pytest-cov"]

# Setup requirements
setup_requirements = ["matplotlib", "wheel", "pytest-runner"]

extras = {
    "test": test_requirements,
}


def install_styles():
    # Find all style files
    stylefiles = glob.glob("styles/**/*.mplstyle", recursive=True)

    # Find stylelib directory (where the *.mplstyle files go)
    mpl_stylelib_dir = os.path.join(matplotlib.get_configdir(), "stylelib")
    if not os.path.exists(mpl_stylelib_dir):
        os.makedirs(mpl_stylelib_dir)

    # Copy files over
    print("Installing styles into", mpl_stylelib_dir)
    for stylefile in stylefiles:
        print(os.path.basename(stylefile))
        shutil.copy(
            stylefile, os.path.join(mpl_stylelib_dir, os.path.basename(stylefile))
        )


class PostInstallMoveFile(install):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        atexit.register(install_styles)


setup(
    name="spiffyplots",
    url="https://github.com/JRBCH/spiffyplots",
    version="0.4.2",
    author="Julian Rossbroich",
    author_email="julian.rossbroich@fmi.ch",
    license="GPL-3",
    description=(
        "A collection of matplotlib style sheets and plotting tools for"
        " publication-ready figures"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["spiffyplots"],
    package_data={"spiffyplots": ["styles/*"]},
    include_package_data=True,
    test_suite="tests",
    install_requires=requirements,
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    extras_require=extras,
    cmdclass={"install": PostInstallMoveFile},
)
