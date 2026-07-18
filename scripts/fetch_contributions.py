#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar — no token, no GraphQL.

GitHub serves the calendar as public HTML at
    https://github.com/users/<username>/contributions
(the same fragment the profile page uses). We scrape the day cells and write
data/contributions.json with the raw days plus derived stats.

    python scripts/fetch_contributions.py               # uses USERNAME below
    python scripts/fetch_contributions.py someuser
"""
import json
import re
import sys
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

USERNAME = "Izza-niazi"
URL = "https://github.com/users/{}/contributions"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (profile-art; +https://github.com/{})",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "text/html",
}


def fetch_html(user: str) -> str:
    r = requests.get(
        URL.format(user),
        headers={**HEADERS, "User-Agent": HEADERS["User-Agent"].format(user)},
        timeout=30,
    )
    r.raise_for_status()
    return r.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    # Map cell id -> contribution count via the <tool-tip> elements.
    counts: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        text = tip.get_text(strip=True)
        if not target:
            continue
        m = re.match(r"^([\d,]+)", text)
        counts[target] = int(m.group(1).replace(",", "")) if m else 0

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        level = int(td.get("data-level", 0))
        cid = td.get("id", "")
        # Prefer the tooltip count; fall back to legacy data-count; else 0.
        count = counts.get(cid)
        if count is None:
            count = int(td.get("data-count", 0) or 0)
        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # Longest / current streak (consecutive days with count > 0).
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)

    # Current streak = trailing run ending today (or yesterday if today is 0).
    current = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        elif current == 0:
            # allow today itself to be empty without breaking the streak
            continue
        else:
            break

    best = max(days, key=lambda x: x["count"], default={"date": "", "count": 0})

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": dict(sorted(monthly.items())),
    }


def main(user: str) -> None:
    days = parse_days(fetch_html(user))
    if not days:
        raise SystemExit("No day cells parsed — GitHub markup may have changed.")

    payload = {
        "username": user,
        "generated_at": days[-1]["date"],  # last calendar day (deterministic)
        "range": {"from": days[0]["date"], "to": days[-1]["date"]},
        "days": days,
        "stats": derive_stats(days),
    }
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(
        f"wrote data/contributions.json  "
        f"{len(days)} days, {payload['stats']['total']} contributions"
    )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else USERNAME)
