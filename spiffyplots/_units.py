"""Physical figure-size unit helpers."""

CM = 1 / 2.54
MM = 1 / 25.4

_UNIT_FACTORS = {"in": 1.0, "cm": CM, "mm": MM}


def figsize(width: float, height: float, units: str) -> tuple[float, float]:
    """Return a ``(width, height)`` figure size converted to inches.

    Args:
        width: Figure width in ``units``.
        height: Figure height in ``units``.
        units: Input unit: ``"in"``, ``"cm"``, or ``"mm"``

    Raises:
        ValueError: If ``units`` is unsupported.
    """
    try:
        factor = _UNIT_FACTORS[units]
    except (KeyError, TypeError):
        raise ValueError(
            f"Unsupported figure-size unit {units!r}; expected 'in', 'cm', or 'mm'."
        ) from None
    return width * factor, height * factor
