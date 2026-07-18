#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing monochrome ASCII SVG.

Each pixel's brightness picks a glyph from a density ramp (bright -> sparse,
dark -> dense). The result is rendered as rows of monospace text; each row is
revealed by a left-to-right clip wipe with a small block "cursor" riding the
edge, staggered top to bottom. Plays once via SMIL, then freezes.

    python scripts/make_ascii_svg.py            # reads source-prepped.png
    python scripts/make_ascii_svg.py in.png out.svg

GitHub strips <script> and inline CSS from READMEs but DOES run SMIL inside an
SVG embedded via <img>, which is why the animation lives entirely in the file.
"""
import sys
from xml.sax.saxutils import escape

from PIL import Image

# Bright (sparse) -> dark (dense). Leading space clears the white background.
RAMP = " .`:-=+*cs#%@"

COLS = 100          # character columns
ROWS = 53           # character rows
CHAR_W = 6.0        # px advance per glyph
LINE_H = 11.0       # px per row  (~2x CHAR_W keeps the portrait square-ish)
FONT_SIZE = 10
FILL = "#c8ced6"    # one light-grey fill — monochrome reads clean, not noisy
BG = "#0d1117"      # GitHub dark canvas
CURSOR = "#39d353"

ROW_DUR = 0.40      # seconds for one row to wipe in
ROW_STAGGER = 0.055 # delay added per row


def brightness_to_glyph(v: int) -> str:
    # v in 0..255 ; 255 (white) -> first ramp char (space)
    idx = int((255 - v) / 255 * (len(RAMP) - 1) + 0.5)
    return RAMP[min(max(idx, 0), len(RAMP) - 1)]


def main(src: str = "source-prepped.png", out: str = "avi-ascii.svg") -> None:
    img = Image.open(src).convert("L").resize((COLS, ROWS))
    px = img.load()

    rows = []
    for y in range(ROWS):
        rows.append("".join(brightness_to_glyph(px[x, y]) for x in range(COLS)))

    w = COLS * CHAR_W
    h = ROWS * LINE_H
    total = ROWS * ROW_STAGGER + ROW_DUR

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" font-family="\'Cascadia Code\',\'Courier New\',monospace" '
        f'font-size="{FONT_SIZE}">',
        f'<rect width="{w:.0f}" height="{h:.0f}" fill="{BG}"/>',
        f'<g fill="{FILL}" xml:space="preserve" '
        f'style="font-variant-ligatures:none;letter-spacing:0">',
    ]

    for i, line in enumerate(rows):
        begin = i * ROW_STAGGER
        y = (i + 1) * LINE_H - 2
        clip = f"clip{i}"
        # A clip rect grows from width 0 to full width -> left-to-right wipe.
        parts.append(
            f'<clipPath id="{clip}"><rect x="0" y="{i * LINE_H:.1f}" height="{LINE_H:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{w:.0f}" '
            f'begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(
            f'<text x="0" y="{y:.1f}" clip-path="url(#{clip})" '
            f'textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs">{escape(line)}</text>'
        )
        # Block cursor rides the wipe edge, then vanishes.
        parts.append(
            f'<rect y="{i * LINE_H:.1f}" width="{CHAR_W:.1f}" height="{LINE_H:.1f}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{w - CHAR_W:.1f}" '
            f'begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.05;0.95;1" '
            f'begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/></rect>'
        )

    parts.append("</g>")
    parts.append(
        f'<!-- total reveal ~{total:.1f}s, plays once and freezes -->'
    )
    parts.append("</svg>")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"wrote {out}  ({COLS}x{ROWS} chars, reveal ~{total:.1f}s)")


if __name__ == "__main__":
    a = sys.argv
    main(a[1] if len(a) > 1 else "source-prepped.png",
         a[2] if len(a) > 2 else "avi-ascii.svg")
