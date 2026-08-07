"""Generate the colour and journal style sheets from their Python definitions.

.. code-block:: console

    python -m spiffyplots._genstyles           # rewrite the sheets
    python -m spiffyplots._genstyles --check   # fail if they are out of date
"""

import argparse
import sys
from pathlib import Path

from . import colors, journals
from ._units import MM

#: Where the generated sheets are written.
STYLES_PATH = Path(__file__).parent / "styles"

#: Subdirectories this script owns, relative to :data:`STYLES_PATH`.
GENERATED_DIRS = ("color", "journal")

TOL_URL = "https://sronpersonalpages.nl/~pault/"
OKABE_ITO_URL = "https://jfly.uni-koeln.de/color/"

# filename stem -> (scheme, title, credit)
SHEETS = {
    "tol-bright": (colors.tol_bright, "Paul Tol's bright scheme", TOL_URL),
    "tol-high-contrast": (
        colors.tol_high_contrast,
        "Paul Tol's high-contrast scheme",
        TOL_URL,
    ),
    "tol-light": (colors.tol_light, "Paul Tol's light scheme", TOL_URL),
    "tol-medium-contrast": (
        colors.tol_medium_contrast,
        "Paul Tol's medium-contrast scheme",
        TOL_URL,
    ),
    "tol-muted": (colors.tol_muted, "Paul Tol's muted scheme", TOL_URL),
    "tol-vibrant": (colors.tol_vibrant, "Paul Tol's vibrant scheme", TOL_URL),
    "okabe-ito": (colors.okabe_ito, "Okabe and Ito (2002)", OKABE_ITO_URL),
}


def render(scheme, title: str, credit: str) -> str:
    """The text of one colour sheet."""
    values = ", ".join(f"'{color.lstrip('#')}'" for color in scheme)
    return "\n".join(
        [
            f"# {title}. {len(scheme)} colours, colour-blind safe.",
            f"# Order: {', '.join(scheme.names)}.",
            f"# Credit: {credit}",
            "#",
            "# Generated from spiffyplots.colors by `python -m spiffyplots._genstyles`.",
            "# Edit the colour data there, not this file.",
            "",
            f"axes.prop_cycle : cycler('color', [{values}])",
            "",
        ]
    )


def render_journal(journal: journals.Journal) -> str:
    """The text of one journal sheet."""
    kind = journal.default_kind
    width_mm = journal.width(kind)
    size = journal.figsize(kind)

    widths = ", ".join(f"{mm:g} mm {name}" for mm, name in journal.widths.values())
    header = [f"# {journal.title}: {widths}."]
    if journal.max_height is not None:
        header.append(f"# Maximum height {journal.max_height:g} mm.")
    if journal.font_range is not None:
        header.append(f"# Text {journal.font_range[0]:g}-{journal.font_range[1]:g} pt.")
    if journal.panel_label is not None:
        label_size, weight, case = journal.panel_label
        header.append(f"# Panel letters {label_size:g} pt {weight} {case}.")

    body = [
        (
            f"figure.figsize : {size[0]:.4f}, {size[1]:.4f}"
            f"   # {width_mm:g} x {size[1] / MM:.4g} mm"
        ),
    ]

    if journal.font_size is not None:
        if journal.font_range is not None:
            reason = (
                f"# {journal.font_size:g} and {journal.label_size:g} pt sit inside "
                f"the {journal.font_range[0]:g}-{journal.font_range[1]:g} pt range"
            )
        else:
            reason = (
                f"# {journal.title} publishes no figure font size, so "
                f"{journal.font_size:g} and {journal.label_size:g} pt are spiffy's"
            )
        body += ["", f"{reason}; change them freely."]
        body += _font_lines(journal.font_size, journal.label_size)

    body += [
        "",
        "pdf.fonttype : 42",
        "ps.fonttype  : 42",
        "svg.fonttype : none",
    ]
    if journal.dpi is not None:
        body.append(f"savefig.dpi  : {journal.dpi}")

    return "\n".join(
        [
            *header,
            f"# Source, checked {journal.checked}:",
            f"# {journal.source}",
            "#",
            "# Generated from spiffyplots.journals by `python -m spiffyplots._genstyles`.",
            "# Edit the spec there, not this file.",
            "",
            *body,
            "",
        ]
    )


def _font_lines(font_size: float, label_size: float) -> list[str]:
    sizes = {
        "font.size": font_size,
        "axes.labelsize": label_size,
        "axes.titlesize": label_size,
        "xtick.labelsize": font_size,
        "ytick.labelsize": font_size,
        "legend.fontsize": font_size,
        "legend.title_fontsize": font_size,
        "figure.titlesize": label_size,
        "figure.labelsize": label_size,
    }
    width = max(len(key) for key in sizes)
    return [f"{key:<{width}} : {value:g}" for key, value in sizes.items()]


def generate() -> dict[str, str]:
    """Every sheet's path, relative to ``styles/``, mapped to its text."""
    sheets = {
        f"color/{stem}.mplstyle": render(*definition)
        for stem, definition in SHEETS.items()
    }
    sheets.update(
        {
            f"journal/{journal.style}.mplstyle": render_journal(journal)
            for journal in journals.JOURNALS.values()
        }
    )
    return sheets


def main(argv: list[str] | None = None) -> int:
    """Write the sheets, or check the shipped ones are up to date."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero if any sheet is out of date",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=STYLES_PATH,
        help=f"directory to write into (default: {STYLES_PATH})",
    )
    args = parser.parse_args(argv)

    sheets = generate()
    problems = []

    for name, text in sheets.items():
        path = args.output / name
        current = path.read_text() if path.is_file() else None
        if current == text:
            continue
        if args.check:
            problems.append(f"out of date: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            print(f"wrote {path}")

    for directory in GENERATED_DIRS:
        if not (args.output / directory).is_dir():
            continue
        problems += [
            f"not generated by this script: {path}"
            for path in sorted((args.output / directory).glob("*.mplstyle"))
            if f"{directory}/{path.name}" not in sheets
        ]

    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print("Run `python -m spiffyplots._genstyles` to regenerate.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
