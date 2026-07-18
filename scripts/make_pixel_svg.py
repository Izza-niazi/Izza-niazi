#!/usr/bin/env python3
"""Render a fun retro pixel-art banner SVG (self-hosted, SMIL-animated).

Pixel text "IZZA NIAZI" materializes left-to-right, a CRT scanline shimmers
across it, twinkling star pixels blink, two space invaders march, and a
"PRESS START" line blinks. All motion is SMIL, so GitHub plays it from an
<img>. Pair it with the interactive <details> menu in the README.

    python scripts/make_pixel_svg.py     # writes pixel-banner.svg
"""

# 5x7 uppercase pixel font — only the glyphs we need.
FONT = {
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10101", "10011", "10001", "10001"],
    " ": ["00000"] * 7,
}

# Two classic "crab" invader frames (11x8), legs alternate.
INVADER_A = [
    "00100000100",
    "00010001000",
    "00111111100",
    "01101110110",
    "11111111111",
    "10111111101",
    "10100000101",
    "00011011000",
]
INVADER_B = [
    "00100000100",
    "10010001001",
    "10111111101",
    "11011101101",
    "11111111111",
    "01111111110",
    "00100000100",
    "01000000010",
]

TEXT = "IZZA NIAZI"
PX = 8            # pixel size for the title text
IPX = 4           # pixel size for invaders
BG = "#0d1117"
GREEN = "#39d353"
PINK = "#ff6ac1"
STAR = "#c8ced6"
WIDTH = 720


def draw_bitmap(rows, ox, oy, px, fill, reveal=None):
    """Emit <rect> for every '1' pixel. reveal=(begin_fn) animates opacity in."""
    out = []
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != "1":
                continue
            x = ox + c * px
            y = oy + r * px
            if reveal is not None:
                b = reveal(c, r)
                out.append(
                    f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{fill}" opacity="0">'
                    f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" '
                    f'dur="0.28s" fill="freeze"/></rect>'
                )
            else:
                out.append(f'<rect x="{x}" y="{y}" width="{px}" height="{px}" fill="{fill}"/>')
    return out


def invader(ox, oy, fill, march, bob_begin):
    """A marching invader that alternates leg frames and slides left<->right."""
    a = "".join(draw_bitmap(INVADER_A, 0, 0, IPX, fill))
    b = "".join(draw_bitmap(INVADER_B, 0, 0, IPX, fill))
    return (
        f'<g transform="translate({ox} {oy})">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="{ox} {oy};{ox + march} {oy};{ox} {oy}" dur="4s" '
        f'repeatCount="indefinite" additive="replace"/>'
        f'<g><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
        f'dur="0.7s" begin="{bob_begin}s" repeatCount="indefinite"/>{a}</g>'
        f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1" '
        f'keyTimes="0;0.5;0.5;1" dur="0.7s" begin="{bob_begin}s" repeatCount="indefinite"/>{b}</g>'
        f'</g>'
    )


def main(out: str = "pixel-banner.svg") -> None:
    # ---- title geometry ----
    char_w = 5 + 1                       # 5 px cols + 1 col gap
    total_cols = len(TEXT) * char_w - 1
    text_w = total_cols * PX
    text_x = (WIDTH - text_w) // 2
    text_y = 66
    text_h = 7 * PX

    height = 190

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" '
        f'font-family="\'Cascadia Code\',monospace">',
        f'<rect width="{WIDTH}" height="{height}" fill="{BG}"/>',
    ]

    # ---- twinkling stars (deterministic positions) ----
    stars = [(40, 24), (120, 46), (200, 18), (300, 40), (410, 22), (520, 44),
             (610, 20), (680, 40), (90, 150), (250, 162), (470, 150),
             (560, 165), (650, 152), (160, 138)]
    for i, (sx, sy) in enumerate(stars):
        p.append(
            f'<rect x="{sx}" y="{sy}" width="3" height="3" fill="{STAR}">'
            f'<animate attributeName="opacity" values="0.15;1;0.15" '
            f'dur="{1.4 + (i % 5) * 0.25:.2f}s" begin="{i * 0.2:.2f}s" '
            f'repeatCount="indefinite"/></rect>'
        )

    # ---- marching invaders ----
    p.append(invader(70, 18, GREEN, 34, 0))
    p.append(invader(600, 138, PINK, -34, 0.35))

    # ---- pixel title with left-to-right reveal ----
    reveal_total = 0.0
    gc = 0
    for ch in TEXT:
        glyph = FONT.get(ch, FONT[" "])
        ox = text_x + gc * PX
        p.extend(draw_bitmap(glyph, ox, text_y, PX,
                             GREEN, reveal=lambda c, r, base=gc: (base + c) * 0.02 + r * 0.004))
        gc += char_w
    reveal_total = total_cols * 0.02 + 1.0

    # ---- CRT scanline shimmer sweeping across the title (starts after reveal) ----
    p.append(
        f'<rect x="{text_x}" y="{text_y - 4}" width="18" height="{text_h + 8}" '
        f'fill="#ffffff" opacity="0.10">'
        f'<animate attributeName="x" from="{text_x - 20}" to="{text_x + text_w}" '
        f'begin="{reveal_total:.2f}s" dur="2.6s" repeatCount="indefinite"/></rect>'
    )

    # ---- blinking PRESS START ----
    p.append(
        f'<text x="{WIDTH // 2}" y="{height - 22}" text-anchor="middle" fill="{GREEN}" '
        f'font-size="16" font-weight="bold" letter-spacing="3">'
        f'<tspan fill="{PINK}">▸</tspan> PRESS START <tspan fill="{PINK}">◂</tspan>'
        f'<animate attributeName="opacity" values="1;1;0.15;0.15" keyTimes="0;0.5;0.5;1" '
        f'dur="1.1s" begin="{reveal_total:.2f}s" repeatCount="indefinite"/></text>'
    )

    p.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"wrote {out}  (\"{TEXT}\", reveal ~{reveal_total:.1f}s)")


if __name__ == "__main__":
    main()
