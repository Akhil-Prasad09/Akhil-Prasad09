"""Render my GitHub contribution calendar as an animated SVG (contrib-heatmap.svg).

Data comes from the public HTML fragment GitHub's own profile page uses, so no token is needed.
Standard library only, so the daily workflow has nothing to install.
"""
import datetime as dt
import re
import sys
import urllib.request
from pathlib import Path

USER = "Akhil-Prasad09"
OUT = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

CELL, GAP = 12, 3                 # 53 weeks * 15px = 795px + labels, inside the 860px README column
LEFT, TOP = 34, 52                # room for weekday labels and the title + month row
W, H = 860, TOP + 7 * (CELL + GAP) + 48


def fetch(user=USER):
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions", headers={"User-Agent": "profile-heatmap"})
    return urllib.request.urlopen(req, timeout=30).read().decode()


def parse(html):
    """[(date, level 0-4, count)] in calendar order (week by week, Sunday first)."""
    counts = {}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"(\d[\d,]*) contribution", text)
        counts[cid] = int(m.group(1).replace(",", "")) if m else 0
    days = []
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        date, level, cid = (re.search(rf'{a}="([^"]+)"', td) for a in ("data-date", "data-level", "id"))
        if date and level:
            days.append((dt.date.fromisoformat(date.group(1)), int(level.group(1)), counts.get(cid.group(1), 0)))
    if len(days) < 300:
        sys.exit(f"only parsed {len(days)} days; GitHub's markup probably changed")
    return sorted(days)


def stats(days, today=None):
    today = today or max(d for d, _, _ in days)
    by_day = {d: c for d, _, c in days if d <= today}
    longest = run = 0
    for d in sorted(by_day):
        run = run + 1 if by_day[d] else 0
        longest = max(longest, run)
    current, d = 0, today if by_day.get(today) else today - dt.timedelta(days=1)   # today may still be young
    while by_day.get(d):
        current, d = current + 1, d - dt.timedelta(days=1)
    best = max(by_day.items(), key=lambda kv: kv[1])
    return {"total": sum(by_day.values()), "current": current, "longest": longest, "best": best}


def render(days):
    s = stats(days)
    first = days[0][0]
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)       # Sunday of the first week
    cells, months, seen = [], [], set()
    for d, level, count in days:
        col, row = (d - start).days // 7, (d.weekday() + 1) % 7
        x, y = LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
        delay = (col + row) * 14                                         # diagonal reveal, top-left first
        noun = "contribution" if count == 1 else "contributions"
        cells.append(f'<rect class="c l{level}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                     f'style="animation-delay:{delay}ms"><title>{count} {noun} on {d:%b %-d, %Y}</title></rect>')
        if d.day <= 7 and row == 0 and (d.year, d.month) not in seen and col < 52:
            seen.add((d.year, d.month))
            months.append(f'<text class="m" x="{x}" y="{TOP - 8}">{d:%b}</text>')
    days_lbl = "".join(f'<text class="m" x="0" y="{TOP + r * (CELL + GAP) + 10}">{n}</text>' for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    ly = TOP + 7 * (CELL + GAP) + 18
    legend = "".join(f'<rect class="c l{i}" x="{W - 120 + i * 16}" y="{ly - 10}" width="{CELL - 2}" height="{CELL - 2}" rx="3"/>' for i in range(5))
    best_d, best_c = s["best"]
    footer = (f'Current streak {s["current"]} day{"" if s["current"] == 1 else "s"}  ·  '
              f'longest {s["longest"]}  ·  best day {best_c} on {best_d:%b %-d}')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{s["total"]} GitHub contributions in the last year">
<style>
  text {{ font: 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #57606a; }}
  .t {{ font-size: 14px; font-weight: 600; fill: #1f2328; }}
  .l0 {{ fill: #ebedf0; }} .l1 {{ fill: #9be9a8; }} .l2 {{ fill: #40c463; }} .l3 {{ fill: #30a14e; }} .l4 {{ fill: #216e39; }}
  .c {{ animation: in 420ms cubic-bezier(.2, .8, .2, 1) backwards; }}   /* visible unless the animation runs */
  @keyframes in {{ from {{ opacity: 0; transform: translateY(-5px); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-color-scheme: dark) {{
    text {{ fill: #8b949e; }} .t {{ fill: #e6edf3; }}
    .l0 {{ fill: #161b22; }} .l1 {{ fill: #0e4429; }} .l2 {{ fill: #006d32; }} .l3 {{ fill: #26a641; }} .l4 {{ fill: #39d353; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .c {{ animation: none; }} }}
</style>
<text class="t" x="0" y="16">{s["total"]:,} contributions in the last year</text>
{"".join(months)}{days_lbl}
{"".join(cells)}
<text x="0" y="{ly}">{footer}</text>
<text x="{W - 160}" y="{ly}">Less</text>{legend}<text x="{W - 36}" y="{ly}">More</text>
</svg>
'''


if __name__ == "__main__":
    OUT.write_text(render(parse(fetch())))
    print(f"wrote {OUT.name}")
