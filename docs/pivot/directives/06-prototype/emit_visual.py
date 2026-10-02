#!/usr/bin/env python3
"""Prototype of scripts/emit_visual.py (directive 06): chapters 2 and 3 of the explorer.

Reads the funding panel, refuses unless its SHA-256 is the published digest, and fills
template.html with data and every number the copy quotes. Nothing on the page is typed:
a placeholder left unfilled is an error. Standard library only.

    python3 emit_visual.py PANEL_CSV REPO_DIR TEMPLATE OUT_HTML
"""
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

EXPECTED_SHA = "9f7d6881a2181b35394daf8097a10e8ad3567250c75383072d11ecb78132e30a"
PRESSURE_BP = 5
CLIP_BP = 45  # top of the full-period scale; days above it are drawn off the frame
TYPES = ["Quarter-end", "Month-end", "Tax window", "Coupon settlement", "Other"]

# Sourced annotations. In the repo these live in docs/visual/annotations.json, never in
# metadata/ (a change there would make every record unpublishable under the publish rule).
EVENTS = [
    ("2019-07-31", "FOMC ends balance-sheet runoff two months early, effective August",
     "https://www.federalreserve.gov/newsevents/pressreleases/monetary20190731a.htm"),
    ("2019-09-17", "SOFR prints {spike_sofr}, {spike_bp} bp above IOER",
     "https://www.federalreserve.gov/econres/notes/feds-notes/what-happened-in-money-markets-in-september-2019-20200227.html"),
    ("2019-10-11", "Fed announces Treasury bill purchases to keep reserves ample",
     "https://www.federalreserve.gov/newsevents/pressreleases/monetary20191011a.htm"),
    ("2020-03-15", "Fed cuts rates to near zero and announces large asset purchases",
     "https://www.federalreserve.gov/newsevents/pressreleases/monetary20200315a.htm"),
    ("2021-07-29", "IORB replaces IOER as the Fed's rate on reserves",
     "https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/decisions/iorb-availability.md"),
    ("2022-06-01", "Balance-sheet runoff resumes",
     "https://federalreserve.gov/monetarypolicy/policy-normalization.htm"),
    ("2025-12-01", "Runoff ends, as announced on 29 Oct 2025",
     "https://federalreserve.gov/monetarypolicy/policy-normalization.htm"),
    ("2025-12-10", "FOMC starts reserve-management purchases of bills",
     "https://www.newyorkfed.org/medialibrary/media/markets/omo/omo2025-pdf.pdf"),
]
RUNOFF = [("2017-10-01", "2019-08-01"), ("2022-06-01", "2025-12-01")]


def fail(msg):
    sys.exit(f"emit_visual: {msg}")


