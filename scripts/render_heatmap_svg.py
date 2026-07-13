#!/usr/bin/env python3
"""
render_heatmap_svg.py
Reads data/contributions.json and writes contrib-heatmap.svg: a GitHub-style
grid of boxes that reveal cell by cell, with a Less->More legend and real
streak stats.
"""
import json
from datetime import date, timedelta

SRC = "data/contributions.json"
OUT = "contrib-heatmap.svg"

CELL = 11
GAP = 3
MARGIN_LEFT = 30
MARGIN_TOP = 40
MARGIN_BOTTOM = 34

LEVEL_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
TEXT_COLOR = "#8b949e"
STRONG_TEXT = "#c9d1d9"

REVEAL_DUR = 0.35
STAGGER = 0.006  # per column (week)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main():
    with open(SRC) as f:
        data = json.load(f)

    days = {d["date"]: d for d in data["days"]}
    if not days:
        raise SystemExit("no contribution data -- run fetch_contributions.py first")

    all_dates = sorted(days)
    end = date.fromisoformat(all_dates[-1])
    start = end - timedelta(days=6 - end.weekday() if False else 0)
    # align grid start to the most recent Sunday on/after 52 weeks back
    grid_start = date.fromisoformat(all_dates[0])
    grid_start -= timedelta(days=(grid_start.weekday() + 1) % 7)  # back to Sunday

    weeks = []
    cur = grid_start
    week = []
    while cur <= end:
        week.append(cur)
        if cur.weekday() == 5:  # Saturday -> close week
            weeks.append(week)
            week = []
        cur += timedelta(days=1)
    if week:
        weeks.append(week)

    n_weeks = len(weeks)
    width = MARGIN_LEFT + n_weeks * (CELL + GAP) + 140
    height = MARGIN_TOP + 7 * (CELL + GAP) + MARGIN_BOTTOM

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Menlo, Consolas, monospace" font-size="11">',
        '<rect width="100%" height="100%" fill="transparent"/>',
    ]

    total = data.get("total", 0)
    cur_streak = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    stats = f"{total} contributions in the last year -- current streak {cur_streak}d, longest {longest}d"
    svg.append(f'<text x="{MARGIN_LEFT}" y="20" fill="{STRONG_TEXT}" font-size="13">{esc(stats)}</text>')

    for wi, wk in enumerate(weeks):
        x = MARGIN_LEFT + wi * (CELL + GAP)
        begin = round(wi * STAGGER, 3)
        for d in wk:
            y = MARGIN_TOP + d.weekday() * (CELL + GAP)
            # weekday(): Mon=0..Sun=6 -> we want Sun on top like GitHub; remap
            dow = (d.weekday() + 1) % 7  # Sun=0..Sat=6
            y = MARGIN_TOP + dow * (CELL + GAP)
            key = d.isoformat()
            level = days.get(key, {}).get("level", 0) or 0
            color = LEVEL_COLORS[min(level, 4)]
            svg.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<title>{key}: {days.get(key, {}).get("count", 0) or 0} contributions</title>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" '
                f'dur="{REVEAL_DUR}s" fill="freeze"/></rect>'
            )

    legend_x = MARGIN_LEFT + n_weeks * (CELL + GAP) + 10
    legend_y = MARGIN_TOP
    svg.append(f'<text x="{legend_x}" y="{legend_y-4}" fill="{TEXT_COLOR}">Less</text>')
    for i, c in enumerate(LEVEL_COLORS):
        svg.append(f'<rect x="{legend_x + 32 + i*(CELL+GAP)}" y="{legend_y-14}" '
                    f'width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    svg.append(f'<text x="{legend_x + 32 + len(LEVEL_COLORS)*(CELL+GAP) + 6}" '
               f'y="{legend_y-4}" fill="{TEXT_COLOR}">More</text>')

    svg.append("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(svg))
    print(f"saved {OUT}  ({n_weeks} weeks)")

if __name__ == "__main__":
    main()
