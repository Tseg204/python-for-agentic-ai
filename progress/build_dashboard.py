"""Builds progress/dashboard.html (or final-report.html with --final) from progress.json.

Run:  python3 progress/build_dashboard.py
      python3 progress/build_dashboard.py --final
"""

import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
DATA = json.loads((HERE / "progress.json").read_text())
FINAL = "--final" in sys.argv
WEAK_BELOW = 60  # a skill under this % correct is marked "needs work"


def pct(right, total):
    return round(100 * right / total) if total else None


# ---- Work out the numbers ----------------------------------------------------
sessions = DATA["sessions"]
done = len(sessions)
total_sessions = DATA["total_sessions"]

per_session = []  # (number, title, quiz %, exercise %)
skills = {}       # skill -> {"right": n, "total": n, "ratings": [..]}
for s in sessions:
    quiz = [i for i in s["items"] if i["source"] == "quiz"]
    ex = [i for i in s["items"] if i["source"] == "exercise"]
    per_session.append((
        s["number"], s["title"],
        pct(sum(i["correct"] for i in quiz), len(quiz)),
        pct(sum(i["correct"] for i in ex), len(ex)),
    ))
    for i in s["items"]:
        k = skills.setdefault(i["skill"], {"right": 0, "total": 0, "ratings": []})
        k["total"] += 1
        k["right"] += int(i["correct"])
    for skill, r in s.get("ratings", {}).items():
        skills.setdefault(skill, {"right": 0, "total": 0, "ratings": []})["ratings"].append(r)

skill_rows = sorted(
    ((name, pct(v["right"], v["total"]), v["total"], v["ratings"]) for name, v in skills.items()),
    key=lambda r: (r[1] if r[1] is not None else 101),
)

quiz_scores = [q for _, _, q, _ in per_session if q is not None]
ex_scores = [e for _, _, _, e in per_session if e is not None]
avg_quiz = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else None
avg_ex = round(sum(ex_scores) / len(ex_scores)) if ex_scores else None


def show(n):
    return "–" if n is None else f"{n}%"


# ---- Build the HTML pieces ---------------------------------------------------
def session_chart():
    if not per_session:
        return '<p class="empty">No sessions yet. Your quiz scores will show up here after Session 1.</p>'
    w, h, pad_l, pad_b, pad_t = 640, 220, 36, 28, 12
    slot = (w - pad_l) / max(total_sessions, 1)
    bar_w = min(18, slot - 4)
    plot_h = h - pad_b - pad_t
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Quiz score per session">']
    for g in (0, 50, 100):
        y = pad_t + plot_h * (1 - g / 100)
        out.append(f'<line class="grid" x1="{pad_l}" x2="{w}" y1="{y}" y2="{y}"/>'
                   f'<text class="axis" x="{pad_l - 6}" y="{y + 4}" text-anchor="end">{g}%</text>')
    for num, title, quiz, ex in per_session:
        if quiz is None:
            continue
        x = pad_l + (num - 1) * slot + (slot - bar_w) / 2
        bh = max(plot_h * quiz / 100, 2)
        y = pad_t + plot_h - bh
        tip = html.escape(f"Session {num}: {title} · quiz {quiz}% · exercise {show(ex)}")
        out.append(
            f'<path class="bar" data-tip="{tip}" d="M{x},{y + bh} V{y + 4} q0,-4 4,-4 h{bar_w - 8} '
            f'q4,0 4,4 V{y + bh} Z"/>'
        )
    for n in range(1, total_sessions + 1):
        if n == 1 or n % 5 == 0:
            x = pad_l + (n - 1) * slot + slot / 2
            out.append(f'<text class="axis" x="{x}" y="{h - 8}" text-anchor="middle">{n}</text>')
    out.append("</svg>")
    return "".join(out)


