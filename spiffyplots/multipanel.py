# -*- coding: utf-8 -*-
"""The Spiffy MultiPanel class and its methods.
"""

from collections import defaultdict
from itertools import product, combinations
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
    The central object of the `multipanel` module. Initiates a figure with multiple panels.
    """

    def __init__(
        self,
        shape: Optional[Tuple[int, int]] = (2, 2),
        grid: Union[Iterable[Tuple], Iterable[int]] = None,
        labels: Union[bool, Iterable[str], Dict[str, tuple], np.array] = False,
        **kwargs
    ) -> None:
        """
        The ``MultiPanel`` object is basically a wrapper of matplotlib's ``GridSpec``,
        but tries to simplify some aspects of multi-panel figure generation, such as Figure labels
        and the layout of panels. Depending on the input, the layout is initialized in one of three ways:

        **OPTION 1: Initialization based on the** ``labels`` **parameter**

            The ``labels`` parameter can be passed in as a dictionary, mapping custom figure labels (e.g. 'a', 'b', 'c')
            to locations in the grid that are defined by Tuples (e.g. {'A': (0, range(2,5)} will make a plot in the
            first row spanning columns 2-4 and give it the label A.

            Similarly, ``labels`` can be passed as a 2-dimensional np.array of strings. In this case, the strings in
            the cells of the array correspond to the label of the panels. Adjacent identical labels are considered
            one panel. For example, the array::
                ['A', 'A', 'D']
                ['B', 'C', 'D']
                ['E', 'E', 'E']

            will create 5 panels, each occupying the space that the respective label takes up in the array.

            This option is useful when you want to control both the arrangement of panels, and the order and
            format of their labels. If label is passed in as a dictionary or np.array, the ``grid`` and ``shape``
            parameters are ignored.

        **OPTION 2: Initialization based on the** ``grid`` **parameter:**

            If option 1 does not apply, the class will try to be initialized through the ``grid`` parameter.

            Example:
                Generate a two-row figure with 3 columns (panels) in the first row and 2 columns (panels)
                in the second row::
                    >>> fig = MultiPanel(grid=[3, 2])

            Example:
                Generate a 2x3 figure with 5 panels, where one panel spans
                both rows in the last column::
                    >>> fig = MultiPanel(grid=[(0, 0), (0, 1), (1, 0), (1, 1), (range(0, 2), 2)])

        **OPTION 3: initialization based on the** ``shape`` **parameter:**

            if neither ``labels`` or ``grid`` are supplied, the class will generate one panel in each cell of the grid
            matrix, as defined by the ``shape`` parameter.

            Example:
                Generate a 3x3 grid with
                9 plots of equal size::
                    >>> fig = MultiPanel(shape=(3, 3))

        Args:
            shape (Tuple): Determines the shape of the MultiPanel grid layout.

            grid (Iterable[Tuple], Iterable[int]): Determines the layout of subplots across the MultiPanel matrix.
                Defaults to one plot in each cell of the ``shape`` matrix. Can be one of:

                * Iterable of grid location tuples of form ``[rows, columns]``, in which rows and columns are
                  either int (for a single cell) or Iterable (for spanning multiple cells).
                * Iterable of ints with length ``shape[0]``, which defines the number of plots in each row.
                  Each plot then has the size ``1 x shape[0]/int``.
                  **Attention**: ``shape[0]`` must be divisable by every element in ``grid``.

            labels (bool, Iterable[str], dict, np.array): Assigns labels to subplots. Defaults to False.
                Can be one of:

                * Boolean. If True, labels are assigned to plots first across rows, then across columns.
                * Iterable of strings assigning labels to subplots, in the same order as defined by ``grid``.
                * A Dictionary mapping [str] keys to [Tuple] locations in the grid. This setting overrides the grid.
                * A np.array of the same shape as ``shape``, mapping string names to the locations in the grid.
                  Figures can span multiple cells in the grid. Also overrides the grid.


        Keyword Args:
            figsize (Tuple): Size of the figure. Will be passed into ``matplotlib.pyplot.figure``.

            label_case (str): 'uppercase' or 'lowercase'.
                This and following kwargs are passed to ``MultiPanel._draw_labels``.
            label_weight (str): Weight of the figure labels. defaults to 'bold'
            label_size (int): Font Size for figure labels. defaults to 14.
            label_location (Tuple): Tuple. Location of the figure labels relative to axis origin.
                    Defaults to (-0.1, 1.1)

            left (float): left margin.
                This and following kwargs are passed to ``matplotlib.gridspec.GridSpec``
            right (float): right margin
            bottom (float): bottom margin
            top (float): top margin
            wspace (float): horizontal spacing
            hspace (float): vertical spacing
            width_ratios (Iterable): width ratios of columns
            height_ratios (Iterable): height ratios of rows
        """

        self.npanels = 0
        self.shape = shape
        self._locations = []
        self._labels = []
        self.panels = []

        # parse kwargs
        figsize = kwargs.pop("figsize", plt.rcParams.get("figure.figsize"))

        self.fig = plt.figure(figsize=figsize, **kwargs)

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
                warnings.warn(
                    "``labels`` was provided as a dictionary or array."
                    "The input to ``grid`` and ``shape`` will be ignored."
                )

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
                    raise TypeError(
                        "Sorry, ``grid`` is not a valid input. "
                        "Refer to the documentation for supported input types."
                    )

            # OPTION 3: INITIALIZATION BASED ON ``shape``
            # # # # # # # # # # # #
            else:
                # Make a panel at each cell of the grid defined by shape
                try:
                    self.shape = shape
                    self.npanels = int(np.prod(shape))

                except ValueError:
                    raise TypeError(
                        "Sorry, ``shape`` is not a valid input. "
                        "Refer to the documentation for supported input types."
                    )

                grid = list()
                for row in range(self.shape[0]):
                    for col in range(self.shape[1]):
                        grid.append((row, col))

            self._locations = grid

            # Get labels based on provided vector or revert to default
            if isinstance(labels, bool):
                self._labels = _get_letters(case=kwargs.pop("label_case", "uppercase"))[
                    : self.npanels
                ]
                draw_labels = labels

            elif isinstance(labels, Iterable):
                assert (
                    len(labels) == self.npanels
                ), "Length of label vector does not match number of panels."
                self._labels = list(labels)
                draw_labels = True

            else:
                raise TypeError(
                    "Sorry, ``labels`` is not a valid input. "
                    "Refer to the documentation for supported input types."
                )

        # MAKE SUBPLOT LAYOUT
        # # # # # # # # # # # #

        # Raise a warning if there are overlapping panels
        overlaps = _panel_overlap(self._locations, self.shape)
        if len(overlaps) != 0:
            warnings.warn(
                "One or more panel coordinates overlap: {}! You probably do not "
                "want this, double check your input coordinates."
            )

        # Initialize GridSpec and consider Keyword Arguments

        self.gridspec = gs.GridSpec(
            nrows=self.shape[0],
            ncols=self.shape[1],
            figure=self.fig,
            left=kwargs.pop("left", None),
            bottom=kwargs.pop("bottom", None),
            right=kwargs.pop("right", None),
            top=kwargs.pop("top", None),
            wspace=kwargs.pop("wspace", None),
            hspace=kwargs.pop("hspace", None),
            width_ratios=kwargs.pop("width_ratios", None),
            height_ratios=kwargs.pop("height_ratios", None),
        )

        Panels = namedtuple("Panels", [i for i in self._labels])
        self.panels = Panels(
            *[
                self.fig.add_subplot(_get_grid_location(loc, self.gridspec))
                for loc in self._locations
            ]
        )

        # If labels should be drawn, draw them now.
        if draw_labels:
            self._draw_labels(
                label_location=kwargs.pop("label_location", (-0.2, 1.1)),
                size=kwargs.pop("label_size", 14),
                weight=kwargs.pop("label_weight", "bold"),
            )

    def _draw_labels(
        self,
        label_location: Tuple[float, float] = (-0.2, 1.1),
        size: int = 14,
        weight: str = "bold",
    ) -> None:

        for ix in range(self.npanels):

            # make separate axis for label
            loc = self._locations[ix]
            axis_loc = (int(np.min(loc[0])), int(np.min(loc[1])))
            ax = self.fig.add_subplot(
                _get_grid_location(axis_loc, self.gridspec), label=self._labels[ix]
            )
            ax.axis("off")

            ax.text(
                label_location[0],
                label_location[1],
                self._labels[ix],
                transform=ax.transAxes,
                size=size,
                weight=weight,
                usetex=False,
                family="sans-serif",
            )


def _get_letters(case: Optional[str] = "uppercase") -> str:
    """

    :param case: 'lowercase' or 'uppercase'. Defaults to 'lowercase'.
    :return: string of ordered alphabet
    """
    if case == "lowercase":
        return string.ascii_lowercase
    else:
        return string.ascii_uppercase


def _is_iter_of_iters(labels) -> bool:
    """
    Helper function to check for iterable of iterables
    """
    return isinstance(labels, Iterable) and all(isinstance(_, Iterable) for _ in labels)


def _decode_label_array(labels: Iterable[Iterable]) -> dict:
    """
    Helper function to transform a numpy array of subplot specifications into a dictionary
    mapping labels to locations. Generally accepts iterables of iterables, including
    numpy arrays, list of lists, and list of strings, where the latter assumes
    labels are individual characters.

    :param labels: grid of labels that maps cells in in the grid to a subplot label
    :return: The mapping in dictionary form
    """

    # make sure we've got a list of lists
    if not _is_iter_of_iters(labels):
        raise TypeError(
            "Sorry, ``labels`` must be a iterable of iterables, where "
            "each sub-iterable is the same length"
        )

    label_grid = [list(_) for _ in labels]

    # verify labels format
    if not all(len(_) == len(label_grid[0]) for _ in label_grid[1:]):
        raise TypeError(
            "Sorry, ``labels`` must be a iterable of iterables, where "
            "each sub-iterable is the same length"
        )

    # collect grid positions for each label
    label_pos = defaultdict(list)
    for i, row in enumerate(label_grid):
        for j, label in enumerate(row):
            label_pos[label].append((i, j))

    # ensure labels spanning grid points are linear contiguous
    label_dict = {}
    for label, positions in label_pos.items():

        rows = list(set([_[0] for _ in positions]))
        cols = list(set([_[1] for _ in positions]))

        row_range = range(min(rows), max(rows) + 1)
        col_range = range(min(cols), max(cols) + 1)

        # check that the label grid positions form a box
        expected_coords = list(product(rows, cols))
        if set(positions) != set(expected_coords):
            raise TypeError(
                "Sorry, label grid spec contains invalid layout; "
                "all identical label positions must be adjacent"
            )

        if len(rows) == 1:
            row_range = rows[0]
        if len(cols) == 1:
            col_range = cols[0]

        label_dict[label] = (row_range, col_range)

    return label_dict


def _get_grid_location(
    location: Tuple, gridspec: matplotlib.gridspec.GridSpec
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
        return gridspec[rows[0] : rows[-1] + 1, cols]

    elif isinstance(rows, int) and isinstance(cols, Iterable):
        return gridspec[rows, cols[0] : cols[-1] + 1]

    elif isinstance(rows, Iterable) and isinstance(cols, Iterable):
        return gridspec[rows[0] : rows[-1] + 1, cols[0] : cols[-1] + 1]


def _get_subplot_raster(
    grid: Iterable[int],
) -> Tuple[Tuple[int, int], Iterable[Tuple], int]:
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
            if size == 1:
                locations.append((row, panel))
            else:
                locations.append(
                    (row, range(int(panel * size), int(panel * size + size)))
                )

    return shape, locations, npanels


def _lcm_of_array(a: Iterable[int]) -> int:
    """
    helper function to calculate the lowest common multiple of an array.
    :param a: Iterable array of integers
    :return: integer
    """

    lcm = a[0]
    for i in range(1, len(a)):
        lcm = lcm * a[i] // math.gcd(lcm, a[i])
    return lcm


def _find_max_tuple(
    x: Iterable[Tuple[Union[Iterable, int], Union[Iterable, int]]]
) -> Tuple[int, int]:
    """
    Given a list of integer / range tuples, returns the maximum values along the first and second dimension
    :param x: List of Tuples
    :return: Tuple of maximum values of first and second dimension that occur in x
    """
    max1 = np.max([np.max(i[0]) for i in x])
    max2 = np.max([np.max(i[1]) for i in x])

    # Add plus one to output to transform to dimensionality (i.e. a max value of 0 indicates 1 dimension)
    return max1 + 1, max2 + 1


def _panel_overlap(locations, shape=None):
    """
    Check a list of (x,y) location coordinates, which may be ranges, to ensure
    none overlap

    :param locations: list of (x,y) tuple locations
    :param shape: the shape the locations should fit into (deprecated)
    """

    # expand all coordinates for each location
    coords = []
    for loc in locations:
        xlocs = loc[0] if isinstance(loc[0], range) else [loc[0]]
        ylocs = loc[1] if isinstance(loc[1], range) else [loc[1]]
        coords.append(list(product(xlocs, ylocs)))

    # examine all pairs of locations to make sure nothing overlaps
    overlap = False
    for loc1, loc2 in combinations(coords, 2):
        overlap = set(loc1).intersection(loc2)
        if overlap:
            break

    return overlap
