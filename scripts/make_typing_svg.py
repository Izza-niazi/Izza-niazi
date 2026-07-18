#!/usr/bin/env python3
"""Self-hosted 'typing' headline SVG (SMIL) — no external typing-svg service.

Cycles through phrases: each types in left-to-right, holds, deletes, then the
next begins. A block cursor blinks throughout. Loops forever. All motion is
SMIL inside the file, so GitHub plays it from an <img>.

    python scripts/make_typing_svg.py     # writes typing-header.svg

Edit PHRASES below.
"""
from xml.sax.saxutils import escape

PHRASES = [
    "Software Engineer · Mobile & Web",
    "Building AI-powered apps",
    "React Native · React · TypeScript",
    "Full-stack builder · ships fast",
]

FONT = 30
CHAR_W = FONT * 0.6          # monospace advance
TYPE = 0.075                 # seconds per char typing
DELETE = 0.04                # seconds per char deleting
HOLD = 1.6                   # seconds to hold a full phrase
GAP = 0.35                   # pause between phrases
GREEN = "#39d353"
PROMPT_C = "#58a6ff"
BG = "#0d1117"
PROMPT = "$ "


def main(out: str = "typing-header.svg") -> None:
    longest = max(len(s) for s in PHRASES)
    prompt_w = len(PROMPT) * CHAR_W
    width = int(prompt_w + longest * CHAR_W + CHAR_W * 3)
    height = int(FONT * 2)
    base_y = int(FONT * 1.35)

    # Per-phrase timeline (seconds) within one full cycle T.
    windows = []
    t = 0.0
    for s in PHRASES:
        t_type = len(s) * TYPE
        t_del = len(s) * DELETE
        windows.append((t, t_type, t_del, len(s)))
        t += t_type + HOLD + t_del + GAP
    T = t

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'font-family="\'Cascadia Code\',\'Courier New\',monospace" font-size="{FONT}">',
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        f'<text x="10" y="{base_y}" fill="{PROMPT_C}" font-weight="bold" '
        f'xml:space="preserve">{escape(PROMPT)}</text>',
    ]

    text_x = 10 + prompt_w

    for (start, t_type, t_del, n), phrase in zip(windows, PHRASES):
        full_w = n * CHAR_W
        # Build keyTimes/values for a clip rect width across the whole cycle T.
        pts = [(0.0, 0.0)]
        seg = [
            (start, 0.0),
            (start + t_type, full_w),
            (start + t_type + HOLD, full_w),
            (start + t_type + HOLD + t_del, 0.0),
            (T, 0.0),
        ]
        for tm, val in seg:
            if tm > pts[-1][0] + 1e-6:      # keep strictly increasing
                pts.append((tm, val))
        kt = ";".join(f"{tm / T:.4f}" for tm, _ in pts)
        vals = ";".join(f"{val:.1f}" for _, val in pts)

        clip = f"tclip{int(start * 1000)}"
        p.append(
            f'<clipPath id="{clip}"><rect x="{text_x:.1f}" y="0" height="{height}" width="0">'
            f'<animate attributeName="width" dur="{T:.3f}s" repeatCount="indefinite" '
            f'calcMode="linear" keyTimes="{kt}" values="{vals}"/></rect></clipPath>'
        )
        p.append(
            f'<text x="{text_x:.1f}" y="{base_y}" fill="{GREEN}" clip-path="url(#{clip})" '
            f'xml:space="preserve">{escape(phrase)}</text>'
        )

    # A single blinking cursor sitting just after the prompt.
    p.append(
        f'<rect x="{text_x + 2:.1f}" y="{base_y - FONT + 6}" width="{CHAR_W * 0.6:.1f}" '
        f'height="{FONT}" fill="{GREEN}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )
    p.append("</svg>")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"wrote {out}  ({len(PHRASES)} phrases, cycle ~{T:.1f}s)")


if __name__ == "__main__":
    main()
