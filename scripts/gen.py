"""Generates contrib-heatmap.svg (live, no token) and info-card.svg. stdlib only."""
import re, sys, urllib.request
from datetime import date

USER = "websboy10"
PAL = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
W = 860

def fetch():
    html = urllib.request.urlopen(urllib.request.Request(
        f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "Mozilla/5.0"})).read().decode()
    counts = {i: 0 if n == "No" else int(n) for i, n in re.findall(
        r'<tool-tip[^>]*for="([^"]+)"[^>]*>(No|\d+) contributions?', html)}
    days = [(date.fromisoformat(d), int(l), counts.get(i, 0)) for d, i, l in
            re.findall(r'data-date="([^"]+)" id="([^"]+)" data-level="(\d)"', html)]
    return sorted(days)

def streaks(days):
    cur = best = run = 0
    for _, _, c in days:
        run = run + 1 if c else 0
        best = max(best, run)
    for _, _, c in reversed(days):
        if c: cur += 1
        elif cur or _ != days[-1][0]: break
    return cur, best

def heatmap(days):
    first = days[0][0]
    total = sum(c for *_, c in days)
    cur, best = streaks(days)
    cells = []
    for d, lvl, c in days:
        wk = (d - first).days // 7
        dow = (d.weekday() + 1) % 7  # Sunday-first rows
        x, y = 42 + wk * 15, 62 + dow * 15
        delay = (wk + dow) * 0.035
        cells.append(f'<rect class="c" x="{x}" y="{y}" width="12" height="12" rx="3" fill="{PAL[min(lvl, 5)]}" style="animation-delay:{delay:.2f}s"/>')
    months = "".join(f'<text x="{42 + ((d - first).days // 7) * 15}" y="54" class="m">{d.strftime("%b")}</text>'
                     for d, *_ in days if d.day <= 7 and d.weekday() == 6)
    dows = "".join(f'<text x="8" y="{72 + i * 15}" class="m">{n}</text>' for i, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    legend = "".join(f'<rect x="{W - 150 + i * 16}" y="188" width="12" height="12" rx="3" fill="{c}"/>' for i, c in enumerate(PAL))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="220" viewBox="0 0 {W} 220" font-family="{FONT}">
<style>.c{{opacity:0;animation:in .5s ease-out forwards}}@keyframes in{{from{{opacity:0;transform:translateY(-6px)}}to{{opacity:1;transform:none}}}}.m{{fill:#7d8590;font-size:10px}}.t{{fill:#e6edf3;font-size:13px}}</style>
<rect width="{W}" height="220" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="42" y="30" class="t"><tspan fill="#39d353">{USER}@github</tspan> ~ $ ./contributions.sh</text>
{months}{dows}{"".join(cells)}
<text x="42" y="199" class="m">{total:,} contributions in the last year · streak {cur}d · longest {best}d</text>
<text x="{W - 190}" y="199" class="m" text-anchor="end">Less</text>{legend}<text x="{W - 46}" y="199" class="m">More</text>
</svg>'''

CARD = [  # (key, value)
    ("", "sehit@denmark"),
    ("", "─" * 44),
    ("Role", "AI-agent engineer &amp; founder"),
    ("Now", "Modestly · modest-fashion marketplace"),
    ("Also", "Nordisk Software · Nordic Engine CRM"),
    ("Stack", "TypeScript · Next.js · Postgres/Supabase · C#"),
    ("Agents", "Claude Code · GSD · MCP · routines"),
    ("Edge", "Cloudflare Workers · D1 · Vercel"),
    ("Shipped", "sehit-studio · mix-madsen · future-gaming"),
    ("Ask me", "loop engineering, agent workflows, web that stares back"),
]

def card():
    rows = []
    for i, (k, v) in enumerate(CARD):
        y = 54 + i * 24
        key = f'<tspan fill="#39d353" font-weight="bold">{k}</tspan>' if k else ""
        rows.append(f'<text class="l" x="24" y="{y}" style="animation-delay:{i * 0.18:.2f}s">{key}{" " * (9 - len(k)) if k else ""}<tspan fill="#e6edf3">{v}</tspan></text>')
    h = 54 + len(CARD) * 24
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{FONT}">
<style>.l{{font-size:14px;white-space:pre;opacity:0;animation:in .4s ease-out forwards}}@keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}</style>
<rect width="{W}" height="{h}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="22" cy="20" r="6" fill="#ff5f56"/><circle cx="42" cy="20" r="6" fill="#ffbd2e"/><circle cx="62" cy="20" r="6" fill="#27c93f"/>
{"".join(rows)}
</svg>'''

if __name__ == "__main__":
    days = fetch()
    assert len(days) > 300, "contribution fetch returned too few days"
    open("contrib-heatmap.svg", "w").write(heatmap(days))
    open("info-card.svg", "w").write(card())
