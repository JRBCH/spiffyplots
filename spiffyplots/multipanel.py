"""The Spiffy MultiPanel class and its methods."""

import math
import string
import warnings
from collections import defaultdict, namedtuple
from collections.abc import Iterable
from itertools import combinations, product
from numbers import Integral

import matplotlib
import matplotlib.gridspec as gs
import matplotlib.pyplot as plt
import numpy as np


class MultiPanel:
    """
    The central object of the `multipanel` module. Initiates a figure with multiple panels.
    """

    def __init__(
        self,
        shape: tuple[int, int] | None = (2, 2),
        grid: Iterable[tuple] | Iterable[int] | None = None,
        labels: bool | Iterable[str] | dict[str, tuple] | np.ndarray = False,
        **kwargs,
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

            label_case (str): 'uppercase' or 'lowercase'. Defaults to 'lowercase'.
                This and following kwargs are passed to ``MultiPanel._draw_labels``.
            label_weight (str): Weight of the figure labels. defaults to 'bold'
            label_size (int): Font size for figure labels. Defaults to 12.
            label_offset (Tuple): Label offset in points from the panel's top-left
                corner. Defaults to (-20, 6).
            label_location (Tuple): Deprecated label location in panel axes fractions.
                Use ``label_offset`` for layout-independent alignment.
            label_color (str): Color of the figure labels. Defaults to 'black'.

            left (float): left margin.
                This and the following five geometry kwargs are passed to
                ``matplotlib.gridspec.GridSpec``. They are mutually exclusive
                with constrained layout: when constrained layout is active,
                they are ignored and ``MultiPanel`` emits a warning. Disable
                constrained layout before constructing the figure to use them.
            right (float): right margin
            bottom (float): bottom margin
            top (float): top margin
            wspace (float): horizontal spacing
            hspace (float): vertical spacing
            width_ratios (Iterable): width ratios of columns. Works with or
                without constrained layout.
            height_ratios (Iterable): height ratios of rows. Works with or
                without constrained layout.
        """

        gridspec_kwarg_names = (
            "left",
            "bottom",
            "right",
            "top",
            "wspace",
            "hspace",
            "width_ratios",
            "height_ratios",
        )
        supported_kwargs = {
            "figsize",
            "dpi",
            "label_case",
            "label_weight",
            "label_size",
            "label_offset",
            "label_location",
            "label_color",
            *gridspec_kwarg_names,
        }
        unexpected_kwargs = sorted(set(kwargs) - supported_kwargs)
        if unexpected_kwargs:
            raise TypeError(
                "MultiPanel() got unexpected keyword arguments: "
                f"{', '.join(unexpected_kwargs)}"
            )

        self.npanels = 0
        self.shape = shape
        self._locations = []
        self._labels = []
        self.panels = []

        # parse kwargs
        figsize = kwargs.pop("figsize", plt.rcParams.get("figure.figsize"))
        dpi = kwargs.pop("dpi", plt.rcParams.get("figure.dpi"))

        self.fig = plt.figure(figsize=figsize, dpi=dpi)

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
                elif all(isinstance(i, tuple) for i in grid):
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

                grid = []
                for row in range(self.shape[0]):
                    for col in range(self.shape[1]):
                        grid.append((row, col))

            self._locations = grid

            # Get labels based on provided vector or revert to default
            if isinstance(labels, bool):
                self._labels = _get_letters(case=kwargs.pop("label_case", "lowercase"))[
                    : self.npanels
                ]
                draw_labels = labels

            elif isinstance(labels, Iterable):
                assert len(labels) == self.npanels, (
                    "Length of label vector does not match number of panels."
                )
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
                f"One or more panel coordinates overlap: {sorted(overlaps)}! "
                "You probably do not want this, double check your input coordinates.",
                stacklevel=2,
            )

        # Initialize GridSpec and consider Keyword Arguments

        gridspec_kwargs = {
            name: kwargs.pop(name, None) for name in gridspec_kwarg_names
        }
        geometry_kwargs = [
            name
            for name in gridspec_kwarg_names[:6]
            if gridspec_kwargs[name] is not None
        ]
        if geometry_kwargs and self.fig.get_constrained_layout():
            formatted_kwargs = ", ".join(f"`{name}`" for name in geometry_kwargs)
            warnings.warn(
                f"GridSpec keyword arguments {formatted_kwargs} are ignored while "
                "constrained layout is active. Explicit GridSpec geometry and "
                "constrained layout are mutually exclusive; disable constrained "
                "layout to use these values.",
                stacklevel=2,
            )

        self.gridspec = gs.GridSpec(
            nrows=self.shape[0],
            ncols=self.shape[1],
            figure=self.fig,
            **gridspec_kwargs,
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
            has_label_location = "label_location" in kwargs
            has_label_offset = "label_offset" in kwargs
            if has_label_location and has_label_offset:
                raise TypeError("Pass only one of `label_offset` and `label_location`.")

            label_location = kwargs.pop("label_location", None)
            label_offset = kwargs.pop("label_offset", (-20, 6))
            if has_label_location:
                warnings.warn(
                    "`label_location` is deprecated; use `label_offset` for "
                    "layout-independent point offsets.",
                    DeprecationWarning,
                    stacklevel=2,
                )

            self._draw_labels(
                label_offset=label_offset,
                label_location=label_location,
                size=kwargs.pop("label_size", 12),
                weight=kwargs.pop("label_weight", "bold"),
                color=kwargs.pop("label_color", "black"),
            )

    def _draw_labels(self, label_offset, label_location, size, weight, color) -> None:

        text_kwargs = {
            "size": size,
            "weight": weight,
            "ha": "left",
            "va": "baseline",
            "usetex": False,
            "family": "sans-serif",
            "color": color,
        }
        for ax, label in zip(self.panels, self._labels, strict=True):
            if label_location is not None:
                ax.text(
                    label_location[0],
                    label_location[1],
                    label,
                    transform=ax.transAxes,
                    clip_on=False,
                    **text_kwargs,
                )
            else:
                ax.annotate(
                    label,
                    xy=(0, 1),
                    xycoords="axes fraction",
                    xytext=label_offset,
                    textcoords="offset points",
                    annotation_clip=False,
                    **text_kwargs,
                )

    def save(self, path: str, format: str | tuple | list = "pdf", **kwargs):
        """
        Saves the figure as one or multiple file types

        Args:
            path:   file path
                    Example:
                        `save(path='figures/figure1, format='pdf)` will save the object as
                        figures/figure1.pdf
            format: the file format(s) to save as. Defaults to 'pdf'

        """

        if isinstance(format, str):
            formats = (format,)
        else:
            assert isinstance(format, (tuple, list)), (
                "Pass file format as string or tuple/list of strings please"
            )
            formats = tuple(format)

        for file_format in formats:
            fname = f"{path}.{file_format}"
            self.fig.savefig(fname, **kwargs)
            print(f"Saved figure as {fname}")

    def close(self):
        """
        Closes the matplotlib figure object
        """
        plt.close(self.fig)


def _get_letters(case: str | None = "lowercase") -> str:
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
        rows = list({position[0] for position in positions})
        cols = list({position[1] for position in positions})

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
    location: tuple, gridspec: matplotlib.gridspec.GridSpec
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
    row_values = _expand_grid_coordinate(rows)
    col_values = _expand_grid_coordinate(cols)

    row_index = (
        row_values[0]
        if len(row_values) == 1
        else slice(row_values[0], row_values[-1] + 1)
    )
    col_index = (
        col_values[0]
        if len(col_values) == 1
        else slice(col_values[0], col_values[-1] + 1)
    )
    return gridspec[row_index, col_index]


def _expand_grid_coordinate(coordinate: int | Iterable[int]) -> list[int]:
    """Return a grid coordinate as a concrete sequence of integer positions."""
    if isinstance(coordinate, Integral):
        return [int(coordinate)]
    return list(coordinate)


def _get_subplot_raster(
    grid: Iterable[int],
) -> tuple[tuple[int, int], Iterable[tuple], int]:
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
    x: Iterable[tuple[Iterable | int, Iterable | int]],
) -> tuple[int, int]:
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
        xlocs = _expand_grid_coordinate(loc[0])
        ylocs = _expand_grid_coordinate(loc[1])
        coords.append(list(product(xlocs, ylocs)))

    # examine all pairs of locations to make sure nothing overlaps
    overlap = set()
    for loc1, loc2 in combinations(coords, 2):
        overlap = set(loc1).intersection(loc2)
        if overlap:
            break

    return overlap
