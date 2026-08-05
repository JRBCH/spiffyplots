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

from setuptools import setup
from setuptools.command.install import install


def install_styles():
    import matplotlib

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
    cmdclass={"install": PostInstallMoveFile},
)