def skill_table():
    if not skill_rows:
        return '<p class="empty">Skills appear here once you\'ve done a session.</p>'
    rows = []
    for name, p, total, ratings in skill_rows:
        avg_r = f"{sum(ratings) / len(ratings):.1f} / 3" if ratings else "–"
        flag = '<span class="flag">needs work</span>' if p is not None and p < WEAK_BELOW else ""
        width = p or 0
        rows.append(
            f'<tr><td class="skill"><code>{html.escape(name)}</code> {flag}</td>'
            f'<td class="meter"><div class="track"><div class="fill" style="width:{width}%" '
            f'data-tip="{html.escape(name)}: {show(p)} correct over {total} questions"></div></div></td>'
            f'<td class="num">{show(p)}</td><td class="num">{total}</td><td class="num">{avg_r}</td></tr>'
        )
    return ('<table><thead><tr><th>Skill</th><th></th><th>Correct</th><th>Questions</th>'
            '<th>Teacher rating</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>")


def notes_list():
    if not sessions:
        return ""
    items = []
    for s in reversed(sessions[-5:]):
        items.append(
            f'<li><strong>Session {s["number"]}: {html.escape(s["title"])}</strong> '
            f'<span class="muted">{html.escape(s["date"])}</span><br>'
            f'Went well: {html.escape(s.get("went_well", ""))}<br>'
            f'Hard: {html.escape(s.get("hard", ""))}</li>'
        )
    return '<section><h2>Recent session notes</h2><ul class="notes">' + "".join(items) + "</ul></section>"


def work_on():
    if not FINAL:
        return ""
    notes = DATA.get("final_notes", [])
    if notes:
        cards = []
        for n in notes:
            practice = "".join(f"<li>{html.escape(p)}</li>" for p in n.get("practice", []))
            cards.append(f'<div class="card"><h3><code>{html.escape(n["skill"])}</code></h3>'
                         f'<p>{html.escape(n["reason"])}</p><ul>{practice}</ul></div>')
        body = "".join(cards)
    else:
        weakest = [r[0] for r in skill_rows[:3]]
        body = "<p>Weakest skills by score: " + ", ".join(f"<code>{w}</code>" for w in weakest) + "</p>"
    return f'<section><h2>What to work on next</h2><div class="cards">{body}</div></section>'


next_up = (f"Next up: Session {DATA['current_session']}"
           if DATA["current_session"] <= total_sessions else "Course complete")
title = "Final Report" if FINAL else "My Python Progress"

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{
  color-scheme: light;
  --surface: #fcfcfb; --card: #ffffff; --line: #e6e5e0;
  --text: #0b0b0b; --text-2: #52514e; --muted: #7a7974;
  --series-1: #2a78d6; --track: #eeede8; --flag: #b3261e;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    --surface: #1a1a19; --card: #232322; --line: #3a3a38;
    --text: #f0efec; --text-2: #c3c2b7; --muted: #8f8e88;
    --series-1: #3987e5; --track: #2f2f2d; --flag: #ff8a80;
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --surface: #1a1a19; --card: #232322; --line: #3a3a38;
  --text: #f0efec; --text-2: #c3c2b7; --muted: #8f8e88;
  --series-1: #3987e5; --track: #2f2f2d; --flag: #ff8a80;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--surface); color: var(--text);
  font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
main {{ max-width: 760px; margin: 0 auto; padding: 32px 16px 64px; }}
h1 {{ margin: 0 0 4px; font-size: 28px; }}
h2 {{ font-size: 18px; margin: 36px 0 12px; }}
.muted, .sub {{ color: var(--text-2); }}
.tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 24px; }}
.tile {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px; }}
.tile .big {{ font-size: 32px; font-weight: 600; }}
.tile .label {{ color: var(--text-2); font-size: 14px; }}
svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--line); stroke-width: 1; }}
.axis {{ fill: var(--muted); font-size: 11px; }}
.bar {{ fill: var(--series-1); cursor: default; }}
.bar:hover, .fill:hover {{ opacity: .8; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ text-align: left; color: var(--text-2); font-weight: 500; padding: 6px 8px; border-bottom: 1px solid var(--line); }}
td {{ padding: 8px; border-bottom: 1px solid var(--line); }}
td.num {{ text-align: right; white-space: nowrap; }}
td.meter {{ width: 35%; }}
.track {{ background: var(--track); border-radius: 4px; height: 10px; }}
.fill {{ background: var(--series-1); border-radius: 4px; height: 10px; }}
.flag {{ color: var(--flag); font-size: 12px; margin-left: 6px; white-space: nowrap; }}
.flag::before {{ content: "⚠ "; }}
.empty {{ color: var(--muted); background: var(--card); border: 1px dashed var(--line); border-radius: 12px; padding: 20px; }}
.notes {{ list-style: none; padding: 0; }}
.notes li {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; }}
.cards {{ display: grid; gap: 12px; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px; }}
.card h3 {{ margin: 0 0 6px; }}
#tip {{ position: fixed; pointer-events: none; background: var(--text); color: var(--surface);
  font-size: 13px; padding: 6px 10px; border-radius: 6px; display: none; max-width: 260px; }}
.scroll {{ overflow-x: auto; }}
</style></head>
<body><main>
<h1>{title}</h1>
<div class="sub">{html.escape(DATA['course'])} · {html.escape(DATA['pace'])}</div>
<div class="tiles">
  <div class="tile"><div class="big">{done}/{total_sessions}</div><div class="label">sessions done</div></div>
  <div class="tile"><div class="big">{show(avg_quiz)}</div><div class="label">average quiz score</div></div>
  <div class="tile"><div class="big">{show(avg_ex)}</div><div class="label">average exercise score</div></div>
  <div class="tile"><div class="big" style="font-size:20px;padding-top:10px">{next_up}</div><div class="label">&nbsp;</div></div>
</div>
{work_on()}
<section><h2>Quiz score per session</h2>{session_chart()}</section>
<section><h2>Skills, weakest first</h2><div class="scroll">{skill_table()}</div></section>
{notes_list()}
</main>
<div id="tip"></div>
<script>
const tip = document.getElementById('tip');
document.querySelectorAll('[data-tip]').forEach(el => {{
  el.addEventListener('mousemove', e => {{
    tip.textContent = el.dataset.tip; tip.style.display = 'block';
    tip.style.left = Math.min(e.clientX + 12, innerWidth - 270) + 'px';
    tip.style.top = (e.clientY + 12) + 'px';
  }});
  el.addEventListener('mouseleave', () => tip.style.display = 'none');
}});
</script>
</body></html>
"""

out = HERE / ("final-report.html" if FINAL else "dashboard.html")
out.write_text(page)
print(f"Wrote {out}")
