#!/usr/bin/env python3
"""
fetch_contributions.py
Scrapes the public (no-auth) contribution calendar fragment GitHub serves at
https://github.com/users/<username>/contributions and writes data/contributions.json.

Usage: GH_PROFILE_USER=yourname python scripts/fetch_contributions.py
"""
import os
import sys
import json
import re
from datetime import date
import requests
from bs4 import BeautifulSoup

def main():
    user = os.environ.get("GH_PROFILE_USER")
    if not user:
        print("set GH_PROFILE_USER env var")
        sys.exit(1)

    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    days = []
    cells = soup.select("td.ContributionCalendar-day, td[data-date]")
    if not cells:
        # fallback: newer markup uses <table> less often; try rect/tool-tip based layout
        cells = soup.select("[data-date]")

    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        count = 0
        tooltip_id = cell.get("id")
        if level is None:
            # try to read the tooltip text e.g. "5 contributions on ..."
            level = 0
        else:
            level = int(level)
        days.append({"date": d, "level": level})

    # try to enrich with actual counts from tooltip <tool-tip> elements
    tooltips = {t.get("for"): t.get_text(strip=True) for t in soup.select("tool-tip")}
    for day in days:
        tid = None
        cell = soup.find(attrs={"data-date": day["date"]})
        if cell is not None:
            tid = cell.get("id")
        text = tooltips.get(tid, "")
        m = re.search(r"(\d+)\s+contribution", text)
        day["count"] = int(m.group(1)) if m else (0 if "No contributions" in text else None)

    days.sort(key=lambda d: d["date"])

    total = sum(d["count"] or 0 for d in days)
    # streaks
    longest = current = 0
    today = date.today().isoformat()
    for d in days:
        if (d["count"] or 0) > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    # current streak counted from the end backwards
    running = 0
    for d in reversed(days):
        if d["date"] > today:
            continue
        if (d["count"] or 0) > 0:
            running += 1
        else:
            break

    out = {
        "user": user,
        "generated": date.today().isoformat(),
        "total": total,
        "longest_streak": longest,
        "current_streak": running,
        "days": days,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"saved data/contributions.json  ({len(days)} days, total={total}, "
          f"current_streak={running}, longest_streak={longest})")

if __name__ == "__main__":
    main()
