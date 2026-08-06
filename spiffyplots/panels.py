"""Panel letters for any matplotlib figure.

The label is anchored to the top left corner of each panel
and offset from there in points, so it sits a fixed physical distance from the
corner.
"""

import string

from matplotlib import rcParams
from matplotlib.text import Text

__all__ = ["label_panels"]

# Set by ``Colorbar``'s own axes creation in both matplotlib 3.8 and 3.11.
_COLORBAR_LABEL = "<colorbar>"

# How far apart, in points, two panel tops can be and still count as one row.
_ROW_TOLERANCE = 6.0


def get_letters(case: str = "lowercase", count: int = 26) -> list[str]:
    """Return ordered letter labels, continuing with aa/AA after z/Z.

    Args:
        case: ``'lowercase'`` or ``'uppercase'``. Defaults to ``'lowercase'``.
        count: number of labels to return.

    Returns:
        A list of ``count`` labels.
    """
    if case == "lowercase":
        alphabet = string.ascii_lowercase
    elif case == "uppercase":
        alphabet = string.ascii_uppercase
    else:
        raise ValueError(
            f"`case` must be 'lowercase' or 'uppercase', got {case!r}.",
        )

    labels = []
    for index in range(count):
        label = ""
        while True:
            index, remainder = divmod(index, len(alphabet))
            label = alphabet[remainder] + label
            if index == 0:
                break
            index -= 1
        labels.append(label)
    return labels


def _is_colorbar(ax) -> bool:
    """Whether ``ax`` is the axes matplotlib created for a colorbar.

    Uses the public label matplotlib puts on colorbar axes. An axes the caller
    built themselves and passed as ``cax=`` carries no such label and is not
    detected; pass ``axes=`` explicitly in that case.
    """
    return ax.get_label() == _COLORBAR_LABEL


def _reading_order(fig, axes) -> list:
    """Sort ``axes`` into reading order: rows top to bottom, and left to right
    within each row.

    Works from the top-left corner in display coordinates rather than from
    ``get_position()``, because the position of an axes inside a ``SubFigure``
    is relative to that subfigure and so is not comparable across subfigures.
    """
    corners = {ax: tuple(ax.transAxes.transform((0.0, 1.0))) for ax in axes}
    tolerance = _ROW_TOLERANCE * fig.dpi / 72.0

    # Group into rows by descending top edge, so panels of unequal height whose
    # tops are level to within the tolerance stay one row, then order each row
    # left to right.
    ordered = []
    row = []
    row_top = None
    for ax in sorted(axes, key=lambda ax: -corners[ax][1]):
        top = corners[ax][1]
        if row_top is not None and row_top - top > tolerance:
            ordered.extend(sorted(row, key=lambda ax: corners[ax][0]))
            row = []
            row_top = None
        if row_top is None:
            row_top = top
        row.append(ax)
    ordered.extend(sorted(row, key=lambda ax: corners[ax][0]))
    return ordered


def _default_axes(fig) -> list:
    """Panel axes of ``fig`` in reading order.

    ``fig.axes`` already recurses into subfigures and already excludes inset
    axes, which are children of their parent axes. Colorbars are the only thing
    that needs filtering out.
    """
    return _reading_order(fig, [ax for ax in fig.axes if not _is_colorbar(ax)])


def label_panels(
    fig,
    axes=None,
    labels=None,
    offset=(-20, 6),
    case="lowercase",
    size=None,
    weight="bold",
    color=None,
    **text_kwargs,
) -> list[Text]:
    """Add panel letters to the axes of a figure.

    Args:
        fig: the :class:`~matplotlib.figure.Figure` to label.
        axes: the axes to label, in the order the labels should be applied.
            Defaults to the axes of ``fig`` in reading order, excluding the
            axes matplotlib created for colorbars.
        labels: the labels themselves. Defaults to letters in ``case``.
        offset: ``(dx, dy)`` in points from the top-left corner of each panel.
        case: ``'lowercase'`` or ``'uppercase'``, used only when ``labels`` is
            not given.
        size: font size. Defaults to ``rcParams["axes.labelsize"]``.
        weight: font weight.
        color: text color. Defaults to the rcParams default.
        **text_kwargs: passed to :meth:`~matplotlib.axes.Axes.annotate`, and
            override every default set here, including ``family`` and
            ``usetex``.

    Returns:
        The :class:`~matplotlib.text.Text` artists, in the order the axes were
        labelled, so a single label can be nudged afterwards.

    Examples:
        >>> from matplotlib.figure import Figure
        >>> from spiffyplots import label_panels
        >>> fig = Figure()
        >>> axs = fig.subplot_mosaic([["a", "a"], ["b", "c"]])
        >>> texts = label_panels(fig)
        >>> [text.get_text() for text in texts]
        ['a', 'b', 'c']

        Labelling a subset, in an order of your own:

        >>> texts = label_panels(fig, axes=[axs["c"], axs["a"]])
        >>> [text.get_text() for text in texts]
        ['a', 'b']
    """
    if axes is None:
        axes = _default_axes(fig)
    else:
        axes = list(axes)

    if labels is None:
        labels = get_letters(case=case, count=len(axes))
    else:
        labels = list(labels)
        if len(labels) != len(axes):
            raise ValueError(
                f"Got {len(labels)} labels for {len(axes)} axes.",
            )

    # Sans-serif and no TeX suits panel letters even inside a serif figure, but
    # both stay overridable through **text_kwargs.
    annotate_kwargs = {
        "size": rcParams["axes.labelsize"] if size is None else size,
        "weight": weight,
        "ha": "left",
        "va": "baseline",
        "usetex": False,
        "family": "sans-serif",
    }
    if color is not None:
        annotate_kwargs["color"] = color
    annotate_kwargs.update(text_kwargs)

    return [
        ax.annotate(
            label,
            xy=(0, 1),
            xycoords="axes fraction",
            xytext=offset,
            textcoords="offset points",
            annotation_clip=False,
            **annotate_kwargs,
        )
        for ax, label in zip(axes, labels, strict=True)
    ]
