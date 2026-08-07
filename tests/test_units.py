"""Public figure-size unit behavior."""

import pytest

from spiffyplots import CM, MM, figsize


def test_figure_sizes_convert_to_inches():
    cases = (
        ((1, 2), "in", (1, 2)),
        ((2.54, 5.08), "cm", (1, 2)),
        ((25.4, 50.8), "mm", (1, 2)),
    )
    for size, units, expected in cases:
        assert figsize(*size, units=units) == pytest.approx(expected)

    assert 2.54 * CM == pytest.approx(1)
    assert 25.4 * MM == pytest.approx(1)


def test_figure_sizes_reject_unknown_or_missing_units():
    with pytest.raises(ValueError, match="expected 'in', 'cm', or 'mm'"):
        figsize(1, 2, units="pt")
    with pytest.raises(TypeError):
        figsize(1, 2)
