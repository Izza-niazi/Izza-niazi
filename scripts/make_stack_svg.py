#!/usr/bin/env python3
"""Render an animated tech-stack SVG (self-hosted, replaces static shields).

Coloured pills that fade + slide in on a stagger, wrapping across rows and
centered. One-time reveal that freezes — same motion language as the info card
and streak card. GitHub plays the SMIL from an <img>.

    python scripts/make_stack_svg.py     # writes stack.svg

Edit TECHS below: (label, background, text-color).
"""
from xml.sax.saxutils import escape

# Frontend / mobile-leaning stack. Light backgrounds get dark text.
TECHS = [
    ("JavaScript",     "#F7DF1E", "#0d1117"),
    ("TypeScript",     "#3178C6", "#ffffff"),
    ("React",          "#20232A", "#61DAFB"),
    ("React Native",   "#087EA4", "#ffffff"),
    ("Expo",           "#1C2024", "#ffffff"),
    ("Redux",          "#764ABC", "#ffffff"),
    ("Node.js",        "#339933", "#ffffff"),
    ("HTML5",          "#E34F26", "#ffffff"),
    ("CSS3",           "#1572B6", "#ffffff"),
    ("Tailwind CSS",   "#06B6D4", "#0d1117"),
    ("Python",         "#3776AB", "#ffffff"),
    ("PostgreSQL",     "#4169E1", "#ffffff"),
    ("Docker",         "#2496ED", "#ffffff"),
    ("Git",            "#F05032", "#ffffff"),
    ("GitHub Actions", "#2088FF", "#ffffff"),
    ("AWS",            "#FF9900", "#0d1117"),
]

WIDTH = 860
FONT = 15
CHAR_W = FONT * 0.6
PAD_X = 15          # inner horizontal padding of a pill
PILL_H = 34
GAP = 10           # gap between pills in a row
ROW_GAP = 12
MARGIN_Y = 10
BG = "#0d1117"


def pill_width(label: str) -> int:
    return int(len(label) * CHAR_W + PAD_X * 2)


def main(out: str = "stack.svg") -> None:
    # Greedy wrap into centered rows.
    rows, row, row_w = [], [], 0
    for t in TECHS:
        w = pill_width(t[0])
        need = w + (GAP if row else 0)
        if row and row_w + need > WIDTH:
            rows.append((row, row_w))
            row, row_w = [], 0
            need = w
        row.append((t, w))
        row_w += need
    if row:
        rows.append((row, row_w))

    height = MARGIN_Y * 2 + len(rows) * PILL_H + (len(rows) - 1) * ROW_GAP

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" '
        f'font-family="\'Cascadia Code\',\'Segoe UI\',monospace" font-size="{FONT}">',
        f'<rect width="{WIDTH}" height="{height}" fill="{BG}"/>',
    ]

    idx = 0
    y = MARGIN_Y
    for row, total_w in rows:
        x = (WIDTH - total_w) / 2
        for (label, bg, fg), w in row:
            begin = idx * 0.07
            cx = x + w / 2
            ty = y + PILL_H / 2 + FONT * 0.35
            p.append(
                f'<g opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
                f'dur="0.4s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0 9" to="0 0" begin="{begin:.2f}s" dur="0.4s" fill="freeze" '
                f'calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                f'<rect x="{x:.1f}" y="{y}" width="{w}" height="{PILL_H}" rx="8" fill="{bg}" '
                f'stroke="#ffffff" stroke-opacity="0.08"/>'
                f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="{fg}" '
                f'font-weight="bold">{escape(label)}</text>'
                f'</g>'
            )
            x += w + GAP
            idx += 1
        y += PILL_H + ROW_GAP

    p.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"wrote {out}  ({len(TECHS)} techs, {len(rows)} rows)")


if __name__ == "__main__":
    main()
