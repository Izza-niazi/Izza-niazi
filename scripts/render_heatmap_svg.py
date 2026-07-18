#!/usr/bin/env python3
"""Render data/contributions.json as an animated contribution heatmap SVG.

The classic 53-week x 7-day calendar of rounded boxes, revealed once with a
diagonal line-after-line slide-down (CSS keyframes that play on load, then
freeze — no looping glow). Adds month labels, a Less->More legend, and a
stats footer. GitHub runs CSS keyframe animations inside an <img>-embedded SVG.

    python scripts/render_heatmap_svg.py        # writes contrib-heatmap.svg
"""
import json
from datetime import date, timedelta

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#           none  ----------------------------------------->  neon top end
BG = "#0d1117"
TEXT = "#8b949e"
TEXT_BRIGHT = "#c8ced6"

BOX = 11            # box size
GAP = 3            # gap between boxes
CELL = BOX + GAP   # 14
PAD_X = 30         # left pad (weekday labels)
PAD_TOP = 34       # top pad (month labels)
PAD_BOT = 46       # bottom pad (legend + footer)

WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level_for(count: int, level: int) -> int:
    # Promote a truly huge day to the neon 5th level for a pop of colour.
    if level >= 4 and count >= 20:
        return 5
    return min(level, 5)


def main(src: str = "data/contributions.json", out: str = "contrib-heatmap.svg") -> None:
    with open(src, encoding="utf-8") as f:
        data = json.load(f)

    days = data["days"]
    by_date = {d["date"]: d for d in days}
    first = date.fromisoformat(days[0]["date"])
    last = date.fromisoformat(days[-1]["date"])

    # Align the grid to weeks starting on Sunday (weekday(): Mon=0..Sun=6).
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    weeks = (last - start).days // 7 + 1

    grid_w = weeks * CELL
    width = PAD_X + grid_w + 12
    height = PAD_TOP + 7 * CELL + PAD_BOT

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'font-family="\'Cascadia Code\',\'Segoe UI\',sans-serif" font-size="10">',
        "<style>",
        "@keyframes reveal{from{opacity:0;transform:translateY(-6px)}"
        "to{opacity:1;transform:translateY(0)}}",
        ".box{opacity:0;transform-box:fill-box;transform-origin:center;"
        "animation:reveal .5s ease-out forwards}",
        "</style>",
        f'<rect width="{width}" height="{height}" rx="8" fill="{BG}"/>',
    ]

    # Month labels along the top.
    seen_month = None
    d = start
    for w in range(weeks):
        wk = start + timedelta(days=w * 7)
        if wk.month != seen_month and wk.day <= 7:
            x = PAD_X + w * CELL
            p.append(f'<text x="{x}" y="{PAD_TOP - 12}" fill="{TEXT}">{MONTHS[wk.month - 1]}</text>')
            seen_month = wk.month

    # Weekday labels down the left.
    for wd, label in WEEKDAY_LABELS.items():
        y = PAD_TOP + wd * CELL + BOX - 1
        p.append(f'<text x="0" y="{y}" fill="{TEXT}">{label}</text>')

    # The boxes.
    for w in range(weeks):
        for wd in range(7):
            cur = start + timedelta(days=w * 7 + wd)
            if cur < first or cur > last:
                continue
            info = by_date.get(cur.isoformat())
            if info is None:
                continue
            lvl = level_for(info["count"], info["level"])
            x = PAD_X + w * CELL
            y = PAD_TOP + wd * CELL
            delay = (w + wd) * 0.018   # diagonal cascade
            p.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2.5" '
                f'fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
                f'<title>{info["count"]} on {cur.isoformat()}</title></rect>'
            )

    # Legend: Less [] [] [] [] [] More
    lg_y = height - PAD_BOT + 40
    lg_x = width - 12 - 6 * CELL - 70
    p.append(f'<text x="{lg_x}" y="{lg_y + BOX - 2}" fill="{TEXT}">Less</text>')
    for i, c in enumerate(PALETTE):
        x = lg_x + 34 + i * CELL
        p.append(f'<rect x="{x}" y="{lg_y}" width="{BOX}" height="{BOX}" rx="2.5" fill="{c}"/>')
    p.append(f'<text x="{lg_x + 34 + 6 * CELL + 6}" y="{lg_y + BOX - 2}" fill="{TEXT}">More</text>')

    # Footer stats.
    s = data["stats"]
    foot_y = height - PAD_BOT + 40
    p.append(
        f'<text x="{PAD_X}" y="{foot_y + BOX - 2}" fill="{TEXT_BRIGHT}">'
        f'{s["total"]:,} contributions in the last year</text>'
    )
    p.append(
        f'<text x="{PAD_X}" y="{foot_y + BOX + 16}" fill="{TEXT}">'
        f'▲ {s["longest_streak"]}d longest streak  ·  '
        f'{s["current_streak"]}d current  ·  best {s["best_day"]["count"]} on '
        f'{s["best_day"]["date"]}</text>'
    )

    p.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p))
    print(f"wrote {out}  ({weeks} weeks, {s['total']} contributions)")


if __name__ == "__main__":
    main()
