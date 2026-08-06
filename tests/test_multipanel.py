"""Public MultiPanel behavior."""

import re
import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

from spiffyplots import MultiPanel


def test_shape_layout_exposes_panels_by_position_and_label():
    figure = MultiPanel(shape=(1, 2), labels=["left", "right"])

    assert figure.shape == (1, 2)
    assert len(figure.panels) == 2
    assert figure.panels["left"] is figure.panels[0]
    assert figure.panels.right is figure.panels[1]
    with pytest.raises(TypeError):
        figure.panels[0] = figure.panels[1]


def test_grid_layouts_compute_the_expected_raster():
    rows = MultiPanel(grid=[3, 2])
    spans = MultiPanel(grid=[(0, 0), (range(2), 1)])

    assert rows.shape == (2, 6)
    assert len(rows.panels) == 5
    assert spans.shape == (2, 2)
    assert spans.panels[1].get_subplotspec().rowspan.start == 0
    assert spans.panels[1].get_subplotspec().rowspan.stop == 2


def test_label_grid_defines_spanning_named_panels():
    figure = MultiPanel(labels=[["main", "side"], ["main", "lower"]])

    assert figure.shape == (2, 2)
    assert len(figure.panels) == 3
    assert figure.panels.main is figure.panels[0]
    assert figure.panels.main.get_subplotspec().rowspan.stop == 2

    with pytest.raises(TypeError, match="adjacent"):
        MultiPanel(labels=[["A", "B"], ["B", "A"]])


def test_panel_labels_follow_the_requested_style():
    with matplotlib.rc_context({"axes.labelsize": 9}):
        figure = MultiPanel(
            shape=(1, 2),
            labels=True,
            label_case="uppercase",
            label_offset=(-12, 4),
            label_color="green",
        )

    labels = [panel.texts[0] for panel in figure.panels]
    assert [label.get_text() for label in labels] == ["A", "B"]
    assert labels[0].xyann == (-12, 4)
    assert labels[0].get_fontsize() == 9
    assert labels[0].get_color() == "green"


def test_figure_units_dpi_and_grid_ratios_are_forwarded():
    figure = MultiPanel(
        shape=(1, 2),
        figsize=(25.4, 50.8),
        units="mm",
        dpi=144,
        width_ratios=(1, 2),
    )

    np.testing.assert_allclose(figure.fig.get_size_inches(), (1, 2))
    assert figure.fig.dpi == 144
    assert figure.gridspec.get_width_ratios() == (1, 2)


def test_layout_conflicts_and_overlaps_warn():
    with pytest.warns(UserWarning, match="coordinates overlap"):
        MultiPanel(grid=[(0, 0), (0, 0)])

    with (
        matplotlib.style.context("spiffy"),
        pytest.warns(UserWarning, match="mutually exclusive"),
    ):
        MultiPanel(shape=(1, 2), left=0.2)


def test_invalid_arguments_fail_before_leaking_a_figure():
    before = set(plt.get_fignums())

    with pytest.raises(TypeError, match="unexpected keyword arguments"):
        MultiPanel(figsizee=(4, 3))
    with pytest.raises(ValueError, match="expected 'in', 'cm', or 'mm'"):
        MultiPanel(units="pt")

    assert set(plt.get_fignums()) == before


def test_savefig_and_close_delegate_to_the_wrapped_figure(tmp_path):
    figure = MultiPanel(shape=(1, 1))
    figure_number = figure.fig.number
    output = tmp_path / "figure.pdf"

    figure.savefig(output)
    assert output.read_bytes().startswith(b"%PDF")

    figure.close()
    assert figure_number not in plt.get_fignums()


def test_explicit_size_is_exact_without_tight_bbox_and_tight_bbox_warns(tmp_path):
    figure = MultiPanel(shape=(1, 1), figsize=(89, 60), units="mm")
    exact_output = tmp_path / "exact.pdf"

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        figure.savefig(exact_output)

    media_box = re.search(
        rb"/MediaBox\s*\[\s*0\s+0\s+([0-9.]+)\s+([0-9.]+)\s*\]",
        exact_output.read_bytes(),
    )
    assert media_box is not None
    width_pt, height_pt = map(float, media_box.groups())
    assert width_pt * 25.4 / 72 == pytest.approx(89)
    assert height_pt * 25.4 / 72 == pytest.approx(60)

    with pytest.warns(
        UserWarning,
        match=r"Declared 89\.0 x 60\.0 mm.*Drop `bbox_inches`",
    ):
        figure.savefig(tmp_path / "tight.pdf", bbox_inches="tight")


def test_tight_bbox_warning_respects_defaults_and_rcparams(tmp_path):
    default_figure = MultiPanel(shape=(1, 1))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        default_figure.savefig(tmp_path / "default-tight.pdf", bbox_inches="tight")

    explicit_figure = MultiPanel(shape=(1, 1), figsize=(8.9, 6), units="cm")
    with (
        matplotlib.rc_context({"savefig.bbox": "tight"}),
        pytest.warns(UserWarning, match=r"Declared 8\.9 x 6\.0 cm"),
    ):
        explicit_figure.savefig(tmp_path / "rc-tight.pdf")
