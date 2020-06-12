"""
The Spiffy MultiPanel class and its methods
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import numpy as np
import string
import math

from collections import namedtuple
from typing import Dict, Tuple, Union, Optional, Iterable
import warnings


class MultiPanel(object):
    """
    The central object class of the `spiffy` package.
    The MultiPanel object initiates a figure with multiple panels.
    It is build upon matplotlib's GridSpec, but aims to add simplicity and functionality.
    """

    def __init__(
        self,
        shape: Optional[Tuple[int, int]] = (2, 2),
        grid: Union[Iterable[Tuple], Iterable[int]] = None,
        labels: Union[bool, Iterable[str], Dict[str, tuple], np.array] = False,
        **kwargs
    ) -> None:
        # language=rst
        """
        Initializes a MultiPanel figure.

        The ``MultiPanel`` object is basically a wrapper of matplotlib's ``GridSpec``,
        but tries to simplify some aspects of multi-panel figure generation, such as Figure labels
        and the layout of panels. Depending on the input, the layout is initialized in one of three ways:

        **OPTION 1: Initialization based on ``labels``**

        The ``labels`` parameter can be passed in as a dictionary, mapping custom figure labels [e.g. 'A', 'B', 'C']
        to locations in the grid that are defined by Tuples [e.g. {'A': (0, range(2,5)} will make a plot in the
        first row spanning columns 2-4 and give it the label A.

        Similarly, ``labels`` can be passed as a 2-dimensional np.array of strings. In this case, the strings in
        the cells of the array correspond to the label of the panels. Adjacent identical labels are considered
        one panel. For example, the array
        |``[['A', 'A', 'D'],``
        | ``['B', 'C', 'D'],``
        | ``['E', 'E', 'E']]``
        will create 5 panels, each occupying the space that the respective label takes up in the array.

        This option is useful when you want to control both the arrangement of panels, and the order and
        format of their labels. If label is passed in as a dictionary or np.array, the ``grid`` and ``shape``
        parameters are ignored.

        **OPTION 2: INITIALIZATION BASED ON ``grid``**

        If **OPTION 1** does not apply, the class will try to be initialized through the ``grid`` parameter.


        :param shape: Tuple of form ``[rows, columns]`` determining the shape of the MultiPanel matrix

        :param grid: Determines the layout of subplots across the MultiPanel matrix. Defaults to one plot in each
                    cell of the ``shape`` matrix.
                    Can be one of:
                    - Iterable of grid location tuples of form ``[rows, columns]``, in which rows and columns are
                    either int (for a single cell) or Iterable (for spanning multiple cells).
                    - Iterable of ints with length ``shape[0]``, which defines the number of plots in each row.
                    Each plot then has the size ``1 x shape[0]/int``.
                    Attention: ``shape[0]`` must be divisable by every element in ``grid``.

        :param labels: Assigns labels to subplots. Defaults to False.
                    Can be one of:
                    - Boolean. If True, labels are assigned to plots first across rows, then across columns.
                    - Iterable of strings assigning labels to subplots, in the same order as defined by ``grid``.
                    - A Dictionary mapping [str] keys to [Tuple] locations in the grid. This setting overrides the grid.
                    - A np.array of the same shape as ``shape``, mapping string names to the locations in the grid.
                    Figures can span multiple cells in the grid. Also overrides the grid.

        kwargs for SpiffyPlot functions:
        :param label_case: String. 'uppercase' or 'lowercase' - passed into function that
                    generates figure labels.
        :param label_weight: String. Weight of the figure labels. defaults to 'bold'
        :param label_size: Int. Font Size for figure labels. defaults to 14.
        :param label_location: Tuple. Location of the figure labels relative to axis origin.
                    Defaults to (-0.1, 1.1)

        kwargs for matplotlib figure:
        :param figsize: Size of the figure. Will be passed into the matplotlib figure generator.
        :param constrained_layout: Boolean passed into figure generation.

        kwargs for GridSpec: (see matplotlib documentations)
        :param left:
        :param right:
        :param bottom:
        :param top:
        :param wspace:
        :param hspace:
        :param width_ratios:
        :param height_ratios:
        """

        self.npanels = 0
        self.shape = shape
        self._locations = []
        self._labels = []
        self.panels = []

        self.figsize = kwargs.get('figsize', plt.rcParams.get('figure.figsize'))

        self.fig = plt.figure(**kwargs)

        # OPTION 1: INITIALIZATION BASED ON ``labels``
        # # # # # # # # # # # #
        # When labels is given as a numpy array or dictionary,
        # the shape and grid parameters are ignored.

        # If labels is given as a numpy array, decode it into dictionary form.
        if isinstance(labels, np.ndarray):
            labels = _decode_label_array(labels)

        if isinstance(labels, dict):

            # If other parameters were not passed as their default
            if grid is not None or shape != (2, 2):
                warnings.warn('``labels`` was provided as a dictionary or array.'
                              'The input to ``grid`` and ``shape`` will be ignored.')

            # Set crucial variables
            self._labels = list(labels.keys())
            self._locations = list(labels.values())
            self.shape = _find_max_tuple(self._locations)
            self.npanels = len(self._labels)
            draw_labels = True

        else:

            # OPTION 2: INITIALIZATION BASED ON ``grid``
            # # # # # # # # # # # #

            if grid is not None:

                # OPTION 2.1: grid is passed as an Iterable of ints
                if all(isinstance(i, int) for i in grid):
                    self.shape, grid, self.npanels = _get_subplot_raster(grid)

                # OPTION 2.2: grid is passed as an Iterable of Tuples
                elif all(isinstance(i, Tuple) for i in grid):
                    self.npanels = len(grid)
                    self.shape = _find_max_tuple(grid)

                else:
                    raise TypeError("Sorry, ``grid`` is not a valid input. "
                                    "Refer to the documentation for supported input types.")

            # OPTION 3: INITIALIZATION BASED ON ``shape``
            # # # # # # # # # # # #
            else:
                # Make a panel at each cell of the grid defined by shape
                self.shape = shape
                self.npanels = int(np.prod(shape))

                grid = list()
                for row in range(self.shape[0]):
                    for col in range(self.shape[1]):
                        grid.append((row, col))

            self._locations = grid

            # Get labels based on provided vector or revert to default
            if isinstance(labels, bool):
                self._labels = _get_letters(case=kwargs.get('label_case', 'uppercase'))[:self.npanels]
                draw_labels = labels

            elif isinstance(labels, Iterable):
                assert len(labels) == self.npanels, "Length of label vector does not match number of panels."
                self._labels = list(labels)
                draw_labels = True

            else:
                raise TypeError("Sorry, ``labels`` is not a valid input. "
                                "Refer to the documentation for supported input types.")

        # MAKE SUBPLOT LAYOUT
        # # # # # # # # # # # #

        self.gridspec = gs.GridSpec(nrows=self.shape[0],
                                    ncols=self.shape[1],
                                    figure=self.fig,
                                    **kwargs
                                    )

        Panels = namedtuple('Panels', [i for i in self._labels])
        self.panels = Panels(*[self.fig.add_subplot(_get_grid_location(loc, self.gridspec))
                               for loc in self._locations])

        # If labels should be drawn, draw them now.
        if draw_labels:
            self._draw_labels(label_location=kwargs.get('label_location', (-0.1, 1.1)),
                              size=kwargs.get('label_size', 14),
                              weight=kwargs.get('label weight', 'bold'))


    def _draw_labels(self,
                     label_location: Optional[Tuple] = (-0.1, 1.1),
                     size: Optional[int] = 14,
                     weight: Optional[str] = 'bold'
                     ) -> None:

        for ix in range(self.npanels):
            self.panels[ix].text(label_location[0],
                                 label_location[1],
                                 self._labels[ix],
                                 transform=self.panels[ix].transAxes,
                                 size=size,
                                 weight=weight,
                                 usetex=False,
                                 family='sans-serif')


def _get_letters(case: Optional[str] = 'uppercase') -> str:
    """

    :param case: 'lowercase' or 'uppercase'. Defaults to 'lowercase'.
    :return: string of ordered alphabet
    """
    if case == 'lowercase':
        return string.ascii_lowercase
    else:
        return string.ascii_uppercase


def _decode_label_array(labels: np.array) -> dict:
    """
    Helper function to transform a numpy array of subplot specifications into a dictionary
    mapping labels to locations
    :param labels: np.array that maps cells in in the grid to a subplot label
    :return: The mapping in dictionary form
    """
    NotImplemented


def _get_grid_location(location: Tuple,
                       gridspec: matplotlib.gridspec.GridSpec
                       ) -> matplotlib.gridspec.SubplotSpec:
    """
    From A tuple of locations in a grid, return the SubplotSpec at the given coordinates.

    :param location: Tuple of locations. Can take one of these forms:
                    - (int, int)
                    - (Iterable, int)
                    - (Iterable, Iterable)
    :param gridspec: matplotlib GridSpec object
    :return: matplotlib SubplotSpec object
    """
    rows, cols = location

    # if both are integers
    if isinstance(rows, int) and isinstance(cols, int):
        return gridspec[rows, cols]

    elif isinstance(rows, Iterable) and isinstance(cols, int):
        return gridspec[rows[0]:rows[-1]+1, cols]

    elif isinstance(rows, int) and isinstance(cols, Iterable):
        return gridspec[rows, cols[0]:cols[-1]+1]

    elif isinstance(rows, Iterable) and isinstance(cols, Iterable):
        return gridspec[rows[0]:rows[-1]+1, cols[0]:cols[-1]+1]


def _get_subplot_raster(grid: Iterable[int],
                        ) -> Tuple[Tuple[int,int], Iterable[Tuple], int]:
    """
    Defines a subplot raster from an iterable of integers that defines the number of plots in each row.

    :param grid: Iterable of integers, defining the number of plots in each row.
                Length must equal ``grid[0]``

    :return:    - A Tuple defining the shape of the raster
                - A vector of tuples defining the locations of each plot in the grid
                - The number of panels
    """

    npanels = int(sum(grid))
    locations = []

    # calculate shape based on length of grid and least common multiple of grid
    shape = (len(grid), _lcm_of_array(grid))

    for row in range(len(grid)):

        # Size of each plot in this row
        size = shape[1] / grid[row]

        # Make tuples of locations of each plot
        for panel in range(grid[row]):
            locations.append((row, range(int(panel*size), int(panel*size+size))))

    return shape, locations, npanels


def _lcm_of_array(a: Iterable[int]
                  ) -> int:
    """
    helper function to calculate the lowest common multiple of an array.
    :param a: Iterable array of integers
    :return: integer
    """

    lcm = a[0]
    for i in range(1, len(a)):
        lcm = lcm * a[i] // math.gcd(lcm, a[i])
    return lcm

def _find_max_tuple(x: Iterable[Tuple[Union[Iterable, int], Union[Iterable, int]]]
                    ) -> Tuple[int, int]:
    """
    Given a list of integer / range tuples, returns the maximum values along the first and second dimension
    :param x: List of Tuples
    :return: Tuple of maximum values of first and second dimension that occur in x
    """
    max1 = np.max([np.max(i[0]) for i in x])
    max2 = np.max([np.max(i[1]) for i in x])

    return max1+1, max2+1
