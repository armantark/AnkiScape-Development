"""Build the design progress page from classified design rows.

Usage: python3 build.py --out PAGE.html ROWS.jsonl [ROWS.jsonl ...] [--repo PATH]
"""
import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

TEMPLATE = Path(__file__).with_name("template.html")
STATUSES = [
    ("implemented", "Built"),
    ("partial", "Partly built"),
    ("blocked", "Blocked"),
    ("deferred", "Deferred depth"),
    ("not_started", "Not started"),
    ("unverified", "Unverified"),
    ("rejected", "Ruled out"),
]
LABEL = dict(STATUSES)
ORDER = {k: i for i, (k, _) in enumerate(STATUSES)}
OPEN = ("partial", "blocked", "deferred", "not_started")
FAMILIES = [
    "Skills", "Activities & minigames", "Combat & bosses", "Economy & shops",
    "Quests & diaries", "Interface & help", "Core systems", "Tooling & process",
]
BLOCKERS = {
    "source": "Missing period data",
    "owner": "Waiting on your decision",
    "dependency": "Waiting on another system",
    "integration": "Fails a quality gate",
}
DEF = {
    "implemented": "Live in the game on main.",
    "partial": "Some of it is live; the table names what is left.",
    "blocked": "Cannot move until period data, your decision or another system arrives.",
    "deferred": "The base is live; more content is queued behind higher priorities.",
    "not_started": "Settled and free to build, with no work found yet.",
    "unverified": "The records do not show either way.",
    "rejected": "The grill ruled it out, so it needs no work.",
}
# Week chart geometry: plot width and height, left, bottom and top margins.
PW, PH, LM, BM, TM = 720, 220, 30, 34, 12


def esc(s):
    return html.escape(str(s or ""), quote=True)


def fmt_day(d):
    x = dt.date.fromisoformat(d)
    return f"{x.day} {x.strftime('%b')}"


def load_rows(paths):
    rows = []
    for path in paths:
        with open(path) as f:
            for n, line in enumerate(f, 1):
                if line.strip():
                    r = json.loads(line)
                    r["_file"] = f"{path}:{n}"
                    rows.append(r)
    check_rows(rows)
    rows.sort(key=lambda r: (ORDER[r["status"]], FAMILIES.index(r["family"]), r["date"] or "", r["name"]))
    return rows


def check_rows(rows):
    problems = {
        "bad status or family": [
            r["_file"] for r in rows if r["status"] not in LABEL or r["family"] not in FAMILIES
        ],
        "no evidence, so the status must be unverified": [
            r["_file"] for r in rows if r["status"] != "unverified" and not str(r.get("evidence") or "").strip()
        ],
        "duplicate ids": [i for i, c in Counter(r["id"] for r in rows).items() if c > 1],
    }
    found = {k: v for k, v in problems.items() if v}
    if found:
        sys.exit(json.dumps(found, indent=1))


def status_bars(by_status, total):
    maxc = max(by_status.values())
    out = []
    for k, lab in STATUSES:
        c = by_status[k]
        if not c:
            continue
        share = round(100 * c / total)
        tip = f"{c} designs|{lab}|{share}% of all {total}"
        out.append(
            f'<div class="hrow"><div class="hlabel"><span class="key s-{k}"></span>{lab}</div>'
            f'<div class="htrack"><div class="hbar s-{k}" style="width:{100 * c / maxc:.2f}%" tabindex="0" data-tip="{esc(tip)}"></div>'
            f'<span class="hval">{c}<span class="muted"> · {share}%</span></span></div></div>'
        )
    return "\n".join(out)


def family_bars(fam, fam_order):
    fmax = max(sum(fam[f].values()) for f in fam_order)
    out = []
    for f in fam_order:
        n = sum(fam[f].values())
        segs = "".join(
            f'<div class="seg s-{k}" style="flex:{fam[f][k]} 0 0" tabindex="0" data-tip="{esc(f"{fam[f][k]} of {n}|{lab}|{f}")}"></div>'
            for k, lab in STATUSES if fam[f][k]
        )
        out.append(
            f'<div class="frow"><div class="flabel">{esc(f)}</div>'
            f'<div class="ftrack"><div class="fstack" style="width:{100 * n / fmax:.2f}%">{segs}</div>'
            f'<span class="hval">{fam[f]["implemented"]}/{n} built</span></div>'
            f'<div class="fopen">{sum(fam[f][k] for k in OPEN)} open</div></div>'
        )
    return "\n".join(out)