def day(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def span(a, b):
    x, y = date.fromisoformat(a), date.fromisoformat(b)
    return f"{x.day}–{day(b)}" if (x.year, x.month) == (y.year, y.month) else f"{day(a)} – {day(b)}"


def of(k, n):
    return f"{k} of {n} ({round(100 * k / n)}%)" if n else "no days"


def days(n):
    return f"{n} day" if n == 1 else f"{n} days"


def main(panel, repo, template, out):
    raw = Path(panel).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA:
        fail(f"panel digest {sha[:12]} is not the published {EXPECTED_SHA[:12]}; refusing")
    rows = list(csv.DictReader(raw.decode().splitlines()))

    windows = json.loads((Path(repo) / "metadata/events.json").read_text())["windows"]
    commit = subprocess.run(["git", "-C", repo, "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()

    out_rows = []
    for i, r in enumerate(rows):
        iorb = Decimal(r["iorb"])
        r["s"] = int((Decimal(r["sofr"]) - iorb) * 100)
        if i + 1 < len(rows):
            nxt = rows[i + 1]["date"]
        else:  # the panel's last row: its successor is not in the panel, so use the next weekday
            d = date.fromisoformat(r["date"])
            nxt = (d + timedelta(days=3 if d.weekday() == 4 else 1)).isoformat()
        last_bd = nxt[5:7] != r["date"][5:7]
        month = int(r["date"][5:7])
        if last_bd and month in (3, 6, 9, 12):
            t = 0
        elif last_bd:
            t = 1
        elif r["tax_date"] == "1":
            t = 2
        elif float(r["treasury_settlement_coupons"]) > 0:
            t = 3
        else:
            t = 4
        r["t"] = t
        band = [None, None]
        if r["sofr_p25"] and r["sofr_p75"]:
            band = [int((Decimal(r["sofr_p25"]) - iorb) * 100), int((Decimal(r["sofr_p75"]) - iorb) * 100)]
        out_rows.append([r["date"], r["s"], band[0], band[1], float(r["sofr"]), float(iorb),
                         round(float(r["reserve_balances"]) / 1e3, 3), t])

    yr = lambda r: int(r["date"][:4])
    above = lambda ys: sum(1 for r in rows if yr(r) in ys and r["s"] > 0)
    spike = max(rows, key=lambda r: r["s"])
    ge50 = [r for r in rows if r["s"] >= 50]
    ge50_years = sorted({yr(r) for r in ge50})
    med = lambda lo, hi: round(statistics.median(
        float(r["reserve_balances"]) / 1e3 for r in rows if lo <= yr(r) <= hi and r["s"] >= PRESSURE_BP), 2)

    years = list(range(yr(rows[0]), yr(rows[-1]) + 1))
    cells = {(y, t): [0, 0] for y in years for t in range(len(TYPES))}
    for r in rows:
        c = cells[(yr(r), r["t"])]
        c[0] += 1
        c[1] += r["s"] >= PRESSURE_BP
    quiet = all(cells[(y, t)][1] == 0 for y in (2021, 2022, 2023) for t in range(len(TYPES)))

    head = "".join(f"<th scope='col'>{y}{' (to ' + day(rows[-1]['date'])[:-5] + ')' if y == years[-1] else ''}</th>" for y in years)
    body = []
    for t, name in enumerate(TYPES):
        tds = []
        for y in years:
            n, k = cells[(y, t)]
            share = k / n if n else 0
            cls = " class='hot'" if share > 0.5 else ""
            tds.append(f"<td{cls} style='--share:{round(100 * share)}%'><b>{k}</b><span> of {n}</span></td>")
        body.append(f"<tr><th scope='row'>{name}</th>{''.join(tds)}</tr>")
    table = f"<table><thead><tr><th></th>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"

    vol = rows[-1]["sofr_volume"]
    fills = {
        "latest_volume": f"${float(vol) / 1000:.1f} trillion",
        "above_2021_23": days(above({2021, 2022, 2023})),
        "above_2025": days(above({2025})),
        "n_ge50": days(len(ge50)),
        "ge50_where": (f"all in {ge50_years[0]}" if len(ge50_years) == 1 else
                       f"all in {ge50_years[0]}–{str(ge50_years[1])[2:]}" if len(ge50_years) == 2 and ge50_years[1] - ge50_years[0] == 1
                       else "in " + ", ".join(map(str, ge50_years))),
        "spike_bp": f"+{spike['s']}",
        "spike_day": day(spike["date"]),
        "med_1819": f"${med(2018, 2019):.2f} trillion",
        "med_2526": f"${med(2025, 2026):.2f} trillion",
        "ord_2019": of(cells[(2019, 4)][1], cells[(2019, 4)][0]),
        "ord_2025": of(cells[(2025, 4)][1], cells[(2025, 4)][0]),
        "qe_2025": f"{cells[(2025, 0)][1]} of {cells[(2025, 0)][0]}",
        "quiet_2021_23": "there were none" if quiet else "there were a few",
        "band_missing": days(sum(1 for r in out_rows if r[2] is None)),
        "n_rows": f"{len(rows):,}",
        "first_day": day(rows[0]["date"]),
        "last_day": day(rows[-1]["date"]),
        "sha": sha,
        "sha12": sha[:12],
        "commit": commit,
        "holdouts": " and ".join(span(w["start"], w["end"]) for w in windows),
        "heat_table": table,
        "clip_bp": CLIP_BP,
        "n_off_scale": days(sum(1 for r in rows if r["s"] > CLIP_BP)).capitalize(),
        "n_off_scale_lc": days(sum(1 for r in rows if r["s"] > CLIP_BP)),
    }
    events = [{"date": d, "text": t.format(spike_sofr=f"{float(spike['sofr']):.2f}%", spike_bp=spike["s"]), "src": s}
              for d, t, s in EVENTS]
    fills["event_list"] = "".join(
        f"<li data-i='{i}'><time>{day(e['date'])}</time> {e['text']}. <a href='{e['src']}'>Source</a></li>"
        for i, e in enumerate(events))
    data = {
        "rows": out_rows, "types": TYPES, "events": events,
        "runoff": [{"start": a, "end": b} for a, b in RUNOFF],
        "holdouts": [{"start": w["start"], "end": w["end"]} for w in windows],
        "medians": [{"label": "2018–19", "v": med(2018, 2019)}, {"label": "2025–26", "v": med(2025, 2026)}],
        "iorb_from": "2021-07-29", "pressure_bp": PRESSURE_BP, "clip_bp": CLIP_BP,
    }

    html = Path(template).read_text()
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    for k, v in fills.items():
        html = html.replace("{{" + k + "}}", str(v))
    left = re.findall(r"\{\{\w+\}\}", html)
    if left:
        fail(f"unfilled placeholders: {sorted(set(left))}")
    Path(out).write_text(html)
    print(f"wrote {out}: panel {sha[:12]}, commit {commit}, {len(rows)} rows")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        fail(__doc__.strip().splitlines()[-1].strip())
    main(*sys.argv[1:])
