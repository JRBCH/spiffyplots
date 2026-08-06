import matplotlib.pyplot as plt
import numpy as np
import pytest

from spiffyplots.lineplots import multiline

Y = np.array([[0, 1, 0], [1, 2, 1], [2, 3, 2]], dtype=float)
VALUES = np.array([0.0, 0.5, 1.0])
X = np.array([0.0, 1.0, 2.0])


def test_multiline_colours_match_cmap_of_values_with_shared_x():
    figure, axis = plt.subplots()

    lines = multiline(X, Y, VALUES, axis=axis, cmap="viridis", norm=plt.Normalize(0, 1))
    figure.canvas.draw()

    assert len(lines.get_segments()) == 3
    assert np.allclose(lines.get_colors(), lines.cmap(lines.norm(VALUES)))
    plt.close(figure)


def test_multiline_colours_match_cmap_of_values_with_per_line_x():
    figure, axis = plt.subplots()
    x = [
        np.array([0.0, 1.0]),
        np.array([0.0, 1.0, 2.0]),
        np.array([0.0, 1.0, 2.0, 3.0]),
    ]
    y = [
        np.array([0.0, 1.0]),
        np.array([1.0, 2.0, 1.0]),
        np.array([2.0, 3.0, 2.0, 3.0]),
    ]

    lines = multiline(x, y, VALUES, axis=axis, cmap="viridis", norm=plt.Normalize(0, 1))
    figure.canvas.draw()

    assert [len(seg) for seg in lines.get_segments()] == [2, 3, 4]
    assert np.allclose(lines.get_colors(), lines.cmap(lines.norm(VALUES)))
    plt.close(figure)


def test_multiline_result_is_a_colorbar_mappable():
    figure, axis = plt.subplots()

    lines = multiline(X, Y, VALUES, axis=axis, cmap="viridis")
    bar = figure.colorbar(lines, ax=axis)

    assert bar.mappable is lines
    plt.close(figure)


def test_multiline_accepts_a_generator_of_values():
    figure, axis = plt.subplots()

    lines = multiline(
        X, Y, (v for v in VALUES), axis=axis, cmap="viridis", norm=plt.Normalize(0, 1)
    )
    figure.canvas.draw()

    assert np.allclose(lines.get_colors(), lines.cmap(lines.norm(VALUES)))
    plt.close(figure)


def test_multiline_defaults_to_the_current_axis():
    figure, axis = plt.subplots()

    lines = multiline(X, Y, VALUES)

    assert lines.axes is axis
    plt.close(figure)


def test_multiline_preserves_explicit_limits():
    figure, axis = plt.subplots()
    axis.set_xlim(-1, 1)

    multiline(X, Y, VALUES, axis=axis)

    assert axis.get_xlim() == (-1.0, 1.0)
    assert axis.get_ylim() != (-1.0, 1.0)  # y still autoscaled
    plt.close(figure)


@pytest.mark.parametrize(
    "x, y, c",
    [
        ([X, X, X], Y[:2], VALUES[:2]),  # 3 x arrays, 2 lines
        (X, Y, VALUES[:2]),  # 3 lines, 2 values
        ([np.array([0.0, 1.0])], [np.array([0.0, 1.0, 2.0])], [0.0]),  # point mismatch
        (X, Y, [0.0, 0.5, np.inf]),  # non-finite value
        (X, Y, [0.0, 0.5, np.nan]),  # non-finite value
    ],
)
def test_multiline_rejects_bad_cardinality_before_drawing(x, y, c):
    figure, axis = plt.subplots()

    with pytest.raises(ValueError):
        multiline(x, y, c, axis=axis)

    assert len(axis.collections) == 0
    plt.close(figure)
