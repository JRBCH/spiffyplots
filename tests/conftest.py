"""Shared test isolation."""

import os
import tempfile

import pytest

_MPL_CONFIG = tempfile.TemporaryDirectory(prefix="spiffyplots-mpl-")
os.environ["MPLCONFIGDIR"] = _MPL_CONFIG.name

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")
