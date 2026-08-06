"""Core contracts for the bundled Matplotlib styles."""

import importlib
import shutil
import warnings

import matplotlib
import matplotlib.pyplot as plt

import spiffyplots
from spiffyplots import _genstyles, colors


def test_every_shipped_style_registers_and_renders():
    style_names = {path.stem for path in spiffyplots.STYLES_PATH.rglob("*.mplstyle")}

    assert style_names
    assert style_names <= set(matplotlib.style.available)
    for alias, target in spiffyplots.STYLE_ALIASES.items():
        assert matplotlib.style.library[alias] == matplotlib.style.library[target]

    for style in sorted(style_names):
        if style.startswith("latex") and shutil.which("latex") is None:
            continue
        with plt.style.context(style):
            figure, axis = plt.subplots()
            axis.plot([0, 1], [0, 1], label="line")
            axis.imshow([[0, 1]], alpha=0.1)
            axis.legend()
            figure.canvas.draw()
            plt.close(figure)


def test_spiffy_style_keeps_its_visual_and_export_contract(tmp_path):
    pdf_path = tmp_path / "spiffy.pdf"
    svg_path = tmp_path / "spiffy.svg"

    with plt.style.context("spiffy"):
        assert plt.rcParams["figure.figsize"] == [4.0, 2.5]
        assert plt.rcParams["axes.linewidth"] == 0.5
        assert plt.rcParams["axes.spines.top"] is False
        assert plt.rcParams["axes.spines.right"] is False
        assert plt.rcParams["axes.labelsize"] == 7.0
        assert plt.rcParams["xtick.labelsize"] == 6.0
        assert plt.rcParams["image.cmap"] == "tol.iridescent"
        assert plt.rcParams["axes.prop_cycle"].by_key()["color"] == list(
            colors.SPIFFY_CYCLE
        )

        figure, axis = plt.subplots()
        axis.set_xlabel("editable text")
        figure.savefig(pdf_path)
        figure.savefig(svg_path)

    assert b"/Type3" not in pdf_path.read_bytes()
    assert "<text" in svg_path.read_text()


def test_latex_modifiers_select_the_intended_font_setup():
    with plt.style.context(["spiffy", "latex"]):
        assert plt.rcParams["text.usetex"] is True
        assert plt.rcParams["font.sans-serif"][0] == "Computer Modern Sans Serif"

    with plt.style.context(["spiffy", "latex-helvetica"]):
        assert plt.rcParams["text.usetex"] is True
        assert plt.rcParams["font.sans-serif"][0] == "Helvetica"
        assert "sfmath" in plt.rcParams["text.latex.preamble"]


def test_generated_color_styles_match_the_python_palettes():
    generated = _genstyles.generate()
    shipped = {
        path.name: path.read_text()
        for path in (spiffyplots.STYLES_PATH / "color").glob("*.mplstyle")
    }

    assert shipped == generated


def test_style_registration_uses_no_deprecated_matplotlib_api():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(spiffyplots)

    deprecations = [
        str(entry.message)
        for entry in caught
        if issubclass(entry.category, matplotlib.MatplotlibDeprecationWarning)
    ]
    assert not deprecations
