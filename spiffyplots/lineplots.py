import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection


def multiline(x, y, c, axis=None, **kwargs):
    """Plot many lines at once, coloured by one scalar per line.

    Each row of ``y`` is one line. ``x`` is either one shared 1D array used for
    every line, or one array per line with ragged lengths allowed. ``c`` holds
    one finite scalar per line, mapped through the collection's ``cmap`` and
    ``norm``.

    Args:
        x: shared 1D array of length ``P``, or a sequence of ``N`` arrays.
        y: array of shape ``(N, P)``, or a sequence of ``N`` 1D arrays.
        c: ``N`` finite scalars, one per line.
        axis: target axes. Defaults to ``plt.gca()``.
        **kwargs: forwarded to ``LineCollection`` (``cmap``, ``norm``, ``lw`` ...).

    Returns:
        matplotlib.collections.LineCollection: the added collection, itself the
        mappable to hand to ``fig.colorbar``.

    Raises:
        ValueError: if the x/y point counts or the line/value counts disagree,
            or any value is not finite.

    Example:
        >>> cmap = spiffy.cmap.from_base(spiffy.colors.tol_vibrant.red)
        >>> norm = plt.Normalize(values.min(), values.max())
        >>> lines = spiffy.multiline(x, y, values, axis=ax, cmap=cmap, norm=norm)
        >>> fig.colorbar(lines, ax=ax, label="parameter")
    """
    values = np.asarray(list(c), dtype=float)
    if values.ndim != 1:
        raise ValueError("c must be one scalar per line")

    y_lines = [np.asarray(row, dtype=float) for row in y]
    x_lines = _as_x_lines(x, len(y_lines))
    n_lines = len(y_lines)

    if len(values) != n_lines:
        raise ValueError(f"{n_lines} lines but {len(values)} colour values")
    if not np.isfinite(values).all():
        raise ValueError("c must be finite, one scalar per line")
    if len(x_lines) != n_lines:
        raise ValueError(f"{len(x_lines)} x arrays but {n_lines} lines")
    for i, (xi, yi) in enumerate(zip(x_lines, y_lines)):
        if len(xi) != len(yi):
            raise ValueError(f"line {i}: {len(xi)} x points but {len(yi)} y points")

    lc = LineCollection(
        [np.column_stack([xi, yi]) for xi, yi in zip(x_lines, y_lines)], **kwargs
    )
    lc.set_array(values)

    if axis is None:
        axis = plt.gca()
    axis.add_collection(lc)
    axis.autoscale_view(
        scalex=axis.get_autoscalex_on(),
        scaley=axis.get_autoscaley_on(),
    )
    return lc


def _as_x_lines(x, n_lines):
    """One x array per line: broadcast a shared 1D x, else one array each."""
    try:
        shared = np.asarray(x, dtype=float)
    except (ValueError, TypeError):
        shared = None  # ragged per-line x
    if shared is not None and shared.ndim == 1:
        return [shared] * n_lines
    if shared is not None and shared.ndim == 2:
        return list(shared)
    return [np.asarray(xi, dtype=float) for xi in x]
