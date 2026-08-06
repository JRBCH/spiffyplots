"""Figure specifications from journal author guidelines.

Every entry carries the source it was read from and the date it was checked. 
Claude code extracted this, so take it with a grain of salt, but I checked
the numbers against the source and they seem correct. The
style sheets in ``styles/journal`` are generated from this table.

    >>> from spiffyplots import journals
    >>> journals.nature.width("single")
    89.0
    >>> journals.nature.single_column(height=65)
    (3.5039370078740157, 2.5590551181102366)

Print a journal for the full specification::

    >>> import spiffyplots as spiffy
    >>> spiffy.journals.nature                                
"""

import textwrap
from collections.abc import Mapping
from dataclasses import dataclass, field

from ._units import figsize as _figsize
from ._units import to_inches as _to_inches

__all__ = ["ALIASES", "JOURNALS", "Journal", "available", "get"]

#: Height of a default figure, as a fraction of its width. Spiffy's own 4:2.5.
DEFAULT_ASPECT = 1.6

_CHECKED = "2026-08-06"

_LABEL_WIDTH = 15
_WRAP = 72


def _num(value: float) -> str:
    return f"{value:g}"


def _row(label: str, value: str) -> str:
    lines = textwrap.wrap(
        value, width=_WRAP, break_long_words=False, break_on_hyphens=False
    )
    indent = " " * (2 + _LABEL_WIDTH)
    head = f"  {label:<{_LABEL_WIDTH}}{lines[0]}"
    return "\n".join([head, *(indent + line for line in lines[1:])])


@dataclass(frozen=True)
class Journal:
    """One venue's published figure specification.

    Widths are millimetres. ``font_size`` and ``label_size`` are spiffy's picks
    inside ``font_range``, or ``None`` where the venue publishes no range and the
    base style should carry through.
    """

    title: str
    style: str
    #: Width kind (``single``, ``one_half``, ``double``) to millimetres and the
    #: venue's own name for it.
    widths: Mapping[str, tuple[float, str]]
    source: str
    export: str
    checked: str = _CHECKED
    max_height: float | None = None
    font_range: tuple[float, float] | None = None
    font_size: float | None = None
    label_size: float | None = None
    #: Panel letters as ``(size, weight, case)``.
    panel_label: tuple[float, str, str] | None = None
    font_family: str | None = None
    dpi: int | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def default_kind(self) -> str:
        """The width a bare ``plt.style.use`` gives you: double column, or the
        only width for a single-column venue."""
        return "double" if "double" in self.widths else "single"

    def width(self, kind: str = "single", *, units: str = "mm") -> float:
        """The published width, in ``units``.

        Args:
            kind: ``"single"``, ``"one_half"`` or ``"double"``.
            units: ``"in"``, ``"cm"`` or ``"mm"``. Defaults to ``"mm"``.
        """
        return _to_inches(self._width_mm(kind), "mm") / _to_inches(1.0, units)

    def figsize(
        self, kind: str = "single", height: float | None = None, *, units: str = "mm"
    ) -> tuple[float, float]:
        """A ``(width, height)`` in inches, ready for ``figsize=``.

        Args:
            kind: ``"single"``, ``"one_half"`` or ``"double"``.
            height: Height in ``units``. Defaults to the width over
                :data:`DEFAULT_ASPECT`, capped at the venue's maximum height.
            units: Unit of ``height``: ``"in"``, ``"cm"`` or ``"mm"``. Defaults
                to ``"mm"``.
        """
        width_mm = self._width_mm(kind)
        if height is None:
            return _figsize(width_mm, self._default_height(width_mm), "mm")
        return _to_inches(width_mm, "mm"), _to_inches(height, units)

    def single_column(
        self, height: float | None = None, *, units: str = "mm"
    ) -> tuple[float, float]:
        """Single-column ``(width, height)`` in inches. See :meth:`figsize`."""
        return self.figsize("single", height, units=units)

    def one_half_column(
        self, height: float | None = None, *, units: str = "mm"
    ) -> tuple[float, float]:
        """1.5-column ``(width, height)`` in inches. See :meth:`figsize`."""
        return self.figsize("one_half", height, units=units)

    def double_column(
        self, height: float | None = None, *, units: str = "mm"
    ) -> tuple[float, float]:
        """Double-column ``(width, height)`` in inches. See :meth:`figsize`."""
        return self.figsize("double", height, units=units)

    def _width_mm(self, kind: str) -> float:
        try:
            return self.widths[kind][0]
        except (KeyError, TypeError):
            raise KeyError(
                f"{self.title} has no {kind!r} width. "
                f"Available: {', '.join(self.widths)}."
            ) from None

    def _default_height(self, width_mm: float) -> float:
        height = width_mm / DEFAULT_ASPECT
        if self.max_height is None:
            return height
        return min(height, self.max_height)

    def _widths_line(self) -> str:
        return ", ".join(f"{_num(mm)} mm {name}" for mm, name in self.widths.values())

    def _text_line(self) -> str:
        if self.font_range:
            stated = f"{_num(self.font_range[0])}-{_num(self.font_range[1])} pt"
        else:
            stated = "no size published"
        if self.font_family:
            stated += f", {self.font_family}"
        if self.font_size is None:
            return f"{stated}. Spiffy leaves its own sizes in place."
        return (
            f"{stated}. Spiffy uses {_num(self.font_size)} pt with "
            f"{_num(self.label_size)} pt labels; change freely."
        )

    def _panel_line(self) -> str:
        size, weight, case = self.panel_label
        return (
            f"{_num(size)} pt {weight} {case}. "
            f"Pass label_size={_num(size)} to MultiPanel."
        )

    def __repr__(self) -> str:
        rows = [("Widths", self._widths_line())]
        if self.max_height is not None:
            rows.append(("Max height", f"{_num(self.max_height)} mm"))
        rows.append(("Text", self._text_line()))
        if self.panel_label is not None:
            rows.append(("Panel letters", self._panel_line()))
        rows += [
            ("Export", self.export),
            ("Checked", self.checked),
            ("Source", self.source),
        ]

        attribute = self.style.replace("-", "_")
        blocks = [
            f'{self.title}  (style "{self.style}")',
            "\n".join(_row(label, value) for label, value in rows),
        ]
        blocks += [
            textwrap.fill(
                note, width=_WRAP + 2, initial_indent="  ", subsequent_indent="  "
            )
            for note in self.notes
        ]
        blocks.append(
            f'  plt.style.use(["spiffy", "{self.style}"])\n'
            f"  spiffy.journals.{attribute}."
            f"{self.default_kind}_column(height=...)  ->  figsize in inches"
        )
        return "\n\n".join(blocks)


