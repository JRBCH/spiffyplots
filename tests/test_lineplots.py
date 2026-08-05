import matplotlib.pyplot as plt
import numpy as np

from spiffyplots.lineplots import multiline


def test_multiline_adds_each_line_to_the_requested_axis():
    figure, axis = plt.subplots()
    x = [np.array([0, 1]), np.array([0, 2])]
    y = [np.array([1, 2]), np.array([2, 3])]

    collection = multiline(x, y, [0, 1], axis=axis)

    assert collection.axes is axis
    assert len(collection.get_segments()) == 2
    plt.close(figure)
