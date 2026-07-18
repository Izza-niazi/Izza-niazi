#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG.

Looks like `neofetch` output: a title bar, then colored key/value rows. Each
line fades + slides in on a short stagger so the panel "prints" next to the
portrait. Set STATIC=1 to emit a frozen frame (handy for Quick Look previews).

    python scripts/make_info_card.py            # writes info-card.svg
    STATIC=1 python scripts/make_info_card.py   # no animation

EDIT THE CONTENT BELOW — the graph already covers your GitHub stats, so keep
this for the story numbers can't tell.
"""
import os
from xml.sax.saxutils import escape

# ---------------------------------------------------------------------------
# EDIT ME. Each row is (label, value). Keep values short so they fit the card.
# ---------------------------------------------------------------------------
HANDLE = "izza@github"
TITLE = "izza-niazi"

# Value can be a single string or a list of lines (rendered stacked).
ROWS = [
    ("Role",       "Software Engineer · Mobile & Web"),
    ("Now",        "Building AI-powered apps"),
    ("Prev",       "Frontend · Mobile apps · APIs"),
    ("Stack",      ["React Native · React",
                    "TypeScript · JavaScript · Python"]),
    ("Tools",      ["Git · GitHub Actions",
                    "Supabase · Firebase · Expo"]),
    ("Focus",      ["Mobile UX · Web apps",
                    "AI tools · Clean architecture"]),
    ("Learning",   ["System Design · LLMs",
                    "Open-source development"]),
    ("Highlights", ["Quantum Edge Mobile · Telemedicine",
                    "SharkStack · BeanMachine",
                    "Full-stack builder"]),
]
# ---------------------------------------------------------------------------

BG = "#0d1117"
BORDER = "#30363d"
KEY = "#39d353"       # neofetch-green labels
VALUE = "#c8ced6"
TITLE_C = "#58a6ff"
DIM = "#8b949e"

PAD = 22
FONT = 14
LINE_H = 26
KEY_W = 118           # px reserved for the label column

STATIC = os.environ.get("STATIC") == "1"


def anim(delay: float) -> str:
    if STATIC:
        return ""
    return (
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
        f'dur="0.35s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="10 0" to="0 0" begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
    )


def main(out: str = "info-card.svg") -> None:
    header_lines = 2          # title bar + underline
    total_value_lines = sum(len(v if isinstance(v, list) else [v]) for _, v in ROWS)
    height = PAD * 2 + (header_lines * LINE_H) + (total_value_lines * LINE_H) + 8
    width = 620

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'font-family="\'Cascadia Code\',\'Courier New\',monospace" font-size="{FONT}">',
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # window dots
        f'<circle cx="20" cy="20" r="5" fill="#ff5f56"/>'
        f'<circle cx="38" cy="20" r="5" fill="#ffbd2e"/>'
        f'<circle cx="56" cy="20" r="5" fill="#27c93f"/>',
    ]

    y = PAD + 34
    op = '' if STATIC else ' opacity="0"'

    # Title line:  handle
    p.append(
        f'<g{op}>{anim(0.0)}'
        f'<text x="{PAD}" y="{y}" fill="{TITLE_C}" font-weight="bold">{escape(HANDLE)}</text>'
        f'<text x="{PAD + len(HANDLE) * FONT * 0.62 + 8:.0f}" y="{y}" fill="{DIM}">'
        f'~ neofetch</text></g>'
    )
    y += LINE_H
    p.append(
        f'<g{op}>{anim(0.12)}'
        f'<text x="{PAD}" y="{y}" fill="{DIM}">{escape("-" * len(TITLE))}</text></g>'
    )
    y += LINE_H + 6

    for i, (label, value) in enumerate(ROWS):
        delay = 0.28 + i * 0.11
        lines = value if isinstance(value, list) else [value]
        vx = PAD + KEY_W + 14
        # label + colon + first value line
        row = [
            f'<g{op}>{anim(delay)}',
            f'<text x="{PAD}" y="{y}" fill="{KEY}" font-weight="bold">{escape(label)}</text>',
            f'<text x="{PAD + KEY_W}" y="{y}" fill="{DIM}">:</text>',
            f'<text x="{vx}" y="{y}" fill="{VALUE}">{escape(lines[0])}</text>',
        ]
        # any additional value lines, stacked under the value column
        for extra in lines[1:]:
            y += LINE_H
            row.append(f'<text x="{vx}" y="{y}" fill="{VALUE}">{escape(extra)}</text>')
        row.append('</g>')
        p.append("".join(row))
        y += LINE_H

    p.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"wrote {out}  ({'static' if STATIC else 'animated'}, {len(ROWS)} rows)")


if __name__ == "__main__":
    main()
