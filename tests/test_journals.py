"""The journal specification table and its figure-size API."""

import pytest

from spiffyplots import figsize, journals


def test_widths_convert_to_the_published_millimetres():
    assert journals.nature.width("single") == 89.0
    assert journals.nature.width("double", units="in") == pytest.approx(
        7.20472, abs=1e-5
    )
    assert journals.jmlr.width("single", units="in") == pytest.approx(6.0)


def test_figsize_helpers_match_the_unit_converter():
    assert journals.nature.single_column(height=65) == figsize(89, 65, "mm")
    assert journals.nature.double_column(height=4.5, units="in") == figsize(
        183, 4.5 * 25.4, "mm"
    )


def test_default_height_follows_the_house_aspect_and_respects_the_maximum():
    _, height = journals.nature.double_column()
    assert height == pytest.approx(183 / journals.DEFAULT_ASPECT / 25.4)

    tall = journals.Journal(
        title="Tall",
        style="tall",
        widths={"single": (200.0, "single column")},
        source="",
        export="",
        max_height=50.0,
    )
    assert tall.single_column()[1] == pytest.approx(50.0 / 25.4)


def test_missing_width_names_the_widths_that_exist():
    with pytest.raises(KeyError, match="no 'double' width.*single"):
        journals.jmlr.double_column()


def test_lookup_resolves_aliases_and_both_separators():
    assert journals.get("neuron") is journals.cell
    assert journals.get("plos_compbiol") is journals.get("plos-compbiol")
    assert "neuron" in journals.available()

    with pytest.raises(KeyError, match="Unknown journal 'nurture'"):
        journals.get("nurture")


def test_spiffy_font_picks_sit_inside_every_published_range():
    for journal in journals.JOURNALS.values():
        if journal.font_range is None or journal.font_size is None:
            continue
        low, high = journal.font_range
        assert low <= journal.font_size <= high, journal.style
        assert low <= journal.label_size <= high, journal.style


def test_summary_reports_the_geometry_and_its_source():
    summary = repr(journals.nature)

    assert "89 mm single column" in summary
    assert "183 mm double column" in summary
    assert "5-7 pt" in summary
    assert journals.nature.source in summary
    assert journals.nature.checked in summary
