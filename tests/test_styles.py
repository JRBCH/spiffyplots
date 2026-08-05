"""Tests for the bundled matplotlib style sheets.

These check that the styles actually ship and register. The package spent
years shipping none of them, which went unnoticed because a stale copy in
``~/.matplotlib/stylelib`` made it look fine locally, so the
``clean_mpl_config`` fixture below is not optional decoration.
"""

import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

import spiffyplots

# Resolve through the installed package, never through the repo, so the tests
# can only see what a user would actually get.
STYLES_PATH = spiffyplots.STYLES_PATH

HAS_LATEX = shutil.which("latex") is not None


@pytest.fixture(scope="session", autouse=True)
def clean_mpl_config(tmp_path_factory):
    """Hide any pre-existing user style library for the whole session.

    Without this every test here passes even when the package ships no styles
    at all, because matplotlib picks them up from the user config dir.
    """
    original = os.environ.get("MPLCONFIGDIR")
    os.environ["MPLCONFIGDIR"] = str(tmp_path_factory.mktemp("mplconfig"))
    yield
    if original is None:
        del os.environ["MPLCONFIGDIR"]
    else:
        os.environ["MPLCONFIGDIR"] = original


@pytest.fixture(scope="session")
def styles_per_folder() -> dict[str, set[str]]:
    """Map each folder under ``styles/`` to the style names it contains."""
    folders = {}
    for folder, _, _ in os.walk(STYLES_PATH):
        folder = Path(folder)
        names = {path.stem for path in folder.glob("*.mplstyle")}
        if names:
            folders[str(folder.relative_to(STYLES_PATH))] = names
    return folders


@pytest.fixture(scope="session")
def all_styles(styles_per_folder) -> set[str]:
    return set().union(*styles_per_folder.values())


def test_styles_are_shipped(styles_per_folder):
    """The style files exist inside the installed package."""
    assert STYLES_PATH.is_dir(), f"{STYLES_PATH} is missing from the package"
    assert styles_per_folder, "no .mplstyle files shipped"
    for folder, names in styles_per_folder.items():
        assert names, f"no styles found in {folder}"


def test_styles_registered(all_styles):
    """Every shipped style is registered under its bare name."""
    for style in sorted(all_styles):
        assert style in matplotlib.style.library, f"{style!r} missing from library"
        assert style in matplotlib.style.available, f"{style!r} missing from available"


def test_base_style_applies():
    """The headline style resolves and carries its rcParams."""
    with plt.style.context("spiffy"):
        assert plt.rcParams["axes.linewidth"] == 0.5
        assert plt.rcParams["axes.spines.top"] is False


def test_styles_compose():
    """A colour style layers on top of the base style."""
    with plt.style.context(["spiffy", "muted"]):
        cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        assert cycle[0] == "#332288"
        assert plt.rcParams["axes.linewidth"] == 0.5


@pytest.mark.parametrize(
    "style", sorted(p.stem for p in STYLES_PATH.rglob("*.mplstyle"))
)
def test_usage_of_each_style(style, tmp_path):
    """Each style applies to a real figure and renders.

    Catches rcParam keys that matplotlib removes between releases, which is
    the failure mode a plain 'is it registered' check misses.
    """
    if style == "latex" and not HAS_LATEX:
        pytest.skip("no LaTeX installation available")

    with plt.style.context(style):
        figure, axis = plt.subplots()
        axis.plot([0, 1], [0, 1], label="line")
        axis.legend()
        figure.savefig(tmp_path / f"{style}.png")
        plt.close(figure)


def test_import_emits_no_matplotlib_deprecations():
    """Registration must not rely on deprecated matplotlib helpers.

    ``read_style_directory`` and ``update_nested_dict`` are the obvious way to
    do this and are what SciencePlots uses, but both are deprecated in
    matplotlib 3.11 and removed in 3.13.

    Scoped to ``MatplotlibDeprecationWarning`` on purpose. matplotlib 3.8
    itself trips deprecation warnings inside pyparsing when a recent pyparsing
    is installed, which is upstream noise and not something this package can
    or should fix.
    """
    import importlib

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(spiffyplots)

    deprecations = [
        str(entry.message)
        for entry in caught
        if issubclass(entry.category, matplotlib.MatplotlibDeprecationWarning)
    ]
    assert not deprecations, deprecations


def test_registration_works_without_pyplot():
    """Registration itself must not depend on pyplot being imported.

    ``import spiffyplots`` does pull in pyplot, because MultiPanel needs it.
    What this pins is narrower: the registration path uses only
    ``matplotlib.style``, so the styles land in the library even when pyplot
    has never been touched and no backend has been selected.
    """
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys, matplotlib.style;"
                " import spiffyplots;"
                " spiffyplots._register_styles();"
                " print('spiffy' in matplotlib.style.available)"
            ),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "True"


@pytest.mark.skipif(
    tuple(int(part) for part in matplotlib.__version__.split(".")[:2]) < (3, 7),
    reason="package-relative style names need matplotlib >= 3.7",
)
def test_dotted_package_style_access():
    """Styles are also reachable without the import side effect."""
    with plt.style.context("spiffyplots.styles.spiffy"):
        assert plt.rcParams["axes.linewidth"] == 0.5
