"""Tests for the bundled matplotlib style sheets.

These check that the styles actually exist after installation
(this was broken up to spiffyplots 0.6.1), and the package didn't really
install the styles (Sorry, my bad!)
"""

import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib import font_manager

import spiffyplots
from spiffyplots import _genstyles, colors

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


@pytest.mark.parametrize(("alias", "target"), sorted(spiffyplots.STYLE_ALIASES.items()))
def test_bare_aliases_match_their_tol_sheets(alias, target):
    """The pre-0.7 names still resolve, to the same rcParams. Not covered by
    ``test_usage_of_each_style``, which only sees shipped files."""
    assert alias in matplotlib.style.available
    with plt.style.context(alias):
        aliased = plt.rcParams["axes.prop_cycle"]
    with plt.style.context(target):
        assert plt.rcParams["axes.prop_cycle"] == aliased


def test_base_style_applies():
    """The headline style resolves and carries its rcParams."""
    with plt.style.context("spiffy"):
        assert plt.rcParams["axes.linewidth"] == 0.5
        assert plt.rcParams["axes.spines.top"] is False
        assert plt.rcParams["ps.fonttype"] == 42


def test_base_style_exports_editable_text(tmp_path):
    """Vector exports avoid Type 3 fonts and preserve SVG text objects."""
    pdf_path = tmp_path / "spiffy.pdf"
    svg_path = tmp_path / "spiffy.svg"

    with plt.style.context("spiffy"):
        figure, axis = plt.subplots()
        axis.set_xlabel("UNIQUEWORD")
        figure.savefig(pdf_path)
        figure.savefig(svg_path)
        plt.close(figure)

    assert b"/Type3" not in pdf_path.read_bytes()
    assert "<text" in svg_path.read_text()


@pytest.mark.skipif(not HAS_LATEX, reason="no LaTeX installation available")
def test_latex_style_exports_embedded_font(tmp_path):
    """The LaTeX modifier remains embeddable with the base PDF font type."""
    pdf_path = tmp_path / "latex.pdf"

    with plt.style.context(["spiffy", "latex"]):
        figure, axis = plt.subplots()
        axis.set_xlabel("UNIQUEWORD")
        figure.savefig(pdf_path)
        plt.close(figure)

    pdf_bytes = pdf_path.read_bytes()
    assert b"/Type3" not in pdf_bytes and b"/FontFile" in pdf_bytes


def test_base_style_matches_math_to_text_font():
    """Math and text resolve to the same font file, so a label containing
    ``$\\Delta w$`` does not switch typeface mid-string.

    ``mathtext.rm`` must stay a generic family alias rather than a concrete font
    name: it then follows ``font.sans-serif`` and stays matched to whichever
    entry actually resolved on this machine. Note ``sans-serif`` itself is not
    usable there, because the rcParam is validated as a fontconfig pattern and
    the hyphen fails to parse.
    """
    with plt.style.context("spiffy"):
        assert plt.rcParams["font.sans-serif"][0] == "Helvetica"
        assert plt.rcParams["mathtext.fontset"] == "custom"
        assert plt.rcParams["mathtext.rm"] == "sans"

        text_font = font_manager.findfont(
            font_manager.FontProperties(family=["sans-serif"])
        )
        math_font = font_manager.findfont(
            font_manager.FontProperties(family=[plt.rcParams["mathtext.rm"]])
        )
        assert text_font == math_font


def test_latex_style_hands_the_typeface_back_to_tex():
    """``["spiffy", "latex"]`` gives Computer Modern, not Helvetica.

    Matplotlib's TexManager scans ``font.sans-serif`` for a name it recognises
    and injects the matching LaTeX package. The base sheet leads that list with
    Helvetica, which maps to ``\\usepackage{helvet}``, so without the reset in
    latex.mplstyle the LaTeX output would keep Helvetica text while math stayed
    Computer Modern, mismatched inside a single label.
    """
    with plt.style.context(["spiffy", "latex"]):
        assert plt.rcParams["text.usetex"] is True
        assert "Helvetica" not in plt.rcParams["font.sans-serif"]
        assert plt.rcParams["font.sans-serif"][0] == "Computer Modern Sans Serif"


@pytest.mark.skipif(not HAS_LATEX, reason="no LaTeX installation available")
def test_latex_style_does_not_load_helvet():
    """The reset above is checked against what TexManager actually generates."""
    from matplotlib.texmanager import TexManager

    with plt.style.context(["spiffy", "latex"]):
        preamble, fontcmd = TexManager._get_font_preamble_and_command()

    assert "helvet" not in preamble
    assert fontcmd == r"\sffamily"


def test_styles_compose():
    """A colour style layers on top of the base style."""
    with plt.style.context(["spiffy", "tol-muted"]):
        cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        assert cycle[0] == "#CC6677"
        assert plt.rcParams["axes.linewidth"] == 0.5


def test_base_style_draws_its_default_colormap():
    """``plt.style.use`` does not validate ``image.cmap``, so a sheet naming an
    unregistered colormap applies silently and raises inside ``draw``, far from
    the cause. Catches a broken registration order here instead."""
    with plt.style.context("spiffy"):
        assert plt.rcParams["image.cmap"] == "tol.iridescent"
        figure, axis = plt.subplots()
        axis.imshow(np.arange(9).reshape(3, 3))
        figure.canvas.draw()
        plt.close(figure)


def test_generated_sheets_are_up_to_date(tmp_path):
    """The one thing stopping a sheet's hex from drifting from the Python
    constant it mirrors. If this fails, run ``python -m spiffyplots._genstyles``
    rather than editing the sheet."""
    for filename, expected in _genstyles.generate().items():
        shipped = STYLES_PATH / "color" / filename
        assert shipped.is_file(), f"{filename} is not shipped"
        assert shipped.read_text() == expected, f"{filename} is out of date"

    generated = set(_genstyles.generate())
    shipped = {path.name for path in (STYLES_PATH / "color").glob("*.mplstyle")}
    assert shipped == generated, "hand-written sheet in styles/color"

    # Also has to reproduce them into an empty directory.
    assert _genstyles.main(["--output", str(tmp_path)]) == 0
    assert _genstyles.main(["--check", "--output", str(tmp_path)]) == 0


def test_base_cycle_matches_the_python_constant():
    """``spiffy.mplstyle`` is hand-written, so pin its cycle here rather than
    generating a sheet whose other forty lines are hand-tuned."""
    with plt.style.context("spiffy"):
        cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    assert [color.upper() for color in cycle] == [
        color.upper() for color in colors.SPIFFY_CYCLE
    ]


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
    do this, but both are deprecated in matplotlib 3.11 and removed in 3.13.

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