def top_open(fam, fam_order):
    """The three families with the most open work, keeping ties with third place."""
    open_count = {f: sum(fam[f][k] for k in OPEN) for f in fam_order}
    ranked = sorted(fam_order, key=lambda f: (-open_count[f], f))
    cutoff = open_count[ranked[min(2, len(ranked) - 1)]]
    out = []
    for f in (f for f in ranked if open_count[f] >= cutoff):
        parts = ", ".join(f"{fam[f][k]} {LABEL[k].lower()}" for k in OPEN if fam[f][k])
        out.append(
            f'<li><span class="tnum">{open_count[f]}</span>'
            f'<span><strong>{esc(f)}</strong><br><span class="muted">{esc(parts)}</span></span></li>'
        )
    return "\n".join(out)


def blocker_bars(rows):
    blocked = [r for r in rows if r["status"] == "blocked"]
    blk = Counter(r.get("blocker") for r in blocked)
    bmax = max(blk.values()) if blk else 1
    out = []
    for k, lab in BLOCKERS.items():
        c = blk.get(k, 0)
        if not c:
            continue
        names = "; ".join(r["name"] for r in blocked if r.get("blocker") == k)
        out.append(
            f'<div class="hrow"><div class="hlabel">{lab}</div><div class="htrack">'
            f'<div class="hbar s-blocked" style="width:{100 * c / bmax:.2f}%" tabindex="0" data-tip="{esc(f"{c} blocked|{lab}|{names}")}"></div>'
            f'<span class="hval">{c}</span></div></div>'
        )
    unknown = sum(v for k, v in blk.items() if k not in BLOCKERS)
    note = f"{unknown} blocked designs name no blocker kind." if unknown else ""
    return "\n".join(out), note


def landing_weeks(landed):
    """Landed design names by Monday of their landing week, and every week in the span."""
    weeks = defaultdict(list)
    for r in landed:
        d = dt.date.fromisoformat(r["landed"])
        weeks[d - dt.timedelta(days=d.weekday())].append(r["name"])
    n = (max(weeks) - min(weeks)).days // 7 + 1
    return weeks, [min(weeks) + dt.timedelta(days=7 * i) for i in range(n)]


def column_path(x, y, w):
    """A column from the baseline up to y, with its top corners rounded."""
    base = TM + PH
    r = min(4, base - y)
    return (f"M{x:.1f},{base:.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} "
            f"H{x + w - r:.1f} Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} V{base:.1f} Z")


