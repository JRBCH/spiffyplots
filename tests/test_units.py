"""Tests for physical figure-size helpers."""

import pytest

from spiffyplots import CM, MM, figsize


@pytest.mark.parametrize(
    ("size", "units", "expected"),
    [
        ((1, 2), "in", (1, 2)),
        ((2.54, 5.08), "cm", (1, 2)),
        ((25.4, 50.8), "mm", (1, 2)),
    ],
)
def test_figsize_converts_to_inches(size, units, expected):
    assert figsize(*size, units=units) == pytest.approx(expected)


def test_figsize_defaults_to_millimetres():
    assert figsize(25.4, 50.8) == pytest.approx((1, 2))


def test_unit_constants_convert_to_inches():
    assert 2.54 * CM == pytest.approx(1)
    assert 25.4 * MM == pytest.approx(1)


def test_figsize_rejects_unknown_units():
    with pytest.raises(ValueError, match="expected 'in', 'cm', or 'mm'"):
        figsize(1, 2, units="pt")
