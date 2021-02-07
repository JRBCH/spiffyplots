import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from typing import Dict, Tuple, Union, Optional, Iterable


def multiline(x: Iterable, y: Iterable, c: Iterable, axis=None, **kwargs):
    """
    Plot multiple lines color-coded with a colormap

    Args:
        x: Iterable of X coordinates
        y: Iterable of Y coordinates
        c: Iterable of CMAP values
        axis: matplotlib axis object

    Notes:
        len(xs) == len(ys) == len(c) is the number of line segments
        len(xs[i]) == len(ys[i]) is the number of points for each line (indexed by i)

    Returns
    -------
    lc : instance of matplotlib LineCollection object.
    """

    # Find axis if not defined
    if axis is None:
        axis = plt.gca()

    # Make a LineCollection Object
    segments = [np.column_stack([x, y]) for x, y in zip(xs, ys)]
    lc = LineCollection(segments, **kwargs)

    # set coloring of line segments
    #    Note: I get an error if I pass c as a list here... not sure why.
    lc.set_array(np.asarray(c))

    # add lines to axes and rescale
    #    Note: adding a collection doesn't autoscalee xlim/ylim
    ax.add_collection(lc)
    ax.autoscale()
    return lc