def week_svg(weeks, span):
    wmax = max(len(v) for v in weeks.values())
    tick = 2 if wmax <= 10 else 5
    top = -(-wmax // tick) * tick
    bw = (PW - LM) / len(span)
    barw = min(24, bw - 4)
    svg = [f'<svg viewBox="0 0 {PW} {PH + BM + TM}" class="cols" role="img" aria-label="Designs landing on main per week">']
    for t in range(0, top + 1, tick):
        y = TM + PH - PH * t / top
        svg.append(f'<line x1="{LM}" x2="{PW}" y1="{y:.1f}" y2="{y:.1f}" class="{"base" if t == 0 else "grid"}"/>')
        svg.append(f'<text x="{LM - 6}" y="{y + 4:.1f}" class="tick" text-anchor="end">{t}</text>')
    cum = 0
    for i, wk in enumerate(span):
        names = weeks.get(wk, [])
        cum += len(names)
        left = LM + i * bw
        if names:
            tip = f"{len(names)} landed|Week of {fmt_day(wk.isoformat())} · {cum} total so far|" + "; ".join(names)
            svg.append(f'<rect x="{left:.1f}" y="{TM}" width="{bw:.1f}" height="{PH}" class="hit" tabindex="0" data-tip="{esc(tip)}"/>')
            svg.append(f'<path d="{column_path(left + (bw - barw) / 2, TM + PH - PH * len(names) / top, barw)}" class="col"/>')
        if i % 2 == 0 or len(span) <= 10:
            svg.append(f'<text x="{left + bw / 2:.1f}" y="{TM + PH + 18}" class="tick" text-anchor="middle">{fmt_day(wk.isoformat())}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def table_row(r):
    k = r["status"]
    extra = f' <span class="muted">({BLOCKERS[r["blocker"]]})</span>' if k == "blocked" and r.get("blocker") in BLOCKERS else ""
    landed = f'<div class="sub landed">Landed {esc(r["landed"])}</div>' if r.get("landed") else ""
    search = " ".join(str(r.get(x) or "") for x in ("name", "family", "summary", "remaining", "evidence", "source")) + " " + LABEL[k]
    return (
        f'<tr data-status="{k}" data-family="{esc(r["family"])}" data-search="{esc(search.lower())}">'
        f'<td><strong>{esc(r["name"])}</strong><div class="sub">{esc(r.get("summary"))}</div></td>'
        f'<td>{esc(r["family"])}</td>'
        f'<td class="num">{esc(r.get("date"))}</td>'
        f'<td><span class="pill"><span class="key s-{k}"></span>{LABEL[k]}</span>{extra}{landed}'
        f'</td><td>{esc(r.get("remaining")) or "<span class=muted>Nothing</span>"}</td>'
        f'<td class="ev">{esc(r.get("evidence"))}<div class="src">{esc(r.get("source"))}</div></td></tr>'
    )


def date_range(rows):
    """First and last settled day; the year is shown once unless the range crosses years."""
    dates = sorted(r["date"] for r in rows if r.get("date"))
    first, last = dates[0], dates[-1]
    head = fmt_day(first) + ("" if first[:4] == last[:4] else f" {first[:4]}")
    return head, f"{fmt_day(last)} {last[:4]}"


def undated_note(rows, landed):
    n = sum(1 for r in rows if r["status"] == "implemented") - sum(1 for r in landed if r["status"] == "implemented")
    if not n:
        return ""
    return f"{n} built {'design has' if n == 1 else 'designs have'} no landing date in the records and {'is' if n == 1 else 'are'} not plotted. "


def chart_values(rows, by_status):
    fam = defaultdict(Counter)
    for r in rows:
        fam[r["family"]][r["status"]] += 1
    fam_order = sorted((f for f in FAMILIES if fam[f]), key=lambda f: -sum(fam[f].values()))
    landed = [r for r in rows if r.get("landed")]
    weeks, span = landing_weeks(landed)
    peak = max(span, key=lambda k: len(weeks.get(k, [])))
    blockers, unknown = blocker_bars(rows)
    shown = [(k, lab) for k, lab in STATUSES if by_status[k]]
    return {
        "STATUS_BARS": status_bars(by_status, len(rows)),
        "LEGEND": "".join(f'<span class="lg"><span class="key s-{k}"></span>{lab}</span>' for k, lab in shown),
        "FAMILY_BARS": family_bars(fam, fam_order),
        "TOP_OPEN": top_open(fam, fam_order),
        "BLOCKER_BARS": blockers,
        "UNKNOWN_BLK": unknown,
        "WEEK_SVG": week_svg(weeks, span),
        "LANDED": str(len(landed)),
        "NODATE": undated_note(rows, landed),
        "PEAK": fmt_day(peak.isoformat()),
        "PEAKN": str(len(weeks[peak])),
        "FAM_OPTS": "".join(f'<option value="{esc(f)}">{esc(f)}</option>' for f in fam_order),
    }


def page_values(rows, head):
    by_status = Counter(r["status"] for r in rows)
    buildable = len(rows) - by_status["rejected"]
    built = by_status["implemented"]
    shown = [(k, lab) for k, lab in STATUSES if by_status[k]]
    first, last = date_range(rows)
    return {
        "PCT": str(round(100 * built / buildable)),
        "BUILT": str(built),
        "BUILDABLE": str(buildable),
        "TOTAL": str(len(rows)),
        "PARTIAL": str(by_status["partial"]),
        "REJECTED": str(by_status["rejected"]),
        "BLOCKED": str(by_status["blocked"]),
        "HEAD": head,
        "FIRST": first,
        "LAST": last,
        "METER_BUILT": f"{100 * built / buildable:.2f}",
        "METER_PARTIAL": f"{100 * by_status['partial'] / buildable:.2f}",
        "TILES": "".join(
            f'<div class="tile"><div class="tv">{by_status[k]}</div><div class="tl"><span class="key s-{k}"></span>{lab}</div></div>'
            for k, lab in shown
        ),
        "DEFS": "".join(f'<dt><span class="key s-{k}"></span>{lab}</dt><dd>{DEF[k]}</dd>' for k, lab in shown),
        "ST_OPTS": "".join(f'<option value="{k}">{lab}</option>' for k, lab in shown),
        "ROWS": "\n".join(table_row(r) for r in rows),
        **chart_values(rows, by_status),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("rows", nargs="+", help="classified rows, one JSON object per line")
    ap.add_argument("--out", required=True, help="page to write")
    ap.add_argument("--repo", default=".", help="AnkiScape checkout whose main commit the page names")
    args = ap.parse_args()
    rows = load_rows(args.rows)
    head = subprocess.run(["git", "-C", args.repo, "rev-parse", "--short", "main"],
                          capture_output=True, text=True, check=True).stdout.strip()
    values = page_values(rows, head)
    # One pass, so row text that happens to contain {{...}} is never re-substituted.
    page = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: values[m.group(1)], TEMPLATE.read_text())
    Path(args.out).write_text(page)
    print(json.dumps({"total": len(rows), "by_status": Counter(r["status"] for r in rows), "out": args.out}))


if __name__ == "__main__":
    main()
