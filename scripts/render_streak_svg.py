#!/usr/bin/env python3
"""Render a self-hosted streak card from data/contributions.json.

The popular "GitHub Streak Stats" widget, but generated from data you already
fetch — no external service, no rate limits. Three panels: total contributions,
current streak, longest streak, each with its date range. Refreshes daily with
the heatmap.

    python scripts/render_streak_svg.py     # writes streak-stats.svg
"""
import json
from datetime import date

BG = "#0d1117"
BORDER = "#30363d"
GREEN = "#39d353"
BLUE = "#58a6ff"
FIRE = "#f78166"
VALUE = "#c8ced6"
DIM = "#8b949e"


def pretty(d: str) -> str:
    if not d:
        return "—"
    y, m, dd = d.split("-")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[int(m) - 1]} {int(dd)}, {y}"


def compute(days: list[dict]):
    total = sum(d["count"] for d in days)

    # Longest streak with its span.
    longest = (0, None, None)
    run, run_start = 0, None
    for d in days:
        if d["count"] > 0:
            if run == 0:
                run_start = d["date"]
            run += 1
            if run > longest[0]:
                longest = (run, run_start, d["date"])
        else:
            run = 0

    # Current streak = trailing run (today may legitimately still be 0).
    seq = list(reversed(days))
    start_idx = 1 if (seq and seq[0]["count"] == 0) else 0
    cur, cur_from, cur_to = 0, None, None
    for d in seq[start_idx:]:
        if d["count"] > 0:
            if cur == 0:
                cur_to = d["date"]
            cur += 1
            cur_from = d["date"]
        else:
            break

    return total, (cur, cur_from, cur_to), longest


def panel(x, w, big, big_color, label, sub, delay, ring=False):
    cx = x + w / 2
    parts = [f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" '
             f'begin="{delay:.2f}s" dur="0.5s" fill="freeze"/>']
    if ring:
        r = 34
        circ = 2 * 3.14159 * r
        parts.append(
            f'<circle cx="{cx:.0f}" cy="78" r="{r}" fill="none" stroke="{BORDER}" stroke-width="4"/>'
            f'<circle cx="{cx:.0f}" cy="78" r="{r}" fill="none" stroke="{big_color}" stroke-width="4" '
            f'stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" '
            f'transform="rotate(-90 {cx:.0f} 78)">'
            f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="{circ * 0.18:.1f}" '
            f'begin="{delay + 0.2:.2f}s" dur="0.9s" fill="freeze"/></circle>'
        )
    parts.append(
        f'<text x="{cx:.0f}" y="90" text-anchor="middle" fill="{big_color}" '
        f'font-size="46" font-weight="bold">{big}</text>'
    )
    parts.append(
        f'<text x="{cx:.0f}" y="126" text-anchor="middle" fill="{VALUE}" '
        f'font-size="15" font-weight="bold">{label}</text>'
    )
    parts.append(
        f'<text x="{cx:.0f}" y="150" text-anchor="middle" fill="{DIM}" font-size="11">{sub}</text>'
    )
    parts.append("</g>")
    return "".join(parts)


def main(src: str = "data/contributions.json", out: str = "streak-stats.svg") -> None:
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    days = data["days"]
    total, (cur, cf, ct), (lng, lf, lt) = compute(days)

    W, H = 620, 200
    col = W / 3
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" '
        f'font-family="\'Cascadia Code\',\'Segoe UI\',sans-serif">',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        f'<circle cx="20" cy="20" r="5" fill="#ff5f56"/><circle cx="38" cy="20" r="5" fill="#ffbd2e"/>'
        f'<circle cx="56" cy="20" r="5" fill="#27c93f"/>',
        f'<text x="{W/2:.0f}" y="24" text-anchor="middle" fill="{DIM}" font-size="12" '
        f'font-family="monospace">izza@github ~ $ ./streak.sh</text>',
        # dividers
        f'<line x1="{col:.0f}" y1="48" x2="{col:.0f}" y2="{H-20}" stroke="{BORDER}"/>',
        f'<line x1="{2*col:.0f}" y1="48" x2="{2*col:.0f}" y2="{H-20}" stroke="{BORDER}"/>',
        panel(0, col, f"{total:,}", GREEN, "Total contributions",
              f"{pretty(data['range']['from'])} – {pretty(data['range']['to'])}", 0.1),
        panel(col, col, str(cur), FIRE, "Current streak",
              (f"{pretty(cf)} – {pretty(ct)}" if cur else "start one today!"), 0.28, ring=True),
        panel(2 * col, col, str(lng), BLUE, "Longest streak",
              (f"{pretty(lf)} – {pretty(lt)}" if lng else "—"), 0.46),
        "</svg>",
    ]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"wrote {out}  (total {total}, current {cur}, longest {lng})")


if __name__ == "__main__":
    main()
