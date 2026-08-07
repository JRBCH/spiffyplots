import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

# The demo. The two typed rows start empty; every other row is constant
IMPORT_LINE = "import spiffyplots"
STYLE_LINE = 'plt.style.use("spiffy")'
CODE_LINES = (
    "import matplotlib.pyplot as plt",
    IMPORT_LINE,
    STYLE_LINE,
    "",
    'fig, ax = plt.subplots(1, 2, layout="constrained")',
    "ax[0].plot(t, y)",
    'ax[0].set(xlabel="time (s)", ylabel="value")',
    "ax[1].hist(v)",
    'ax[1].set(xlabel="value", ylabel="count")',
)
TYPED_ROWS = (CODE_LINES.index(IMPORT_LINE), CODE_LINES.index(STYLE_LINE))

# DATA PARAMS
SEED = 0
N_SAMPLES = 400
N_HIST = 600
N_SERIES = 3
PHASES = (0.0, 0.8, 1.6)
NOISE = 0.09
HIST_BINS = 20

# PLOTTING / RENDERING PARAMS
CM = 1 / 2.54
FIG_SIZE_IN = (8 * CM, 4 * CM)
CODE_FONT_PX = 26
LINE_HEIGHT = 39
CODE_PAD = 28
CORNER_RADIUS = 12
MARGIN = 28
GAP = 40

# CODE PANEL COLORS
FRAME_BG = "#FFFFFF"
CODE_BG = "#F6F8FA"
CODE_BORDER = "#D0D7DE"
CARET = "#0077BB"
CARET_WIDTH = 3

# GitHub's light syntax theme, most specific token type first.
TEXT_COLOR = "#1F2328"
TOKEN_COLORS = (
    (Token.Comment, "#6E7781"),
    (Token.Keyword, "#CF222E"),
    (Token.Literal.String, "#0A3069"),
    (Token.Literal.Number, "#0550AE"),
)

HOLD_BEFORE_MS = 1800
TYPE_MS = 60
BEAT_MS = 400
HOLD_AFTER_MS = 3200

GIF_COLORS = 255
OUTPUT = Path(__file__).resolve().parent / "demo.gif"

FONT_PATH = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSansMono.ttf"
FONT = ImageFont.truetype(str(FONT_PATH), CODE_FONT_PX)
ADVANCE = FONT.getlength("M")


def token_color(ttype):
    for parent, color in TOKEN_COLORS:
        if ttype in parent:
            return color
    return TEXT_COLOR


def tokenize(line):
    """Colour spans for a line, lexed whole so a half-typed string still highlights."""
    spans = []
    for ttype, text in lex(line, PythonLexer()):
        text = text.rstrip("\n")
        if text:
            spans.append((token_color(ttype), text))
    return spans


CODE_SPANS = [tokenize(line) for line in CODE_LINES]
CODE_WIDTH = int(max(FONT.getlength(line) for line in CODE_LINES)) + 2 * CODE_PAD
CODE_HEIGHT = LINE_HEIGHT * len(CODE_LINES) + 2 * CODE_PAD
# Whatever DPI makes the figure as wide as the code panel.
DPI = CODE_WIDTH / FIG_SIZE_IN[0]
PLOT_SIZE = (CODE_WIDTH, round(FIG_SIZE_IN[1] * DPI))
FRAME_SIZE = (
    2 * MARGIN + CODE_WIDTH + GAP + PLOT_SIZE[0],
    2 * MARGIN + max(CODE_HEIGHT, PLOT_SIZE[1]),
)


def make_data():
    rng = np.random.default_rng(SEED)
    t = np.linspace(0, 10, N_SAMPLES)
    y = np.sin(t[:, None] + np.array(PHASES)) + NOISE * rng.standard_normal(
        (N_SAMPLES, N_SERIES)
    )
    v = rng.standard_normal(N_HIST)
    return t, y, v


def render_plot(style, data):
    """The demo snippet, run verbatim under `style`, as an image."""
    t, y, v = data
    with plt.style.context(style):
        fig, ax = plt.subplots(1, 2, figsize=FIG_SIZE_IN, layout="constrained")
        ax[0].plot(t, y)
        ax[0].set(xlabel="time (s)", ylabel="value")
        ax[1].hist(v)
        ax[1].set(xlabel="value", ylabel="count")
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=DPI)
        plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")


def render_code(typed, caret_row):
    """The code panel, showing `typed[row]` characters on each row that types in."""
    panel = Image.new("RGB", (CODE_WIDTH, CODE_HEIGHT), CODE_BG)
    draw = ImageDraw.Draw(panel)
    draw.rounded_rectangle(
        (0, 0, CODE_WIDTH - 1, CODE_HEIGHT - 1),
        radius=CORNER_RADIUS,
        outline=CODE_BORDER,
        width=2,
    )

    for row, spans in enumerate(CODE_SPANS):
        y = CODE_PAD + row * LINE_HEIGHT
        budget = typed.get(row)
        x = CODE_PAD
        for color, text in spans:
            if budget is not None:
                text = text[:budget]
                budget -= len(text)
            if text:
                draw.text((x, y), text, font=FONT, fill=color)
                x += FONT.getlength(text)
            if budget == 0:
                break

    caret_x = CODE_PAD + typed[caret_row] * ADVANCE
    caret_y = CODE_PAD + caret_row * LINE_HEIGHT
    draw.rectangle(
        (caret_x, caret_y, caret_x + CARET_WIDTH, caret_y + CODE_FONT_PX),
        fill=CARET,
    )
    return panel


def compose(code, plot):
    frame = Image.new("RGB", FRAME_SIZE, FRAME_BG)
    inner = FRAME_SIZE[1] - 2 * MARGIN
    frame.paste(code, (MARGIN, MARGIN + (inner - CODE_HEIGHT) // 2))
    frame.paste(plot, (MARGIN + CODE_WIDTH + GAP, MARGIN + (inner - PLOT_SIZE[1]) // 2))
    return frame


def build_frames():
    data = make_data()
    before = render_plot("default", data)
    after = render_plot("spiffy", data)

    typed = dict.fromkeys(TYPED_ROWS, 0)
    frames = [(compose(render_code(typed, TYPED_ROWS[0]), before), HOLD_BEFORE_MS)]
    for row in TYPED_ROWS:
        line = CODE_LINES[row]
        for count in range(1, len(line) + 1):
            typed = {**typed, row: count}
            wait = BEAT_MS if count == len(line) else TYPE_MS
            frames.append((compose(render_code(typed, row), before), wait))
    frames.append((compose(render_code(typed, TYPED_ROWS[-1]), after), HOLD_AFTER_MS))
    return frames


def to_palette(frames):
    """One palette for every frame, so colours hold still and GIF deltas stay small."""
    stack = Image.new("RGB", (FRAME_SIZE[0], FRAME_SIZE[1] * len(frames)))
    for index, frame in enumerate(frames):
        stack.paste(frame, (0, index * FRAME_SIZE[1]))
    palette = stack.quantize(colors=GIF_COLORS, dither=Image.Dither.NONE)
    return [
        frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames
    ]


def main():
    frames = build_frames()
    images = to_palette([frame for frame, _ in frames])
    images[0].save(
        OUTPUT,
        save_all=True,
        append_images=images[1:],
        duration=[duration for _, duration in frames],
        loop=0,
        disposal=1,
        optimize=True,
    )
    print(f"{OUTPUT} ({OUTPUT.stat().st_size / 1e3:.0f} kB, {len(images)} frames)")


if __name__ == "__main__":
    main()