#: Every journal, keyed by style-sheet name.
JOURNALS: dict[str, Journal] = {
    "nature": Journal(
        title="Nature",
        style="nature",
        widths={
            "single": (89.0, "single column"),
            "double": (183.0, "double column"),
        },
        max_height=170.0,
        font_range=(5.0, 7.0),
        font_size=6.0,
        label_size=7.0,
        panel_label=(8.0, "bold", "lowercase"),
        font_family="Helvetica or Arial",
        dpi=450,
        export="RGB, vector PDF or EPS, TrueType 42, text left editable",
        source=(
            "https://research-figure-guide.nature.com/figures/"
            "building-and-exporting-figure-panels/"
        ),
        notes=(
            (
                "The Nature-branded research journals (Nature Neuroscience, Nature "
                "Communications and the rest) publish 88 and 180 mm instead, and cap "
                "height by caption length: 130/185 mm under 300 words, 180/210 under "
                "150, 220/225 under 50."
            ),
        ),
    ),
    "science": Journal(
        title="Science",
        style="science",
        widths={
            "single": (90.0, "single column"),
            "double": (183.0, "double column"),
        },
        max_height=227.5,
        font_range=(6.0, 9.0),
        font_size=7.0,
        label_size=8.0,
        panel_label=(10.0, "bold", "uppercase"),
        font_family="Arial or Helvetica",
        dpi=500,
        export=(
            "RGB, vector AI, EPS or PDF, images at 300-500 dpi, "
            "nothing rasterized, flattened or outlined"
        ),
        source=(
            "https://www.science.org/cms/asset/62583409-a188-466e-8cc0-6fb5f083bbff/"
            "author_prep_guide_2025.pdf"
        ),
        notes=(
            (
                "Panel letters are the one exception to the 6-9 pt range. Keep to at "
                "most three type sizes in a figure. Minimum line weight 0.28 pt."
            ),
            (
                "The 227.5 mm page depth comes from the Science family revision "
                "guide, which also recommends staying under 199 mm at double column "
                "so the legend fits. Science Advances uses 184 mm for two columns "
                "and 9 pt panel letters."
            ),
        ),
    ),
    "cell": Journal(
        title="Cell Press",
        style="cell",
        widths={
            "single": (85.0, "single column"),
            "one_half": (114.0, "1.5 columns"),
            "double": (174.0, "full width"),
        },
        font_range=(6.0, 8.0),
        font_size=7.0,
        label_size=8.0,
        font_family="Arial or Helvetica",
        dpi=300,
        export="300 dpi colour and greyscale, 500 dpi black and white, "
        "1000 dpi line art",
        source="https://www.cell.com/figureguidelines",
        notes=(
            (
                "The two-column Cell Press journals, Cell and Neuron among them. "
                "`neuron` is an alias of this entry."
            ),
        ),
    ),
    "jneurosci": Journal(
        title="Journal of Neuroscience",
        style="jneurosci",
        widths={
            "single": (85.0, "single column"),
            "one_half": (116.0, "1.5 columns"),
            "double": (176.0, "double column"),
        },
        font_range=(6.0, 8.0),
        font_size=7.0,
        label_size=8.0,
        font_family="Helvetica or Arial",
        dpi=300,
        export="RGB, TIFF or EPS at 300 dpi, monochrome bitmaps at 1200 dpi",
        source="https://www.jneurosci.org/content/information-authors",
        notes=(
            "eNeuro publishes the same widths.",
            (
                "SfN asks for outlined fonts in EPS. Spiffy keeps text editable; "
                "outline it on export if their production insists."
            ),
        ),
    ),
    "elife": Journal(
        title="eLife",
        style="elife",
        widths={
            "single": (85.0, "single column"),
            "double": (170.0, "full width"),
        },
        dpi=300,
        export="RGB at 300 dpi, 100 mm minimum width, 200 mm for a full-page figure",
        source="https://elife-rp.msubmit.net/html/elife-rp_author_instructions.html",
        notes=(
            (
                "eLife publishes no column widths and no font sizes, only the upload "
                "minima above. 85 and 170 mm are spiffy's picks, not eLife's numbers; "
                "any width is fine."
            ),
        ),
    ),
    "plos-compbiol": Journal(
        title="PLOS Computational Biology",
        style="plos-compbiol",
        widths={
            "single": (132.0, "text column"),
            "double": (190.5, "full page"),
        },
        max_height=222.3,
        font_range=(8.0, 12.0),
        font_size=8.0,
        label_size=9.0,
        font_family="Arial, Times or Symbol only",
        dpi=300,
        export="TIFF or EPS at 300-600 dpi",
        source="https://journals.plos.org/ploscompbiol/s/figures",
        notes=(
            (
                "Accepted widths run from 66.8 to 190.5 mm. PLOS does not accept EPS "
                "generated by LaTeX."
            ),
        ),
    ),
    "jmlr": Journal(
        title="JMLR",
        style="jmlr",
        widths={"single": (152.4, "text width")},
        max_height=215.9,
        font_size=9.0,
        label_size=10.0,
        dpi=300,
        export="vector PDF, TrueType 42, text left editable",
        source="https://github.com/JmlrOrg/jmlr-style-file",
        notes=(
            "Single column, a 6.0 by 8.5 in text block, from jmlr2e.sty.",
            (
                "No figure font size is published. 9 pt sits one step below the 11 pt "
                "body text; change it freely."
            ),
        ),
    ),
    "tmlr": Journal(
        title="TMLR",
        style="tmlr",
        widths={"single": (165.1, "text width")},
        max_height=228.6,
        font_size=8.0,
        label_size=9.0,
        dpi=300,
        export="vector PDF, TrueType 42, text left editable",
        source="https://github.com/JmlrOrg/tmlr-style-file",
        notes=(
            "Single column, a 6.5 by 9 in text block, from tmlr.sty.",
            (
                "No figure font size is published. 8 pt sits one step below the 10 pt "
                "body text; change it freely."
            ),
        ),
    ),
}

#: Journals that share another's specification exactly.
ALIASES = {"neuron": "cell"}


def available() -> list[str]:
    """Every journal name, aliases included."""
    return sorted([*JOURNALS, *ALIASES])


def get(name: str) -> Journal:
    """Look a journal up by name. Underscores and hyphens are interchangeable."""
    key = name.replace("_", "-")
    try:
        return JOURNALS[ALIASES.get(key, key)]
    except KeyError:
        raise KeyError(
            f"Unknown journal {name!r}. Available: {', '.join(available())}."
        ) from None


nature = JOURNALS["nature"]
science = JOURNALS["science"]
cell = JOURNALS["cell"]
neuron = JOURNALS["cell"]
jneurosci = JOURNALS["jneurosci"]
elife = JOURNALS["elife"]
plos_compbiol = JOURNALS["plos-compbiol"]
jmlr = JOURNALS["jmlr"]
tmlr = JOURNALS["tmlr"]
