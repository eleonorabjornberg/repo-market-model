#!/usr/bin/env python3
"""Emit the visual layer: docs/visual/data/*.json and site/index.html (directive 06, #118).

The results page: the plumbing, eight years of the spread, why pressure
happens, and what is known at the decision time (directive 06's descriptive
half); the forecast against its benchmarks and how it is graded (#118's model
half); and how the project was built. Nothing on the page is typed:

* The panel is rebuilt from the tracked fixtures with the repository's own
  `build` command and refused unless its SHA-256 is the published manifest's.
* Every event label and claim about market structure comes from
  `docs/visual/annotations.json`, each with a primary source. `metadata/` is
  read and never written.
* The administered rates in chapter 1 are parsed from a checksummed copy of the
  current FOMC implementation note, never transcribed.
* A placeholder left unfilled is an error, and so is a run record that does
  not declare the as-of information rule (`require_as_of`).
* Every model figure is read from a published run record in `docs/runs/`
  through `from_record`, which refuses a figure no record carries. A model
  figure that no published record carries yet (lead time, the scarcity state)
  is a generated placeholder, and the generator refuses that placeholder once a
  record carries the figure (`pending_figures`).

Every data file carries a provenance block: the commit, the panel's SHA-256 and
the SHA-256 of each input file read. The commit is the latest one that changed
one of `INPUTS`, never the commit that records the output: a file cannot name
the commit that contains it, so a pull request that changes an input commits
that change first, then runs this script and commits the output on top, as
`scripts/emit_status.py` does. It reads git history, so it refuses a shallow
clone unless the commit is passed with `--commit`.

Standard library only, plus this repository's own `src/`.

    python3 scripts/emit_visual.py            # writes docs/visual/data/ and site/index.html
    python3 scripts/emit_visual.py --check    # writes nothing; fails if either is stale
"""
import argparse
import csv
import fnmatch
import hashlib
import html
import json
import math
import re
import statistics
import subprocess
import sys
import tempfile
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model.asof import declared_availability  # noqa: E402
from repo_model.contract import CALENDAR_FEATURES, FEATURE_FIELDS  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

FIXTURES = "tests/fixtures/snapshots/funding_inputs"
MANIFEST = "metadata/funding_panel_manifest.json"
SOURCES = "metadata/sources.json"
EVENTS = "metadata/events.json"
THRESHOLDS = "metadata/stress_thresholds.json"
SPLITS = "metadata/evaluation_splits.json"
ANNOTATIONS = "docs/visual/annotations.json"
TEMPLATE = "site/template.html"
PAGE = "site/index.html"
DATA_DIR = "docs/visual/data"
RUNS = "docs/runs"

#: What the commit stamp is the latest change to. Every file the script reads
#: directly, the fixtures the panel is built from, and the script itself.
INPUTS = (
    "scripts/emit_visual.py",
    TEMPLATE,
    "docs/visual/annotations.json",
    "docs/visual/sources",
    MANIFEST,
    SOURCES,
    EVENTS,
    THRESHOLDS,
    SPLITS,
    FIXTURES,
    f":(glob){RUNS}/*.json",
)

#: Run records the model chapters render: one exceedance record per scored
#: model and benchmark. Each passes `require_as_of`, which fails closed.
MODEL_RECORDS = f"{RUNS}/exceedance_*.json"

#: The pressure probability's benchmarks (`docs/decisions/pressure-probability.md`),
#: by the `model` their records declare, in the order the page draws them.
BENCHMARKS = (
    ("calendar_climatology", "Calendar-type climatology"),
    ("persistence_logistic", "Persistence-logistic"),
)

#: A declared `model` as the page names it. A model not listed is refused
#: rather than shown under a guessed name.
MODEL_NAMES = dict(BENCHMARKS, climatology="Climatology", gbm="Gradient-boosted distribution")

#: The pressure-day types a record splits by, as the page names them.
DAY_TYPES = {"month_end": "Month-end", "ordinary": "Ordinary", "quarter_end": "Quarter-end",
             "tax_date": "Tax date"}

#: Model figures that no published record carries yet: (key, the field a record
#: would carry, what the figure shows). While no record in docs/runs/ carries
#: the field, its chapter renders a generated placeholder; once one does, the
#: generator refuses until the figure is drawn from it.
PENDING = (
    ("lead_time", "lead_time", "lead time to the onset of pressure"),
    ("scarcity", "reserve_scarcity_state", "the reserve-scarcity state against how often pressure came"),
)

#: An order-of-magnitude bound on reserve balances in USD billions, the unit the
#: panel carries since #41. Millions land above it, trillions below it.
RESERVE_BILLIONS = (100.0, 100_000.0)

CLIP_BP = 45  # top of the full-period scale; days above it are drawn off the frame
TYPES = ["Quarter-end", "Month-end", "Tax window", "Coupon settlement", "Other"]
NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                "ten", "eleven", "twelve"]
ALLOWED_SOURCES = (
    "https://www.federalreserve.gov/",
    "https://www.newyorkfed.org/",
    "https://tellerwindow.newyorkfed.org/",
    "https://home.treasury.gov/",
    "https://fiscaldata.treasury.gov/",
    "https://github.com/eleonorabjornberg/repo-market-model/",
)
COLUMN_LABELS = {
    "sofr": "SOFR",
    "iorb": "Rate on reserves (IORB, IOER)",
    "sofr_volume": "SOFR volume",
    "sofr_p25": "SOFR 25th percentile",
    "sofr_p75": "SOFR 75th percentile",
    "tgcr": "TGCR",
    "bgcr": "BGCR",
    "reserve_balances": "Reserve balances",
    "tga": "Treasury General Account",
    "on_rrp": "Overnight reverse repo",
    "treasury_settlement": "Treasury settlements, all",
    "treasury_settlement_bills": "Treasury settlements, bills",
    "treasury_settlement_coupons": "Treasury settlements, coupons",
    "treasury_settlement_soma": "Treasury settlements, Fed add-ons",
    "dealer_treasury_position": "Dealer Treasury positions",
    "tbill_4w": "4-week bill yield",
    "tbill_13w": "13-week bill yield",
    "quarter_end": "Quarter-end flag",
    "tax_date": "Tax-date flag",
    "days_to_month_end": "Days to month-end",
}


class VisualError(ValueError):
    """The page cannot be generated honestly from what is on disk."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(rel, repo):
    return json.loads((repo / rel).read_text(encoding="utf-8"))


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def input_commit(repo):
    """The latest commit that changed one of `INPUTS`."""
    if git(repo, "rev-parse", "--is-shallow-repository") == "true":
        raise VisualError("the clone is shallow, so the latest commit to change an input cannot be "
                          "read; run `git fetch --unshallow` or pass --commit")
    return git(repo, "log", "-1", "--format=%H", "--", *INPUTS)


# ---------------------------------------------------------------- guards


def require_as_of(record, name="record"):
    """Refuse a run record unless every information set in it is the as-of rule.

    Directive 01 records the rule under `derived.information_set.rule`; a
    comparison record carries one per model. A record with none, or with any
    other rule, scored its forecasts under a rule this page does not publish.
    """
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "information_set" and isinstance(value, dict):
                    found.append(value.get("rule"))
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(record)
    if not found:
        raise LookAheadError(f"{name}: declares no information rule; a model chapter renders only "
                             f"records scored under the as-of rule")
    other = sorted({str(rule) for rule in found if rule != "as_of"})
    if other:
        raise LookAheadError(f"{name}: information rule {other} is not the as-of rule; refusing")
    return record


def load_run_record(path):
    return require_as_of(json.loads(Path(path).read_text(encoding="utf-8")), str(path))


def is_published_record(rel):
    """A top-level JSON file in docs/runs/: published, and not archived."""
    rel = str(rel)
    return rel.startswith(RUNS + "/") and "/" not in rel[len(RUNS) + 1:] and rel.endswith(".json")


def from_record(records, rel, *keys):
    """A model figure's value, read from the published record `rel`.

    The only way a model chapter reads a number. It refuses a path outside
    docs/runs/, a record that is not there, and a field the record lacks, so no
    figure is drawn without a published record behind it.
    """
    if not is_published_record(rel):
        raise VisualError(f"{rel}: a model figure reads only a published record in {RUNS}/")
    if rel not in records:
        raise VisualError(f"no published record {rel}: refusing a figure without one")
    node = records[rel]
    for i, key in enumerate(keys):
        if not isinstance(node, dict) or key not in node:
            raise VisualError(f"{rel} carries no {'.'.join(map(str, keys[:i + 1]))}: refusing a figure "
                              f"without a record")
        node = node[key]
    return node


def pending_figures(records):
    """The generated placeholder for each `PENDING` figure no published record carries.

    A record that carries one is refused: the chapter must draw it, not keep a
    placeholder that says no record exists.
    """

    def carries(node, marker):
        if isinstance(node, dict):
            return any(key == marker or carries(value, marker) for key, value in node.items())
        if isinstance(node, list):
            return any(carries(value, marker) for value in node)
        return node == marker

    out = {}
    for key, marker, what in PENDING:
        carriers = sorted(rel for rel, record in records.items() if carries(record, marker))
        if carriers:
            raise VisualError(f"{carriers[0]} carries {marker}, but the page draws no figure of {what} "
                              f"yet: draw it from the record rather than publish a placeholder")
        out[key] = (f"No published record in <code>{RUNS}/</code> carries {what}, so this page draws "
                    f"no figure of it. The generator draws model figures only from such a record, and "
                    f"refuses one that no record carries.")
    return out


def check_reserve_units(rows):
    """Refuse a panel whose reserve balances are not in USD billions."""
    values = [float(r["reserve_balances"]) for r in rows if r.get("reserve_balances")]
    if not values:
        raise VisualError("the panel carries no reserve balances")
    low, high = min(values), max(values)
    if low < RESERVE_BILLIONS[0] or high >= RESERVE_BILLIONS[1]:
        raise VisualError(f"reserve_balances spans {low:,.3f} to {high:,.3f}, outside "
                          f"{RESERVE_BILLIONS[0]:,.0f} to {RESERVE_BILLIONS[1]:,.0f}: the panel is "
                          f"not in USD billions; refusing rather than rescaling")


def check_annotations(notes):
    """Every annotation names a primary source."""
    entries = list(notes["events"]) + list(notes["runoff"]) + list(notes["process"])
    entries += list(notes["guards"]) + [notes["validation"], notes["implementation_note"]]
    entries += list(notes["claims"].values())
    for entry in entries:
        src = entry.get("src", "")
        if not any(src.startswith(prefix) for prefix in ALLOWED_SOURCES):
            raise VisualError(f"annotation {entry} has no primary-source URL")


def fill(template, fills):
    """Fill `{{name}}` placeholders; any left over is an error."""
    out = template
    for key, value in fills.items():
        out = out.replace("{{" + key + "}}", str(value))
    left = sorted(set(re.findall(r"\{\{\w+\}\}", out)))
    if left:
        raise VisualError(f"unfilled placeholders: {left}")
    return out


# ---------------------------------------------------------------- panel


def build_panel(repo, manifest, workdir):
    out = Path(workdir) / "funding_panel.csv"
    cmd = [sys.executable, "-m", "repo_model.cli", "build", "--raw-root", FIXTURES,
           "--output", str(out), "--build-cutoff", manifest["build_cutoff"],
           "--decision-time", manifest["decision_time"]]
    env = {"PYTHONPATH": str(repo / "src"), "PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
    done = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, env=env)
    if done.returncode:
        raise VisualError(f"panel build failed: {done.stderr.strip()[-400:]}")
    digest = sha256(out)
    if digest != manifest["sha256"]:
        raise VisualError(f"panel digest {digest[:12]} is not the published {manifest['sha256'][:12]}; "
                          f"refusing")
    return out.read_bytes(), digest


# ---------------------------------------------------------------- formatting


def day(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def short_day(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def span(a, b):
    x, y = date.fromisoformat(a), date.fromisoformat(b)
    return f"{x.day}–{day(b)}" if (x.year, x.month) == (y.year, y.month) else f"{day(a)} – {day(b)}"


def of(k, n):
    return f"{k} of {n} ({round(100 * k / n)}%)" if n else "no days"


def days(n):
    return f"{n} day" if n == 1 else f"{n} days"


def dash(label):
    return label.replace("-", "–")


def lower_first(label):
    """'Dealer Treasury positions' -> 'dealer Treasury positions'; acronyms such as 'SOFR' stay."""
    return label if label[1:2].isupper() else label[:1].lower() + label[1:]


def word(n):
    return NUMBER_WORDS[n] if 0 <= n < len(NUMBER_WORDS) else str(n)


def bp(value):
    return f"{'+' if value > 0 else '−' if value < 0 else ''}{abs(value)}"


def clock(t):
    h, m = t.hour, t.minute
    suffix = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return f"{h12}{'' if m == 0 else ':%02d' % m} {suffix}"


def link(claim):
    return f"{claim['text']} (<a href='{claim['src']}'>source</a>)."


# ---------------------------------------------------------------- chapter 1


def parse_note(repo, meta):
    """The rates the implementation note states, parsed from its checksummed bytes."""
    path = repo / meta["path"]
    if sha256(path) != meta["sha256"]:
        raise VisualError(f"{meta['path']} does not match its recorded SHA-256; refusing")
    raw = path.read_bytes().decode("utf-8-sig")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)))

    def find(pattern, what):
        m = re.search(pattern, text)
        if not m:
            raise VisualError(f"the implementation note does not state {what}")
        return m.groups()

    def mixed(s):  # "3-3/4" -> 3.75, "4" -> 4
        whole, _, frac = s.strip().partition("-")
        value = Decimal(whole)
        if frac:
            num, den = frac.split("/")
            value += Decimal(num) / Decimal(den)
        return value

    def iso(s):
        return datetime.strptime(s, "%B %d, %Y").date().isoformat()

    issued, = find(r"Implementation Note issued (\w+ \d{1,2}, \d{4})", "its issue date")
    effective, = find(r"Effective (\w+ \d{1,2}, \d{4}), the Federal Open Market Committee directs",
                      "an effective date")
    lo, hi = find(r"target range of ([\d\-/]+) to ([\d\-/]+) percent", "the target range")
    iorb, = find(r"interest rate paid on reserve balances (?:to|at) ([\d.]+) percent", "IORB")
    srp, = find(r"standing overnight repurchase agreement operations at a (?:minimum bid )?rate of "
                r"([\d.]+) percent", "the standing repo rate")
    rrp, = find(r"standing overnight reverse repurchase agreement operations at an offering rate of "
                r"([\d.]+) percent", "the overnight reverse repo rate")
    pcr, = find(r"primary credit rate (?:to|at) ([\d.]+) percent", "the primary credit rate")
    iorb_d = Decimal(iorb)
    rates = [
        {"key": "srp", "name": "Standing repo rate", "who": "Dealers and banks borrow cash from the Fed",
         "v": Decimal(srp)},
        {"key": "pcr", "name": "Primary credit rate", "who": "Banks borrow at the discount window",
         "v": Decimal(pcr)},
        {"key": "iorb", "name": "IORB", "who": "Banks earn it on their reserves", "v": iorb_d},
        {"key": "rrp", "name": "Overnight reverse repo rate",
         "who": "Money funds and other non-banks lend cash to the Fed", "v": Decimal(rrp)},
    ]
    for r in rates:
        r["vs_iorb_bp"] = int((r["v"] - iorb_d) * 100)
        r["v"] = float(r["v"])
    return {
        "issued": iso(issued), "effective": iso(effective),
        "range": [float(mixed(lo)), float(mixed(hi))],
        "rates": rates, "src": meta["src"], "sha256": meta["sha256"],
        "retrieved_at": meta["retrieved_at"],
    }


# ---------------------------------------------------------------- chapter 4


def publication_clock(registry, columns, decision):
    """Each panel input's publication instant relative to the day its value describes.

    Read through `asof.declared_availability`, the same function the as-of rule
    uses, on a synthetic run of consecutive days so that one row is one day.
    """
    dates = [date(2001, 1, 1) + timedelta(days=i) for i in range(60)]
    pos = 30
    origin = datetime.combine(dates[pos], time.min)
    out = []
    for column in columns:
        label = COLUMN_LABELS.get(column, column)
        if column in CALENDAR_FEATURES:
            out.append({"column": column, "label": label, "kind": "calendar"})
            continue
        seen = {}
        for source_id, field in FEATURE_FIELDS[column]:
            source = registry[source_id]
            scheduled = source.get("scheduled_availability") or {}
            if field in (scheduled.get("fields") or ()):
                decl, kind = scheduled, "scheduled"
            else:
                decl = (source.get("field_release_lags") or {}).get(field) or source["release_lag"]
                kind = "retrieval" if decl.get("basis") == "snapshot_retrieved_at" else "observed"
            at = declared_availability(registry, source_id, field, dates, pos)
            key = (kind, decl.get("days"), decl.get("unit"), decl.get("available_time"))
            if key in seen:
                seen[key]["fields"].append(field)
                continue
            entry = {"column": column, "label": label, "kind": kind, "source": source_id,
                     "provider": source.get("provider", source_id), "fields": [field],
                     "unit": decl.get("unit"), "days": decl.get("days"),
                     "time": decl.get("available_time")}
            if at is not None:
                offset = (at - origin) / timedelta(days=1)
                entry["offset"] = round(offset, 4)
                whole = math.floor(offset)
                late = at.time() > decision
                entry["read_lag"] = whole + (1 if late else 0)
            seen[key] = entry
        out.extend(seen.values())
    return out


# ---------------------------------------------------------------- chapters 2 and 3


def classify(rows):
    for i, r in enumerate(rows):
        if i + 1 < len(rows):
            nxt = rows[i + 1]["date"]
        else:  # the panel's last row: its successor is not in the panel, so use the next weekday
            d = date.fromisoformat(r["date"])
            nxt = (d + timedelta(days=3 if d.weekday() == 4 else 1)).isoformat()
        last_bd = nxt[5:7] != r["date"][5:7]
        if r["quarter_end"] == "1":
            r["t"] = 0
        elif last_bd:
            r["t"] = 1
        elif r["tax_date"] == "1":
            r["t"] = 2
        elif float(r["treasury_settlement_coupons"]) > 0:
            r["t"] = 3
        else:
            r["t"] = 4


def regime_views(regimes, rows, clip_bp, second_bp):
    first, last = rows[0]["date"], rows[-1]["date"]
    floor = max(-25, 5 * math.floor(min(r["s"] for r in rows) / 5))
    views = [{"k": "all", "label": "All years", "x": [first, last], "y": [floor, clip_bp]}]
    for g in regimes:
        lo, hi = max(g["first"], first), min(g["last"], last)
        inside = sorted(r["s"] for r in rows if lo <= r["date"] <= hi)
        if not inside:
            continue
        top = inside[min(len(inside) - 1, math.ceil(0.995 * len(inside)) - 1)]
        views.append({"k": g["label"], "label": dash(g["label"]), "x": [lo, hi],
                      "y": [5 * math.floor((inside[0] - 2) / 5), max(second_bp + 5, 10 * math.ceil((top + 5) / 10))]})
    return views


def history(rows, notes, thresholds, regimes, windows):
    taus = [int(t) for t in thresholds["taus_bp"]]
    pressure_bp, second_bp, tail_bp = taus[0], taus[1], taus[-1]
    out_rows = []
    for r in rows:
        iorb = Decimal(r["iorb"])
        r["s"] = int((Decimal(r["sofr"]) - iorb) * 100)
        r["res"] = float(r["reserve_balances"]) / 1e3  # USD billions -> trillions, for the axis
    classify(rows)
    for r in rows:
        iorb = Decimal(r["iorb"])
        band = [None, None]
        if r["sofr_p25"] and r["sofr_p75"]:
            band = [int((Decimal(r["sofr_p25"]) - iorb) * 100), int((Decimal(r["sofr_p75"]) - iorb) * 100)]
        out_rows.append([r["date"], r["s"], band[0], band[1], float(r["sofr"]), float(iorb),
                         round(r["res"], 3), r["t"]])

    def in_regime(r, g):
        return g["first"] <= r["date"] <= g["last"]

    def pressure(r):
        return r["s"] > pressure_bp

    def med(g):
        return round(statistics.median(r["res"] for r in rows if in_regime(r, g) and pressure(r)), 2)

    def type_count(g, t):
        n = [r for r in rows if in_regime(r, g) and r["t"] == t]
        return sum(1 for r in n if pressure(r)), len(n)

    live = [g for g in regimes if any(in_regime(r, g) for r in rows)]
    early, late = live[0], live[-1]
    ample = max(live, key=lambda g: statistics.median(r["res"] for r in rows if in_regime(r, g)))
    yr = lambda r: int(r["date"][:4])
    years = list(range(yr(rows[0]), yr(rows[-1]) + 1))
    cells = {(y, t): [0, 0] for y in years for t in range(len(TYPES))}
    for r in rows:
        c = cells[(yr(r), r["t"])]
        c[0] += 1
        c[1] += pressure(r)
    head = "".join(f"<th scope='col'>{y}{' (to ' + short_day(rows[-1]['date'])[:-5] + ')' if y == years[-1] else ''}</th>"
                   for y in years)
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

    spike = max(rows, key=lambda r: r["s"])
    tail = [r for r in rows if r["s"] > tail_bp]
    tail_years = sorted({yr(r) for r in tail})
    events = [{"date": e["date"], "src": e["src"],
               "text": e["text"].format(spike_sofr=f"{float(spike['sofr']):.2f}%", spike_bp=spike["s"])}
              for e in notes["events"]]
    iorb_from = next(e["date"] for e in notes["events"] if e.get("role") == "iorb_from")
    late_qe = type_count(late, 0)
    quiet = all(type_count(ample, t)[0] == 0 for t in range(len(TYPES)))
    off = sum(1 for r in rows if r["s"] > CLIP_BP)
    above = lambda g: sum(1 for r in rows if in_regime(r, g) and r["s"] > 0)
    span_years = (date.fromisoformat(rows[-1]["date"]) - date.fromisoformat(rows[0]["date"])).days / 365.25
    fills = {
        "n_years_word": word(int(span_years)).capitalize(),
        "latest_volume": f"${float(rows[-1]['sofr_volume']) / 1000:.1f} trillion",
        "early": dash(early["label"]), "late": dash(late["label"]), "ample": dash(ample["label"]),
        "above_ample": days(above(ample)), "above_late": days(above(late)),
        "pressure_bp": pressure_bp, "second_bp": second_bp, "tail_bp": tail_bp,
        "n_tail": days(len(tail)),
        "tail_where": ("all in " + str(tail_years[0]) if len(tail_years) == 1 else
                       "all in " + f"{tail_years[0]}–{str(tail_years[1])[2:]}" if len(tail_years) == 2 and tail_years[1] - tail_years[0] == 1
                       else "in " + ", ".join(map(str, tail_years))) if tail_years else "none",
        "spike_bp": bp(spike["s"]), "spike_day": day(spike["date"]),
        "spike_month": date.fromisoformat(spike["date"]).strftime("%B %Y"),
        "med_early": f"${med(early):.2f} trillion", "med_late": f"${med(late):.2f} trillion",
        "ord_early": of(*type_count(early, 4)), "ord_late": of(*type_count(late, 4)),
        "qe_late": f"{late_qe[0]} of {late_qe[1]}",
        "quiet_ample": "there were none" if quiet else "there were a few",
        "band_missing": days(sum(1 for r in out_rows if r[2] is None)),
        "holdouts": " and ".join(span(w["start"], w["end"]) for w in windows),
        "holdout_months": " and ".join(date.fromisoformat(w["start"]).strftime("%B %Y") for w in windows),
        "iorb_from": day(iorb_from),
        "iorb_event_n": 1 + next(i for i, e in enumerate(notes["events"]) if e.get("role") == "iorb_from"),
        "ioer_until": day((date.fromisoformat(iorb_from) - timedelta(days=1)).isoformat()),
        "heat_table": table, "clip_bp": CLIP_BP,
        "n_off_scale": days(off).capitalize(), "n_off_scale_lc": days(off),
        "event_list": "".join(
            f"<li data-i='{i}'><time>{short_day(e['date'])}</time> {e['text']}. <a href='{e['src']}'>Source</a></li>"
            for i, e in enumerate(events)),
        "c_reserve_ratio": link(notes["claims"]["reserve_ratio"]),
        "c_quarter_end": link(notes["claims"]["quarter_end"]),
        "c_tax_date": link(notes["claims"]["tax_date"]),
        "c_settlement": link(notes["claims"]["settlement"]),
        "c_coupon_demand": link(notes["claims"]["coupon_demand"]),
    }
    data = {
        "rows": out_rows, "types": TYPES, "events": events,
        "runoff": [{"start": b["start"], "end": b["end"]} for b in notes["runoff"]],
        "holdouts": [{"start": w["start"], "end": w["end"]} for w in windows],
        "medians": [{"label": dash(early["label"]), "v": med(early)}, {"label": dash(late["label"]), "v": med(late)}],
        "views": regime_views(regimes, rows, CLIP_BP, second_bp),
        "res_domain": [math.floor(10 * min(r["res"] for r in rows)) / 10, math.ceil(10 * max(r["res"] for r in rows)) / 10],
        "iorb_from": iorb_from, "pressure_bp": pressure_bp, "second_bp": second_bp, "clip_bp": CLIP_BP,
    }
    return data, fills


# ---------------------------------------------------------------- chapters 5 to 7


def run_records(repo):
    """{relative path: content} for every published record: each top-level JSON file in docs/runs/."""
    return {f"{RUNS}/{p.name}": json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((Path(repo) / RUNS).glob("*.json"))}


def model_label(declaration, rel):
    model = declaration.get("model")
    if model not in MODEL_NAMES:
        raise VisualError(f"{rel}: no page name for the model {model!r}; refusing to guess one")
    parts = [MODEL_NAMES[model]]
    if declaration.get("calibration"):
        parts.append(declaration["calibration"].replace("_", "-"))
    if model == "gbm":
        parts.append(f"{len(declaration['features'])} inputs")
    return ", ".join(parts)


def thin_curve(points):
    """A CORP curve's points without those inside a flat run, so the drawn line is unchanged."""
    keyed = [tuple(p[k] for k in ("forecast", "recalibrated", "lower", "upper")) for p in points]
    keep = [k for i, k in enumerate(keyed)
            if i in (0, len(keyed) - 1) or k[1:] != keyed[i - 1][1:] or k[1:] != keyed[i + 1][1:]]
    return [[None if v is None else round(v, 5) for v in k] for k in keep]


def model_chapters(records, taus):
    """Chapters 5 and 6, from the published exceedance records alone.

    Every number is read through `from_record`. The scored models are the
    records whose model is not a benchmark; each is drawn against both
    benchmarks, paired, with its interval, by regime and by pressure-day type.
    """
    found = sorted(rel for rel in records if fnmatch.fnmatchcase(rel, MODEL_RECORDS))
    if not found:
        raise VisualError(f"no {MODEL_RECORDS} record: the model chapters have nothing to draw from")
    keys = {}
    for rel in found:
        require_as_of(from_record(records, rel), rel)
        keys[rel] = (from_record(records, rel, "panel", "sha256"), from_record(records, rel, "folds", "count"),
                     from_record(records, rel, "folds", "first", "scored_date"),
                     from_record(records, rel, "folds", "last", "scored_date"))
    if len(set(keys.values())) != 1:
        raise VisualError(f"the exceedance records are not scored on one panel and one set of days: {keys}")
    panel, n_days, first, last = keys[found[0]]
    names = dict(BENCHMARKS)
    tau_keys = [f"{float(t):g}" for t in taus]
    models = []
    for rel in found:
        declaration = from_record(records, rel, "declaration")
        model = declaration.get("model")
        entry = {"record": rel, "label": model_label(declaration, rel), "benchmark": model in names,
                 "inputs": [COLUMN_LABELS.get(f, f) for f in from_record(records, rel, "declaration", "features")],
                 "by_tau": {}}
        for k in tau_keys:
            row = ("metrics", "by_tau", k)
            decomposition = row + ("decomposition",)
            t = {
                "brier": from_record(records, rel, *row, "brier"),
                "base_rate": from_record(records, rel, *row, "base_rate"),
                "positives": from_record(records, rel, *row, "positives"),
                "reliability": from_record(records, rel, *decomposition, "reliability"),
                "resolution": from_record(records, rel, *decomposition, "resolution"),
                "uncertainty": from_record(records, rel, *decomposition, "uncertainty"),
                "curve": thin_curve(from_record(records, rel, *row, "reliability_curve", "points")),
                "vs": {},
            }
            if from_record(records, rel, *row, "reliability_curve", "method") != "corp_isotonic":
                raise VisualError(f"{rel}: the reliability curve at {k} bp is not CORP")
            if not entry["benchmark"]:
                for name, _ in BENCHMARKS:
                    paired = ("benchmarks", name, "by_tau", k, "paired_brier_difference")
                    vs = {"mean": from_record(records, rel, *paired, "mean"),
                          "lower": from_record(records, rel, *paired, "interval", "lower"),
                          "upper": from_record(records, rel, *paired, "interval", "upper"),
                          "level": from_record(records, rel, *paired, "interval", "level"),
                          "benchmark_brier": from_record(records, rel, "benchmarks", name, "by_tau", k,
                                                         "benchmark_brier")}
                    for split, label in (("by_regime", dash), ("by_day_type", None)):
                        groups = from_record(records, rel, *paired, "splits", split)
                        out = []
                        for group in groups:
                            if label is None and group not in DAY_TYPES:
                                raise VisualError(f"{rel}: no page name for the day type {group!r}")
                            g = paired + ("splits", split, group)
                            out.append([label(group) if label else DAY_TYPES[group],
                                        from_record(records, rel, *g, "count"), from_record(records, rel, *g, "mean"),
                                        from_record(records, rel, *g, "interval", "lower"),
                                        from_record(records, rel, *g, "interval", "upper")])
                        vs[split] = out
                    t["vs"][name] = vs
            entry["by_tau"][k] = t
        models.append(entry)
    labels = [m["label"] for m in models]
    if len(set(labels)) != len(labels):
        raise VisualError(f"two exceedance records share a page name: {labels}")
    scored = [m for m in models if not m["benchmark"]]
    if not scored:
        raise VisualError("every exceedance record is a benchmark: no scored model to draw")
    levels = {vs["level"] for m in scored for t in m["by_tau"].values() for vs in t["vs"].values()}
    if len(levels) != 1:
        raise VisualError(f"the paired intervals are not at one level: {sorted(levels)}")
    level = round(100 * levels.pop())

    def beats(k, n, first_clause):
        if k == 0:
            return f"none of the {word(n)} scored models beats" if first_clause else "none beats"
        if k == n:
            return f"all {word(n)} scored models beat" if first_clause else f"all {word(n)} beat"
        verb = "beats" if k == 1 else "beat"
        return f"{word(k)} of the {word(n)} scored models {verb}" if first_clause else f"{word(k)} {verb}"

    def tally(k):
        return [sum(1 for m in scored if m["by_tau"][k]["vs"][name]["lower"] > 0) for name, _ in BENCHMARKS]

    (_, cal_label), (_, per_label) = BENCHMARKS
    sentences = []
    for i, k in enumerate(tau_keys):
        a, b = tally(k)
        sentences.append(f"At +{k} bp, {beats(a, len(scored), i == 0)} {lower_first(cal_label)}"
                         f"{f' with a {level}% interval above zero' if i == 0 else ''}, and "
                         f"{beats(b, len(scored), False)} the {lower_first(per_label)}.")
    k0 = tau_keys[0]
    share = sorted((m["by_tau"][k0]["reliability"] / m["by_tau"][k0]["brier"], m["label"]) for m in models)
    data = {
        "taus": tau_keys, "level": level,
        "benchmarks": [{"key": name, "label": label} for name, label in BENCHMARKS],
        "scored": {"days": n_days, "first": first, "last": last, "panel": panel},
        "models": models,
    }
    fills = {
        "forecast_lede": " ".join(sentences),
        "n_scored_models": word(len(scored)), "n_models": word(len(models)),
        "model_days": f"{n_days:,}", "model_first": day(first), "model_last": day(last),
        "interval_level": level, "tau_first": k0, "tau_second": tau_keys[-1],
        "base_first": f"{100 * models[0]['by_tau'][k0]['base_rate']:.1f}%",
        "miscal_low": f"{100 * share[0][0]:.0f}%", "miscal_low_model": lower_first(share[0][1]),
        "miscal_high": f"{100 * share[-1][0]:.0f}%", "miscal_high_model": lower_first(share[-1][1]),
    }
    if len({m["by_tau"][k0]["base_rate"] for m in models}) != 1:
        raise VisualError("the exceedance records disagree on how often pressure came")
    return data, fills


# ---------------------------------------------------------------- the page


def generate(repo, commit=None):
    """Return {relative path: bytes} for every output. Writes nothing."""
    repo = Path(repo)
    manifest = read_json(MANIFEST, repo)
    registry = read_json(SOURCES, repo)
    notes = read_json(ANNOTATIONS, repo)
    thresholds = read_json(THRESHOLDS, repo)
    regimes = read_json(SPLITS, repo)["regimes"]
    windows = read_json(EVENTS, repo)["windows"]
    check_annotations(notes)
    records = run_records(repo)
    model, model_fills = model_chapters(records, thresholds["taus_bp"][:2])
    pending = pending_figures(records)
    commit = commit or input_commit(repo)

    with tempfile.TemporaryDirectory() as tmp:
        raw, digest = build_panel(repo, manifest, tmp)
    if model["scored"]["panel"] != digest:
        raise VisualError(f"the exceedance records are scored on panel {model['scored']['panel'][:12]}, not the "
                          f"published {digest[:12]}; refusing")
    rows = list(csv.DictReader(raw.decode().splitlines()))
    check_reserve_units(rows)
    decision = time.fromisoformat(manifest["decision_time"])

    hist, fills = history(rows, notes, thresholds, regimes, windows)
    note = parse_note(repo, notes["implementation_note"])
    last = rows[-1]
    iorb_last = Decimal(last["iorb"])
    plumbing = {
        "note": note,
        "last_day": last["date"],
        "segments": [
            {"key": k, "rate": float(last[k]), "vs_iorb_bp": int((Decimal(last[k]) - iorb_last) * 100),
             "text": notes["claims"]["segments_" + k]["text"], "src": notes["claims"]["segments_" + k]["src"]}
            for k in ("tgcr", "bgcr", "sofr")],
    }
    clock_rows = publication_clock(registry, manifest["built_columns"], decision)
    observed = [c for c in clock_rows if c["kind"] == "observed" and "read_lag" in c]
    stalest = max(observed, key=lambda c: (c["read_lag"], c["unit"] == "business_days"))
    freshest = min(observed, key=lambda c: (c["read_lag"], c["unit"] != "business_days"))
    sched = [c for c in clock_rows if c["kind"] == "scheduled"]
    srp = next(r for r in note["rates"] if r["key"] == "srp")
    rrp = next(r for r in note["rates"] if r["key"] == "rrp")
    c = notes["claims"]
    fills.update({
        "first_day": day(rows[0]["date"]), "last_day": day(last["date"]),
        "n_rows": f"{len(rows):,}", "sha": digest, "sha12": digest[:12],
        "commit": commit, "commit12": commit[:12],
        "decision": clock(decision), "decision_24": decision.strftime("%H:%M"),
        "note_issued": day(note["issued"]), "note_effective": day(note["effective"]),
        "note_src": note["src"], "note_sha": note["sha256"], "note_retrieved": note["retrieved_at"],
        "srp_vs_iorb": bp(srp["vs_iorb_bp"]), "rrp_vs_iorb": bp(rrp["vs_iorb_bp"]),
        "c_segments_tgcr": link(c["segments_tgcr"]), "c_segments_bgcr": link(c["segments_bgcr"]),
        "c_segments_sofr": link(c["segments_sofr"]), "c_sofr_trim": link(c["sofr_trim"]),
        "c_sofr_publication": link(c["sofr_publication"]),
        "c_triparty_actors": link(c["triparty_actors"]), "c_cleared_actors": link(c["cleared_actors"]),
        "c_fed_cash": link(c["fed_cash"]), "c_standing_repo": link(c["standing_repo"]),
        "n_inputs": word(len({r["column"] for r in clock_rows if r["kind"] != "calendar"})),
        "n_calendar": word(sum(1 for r in clock_rows if r["kind"] == "calendar")),
        "lag_min": f"{days(freshest['read_lag'])} old",
        "lag_max": f"{lower_first(stalest['label'])}, {stalest['read_lag']} {stalest['unit'].replace('_', ' ')} old",
        "sched_names": " and ".join(sorted({r["label"].split(",")[0] for r in sched})) or "none",
        "process_list": "".join(f"<li><b>{p['step']}</b><span>{p['text']}. <a href='{p['src']}'>Rule</a></span></li>"
                                for p in notes["process"]),
        "guard_list": "".join(f"<li><b>{g['name']}.</b> {g['text']}. <a href='{g['src']}'>Source</a></li>"
                              for g in notes["guards"]),
        "validation": link(notes["validation"]),
        "lead_time_placeholder": pending["lead_time"],
        "scarcity_placeholder": pending["scarcity"],
    })
    fills.update(model_fills)

    inputs = {rel: sha256(repo / rel) for rel in
              (MANIFEST, SOURCES, EVENTS, THRESHOLDS, SPLITS, ANNOTATIONS, TEMPLATE, notes["implementation_note"]["path"])}
    provenance = {
        "commit": commit,
        "generator": "scripts/emit_visual.py",
        "panel": {"sha256": digest, "rows": len(rows), "first": rows[0]["date"], "last": last["date"],
                  "built_from": FIXTURES, "manifest": MANIFEST},
        "inputs": inputs,
    }
    build = {"process": notes["process"], "guards": notes["guards"], "validation": notes["validation"]}
    clock_data = {"decision_time": decision.strftime("%H:%M"), "inputs": clock_rows}
    model_provenance = dict(provenance, inputs={rel: sha256(repo / rel) for rel in records})
    payloads = {"history": hist, "plumbing": plumbing, "clock": clock_data, "build": build, "model": model}
    out = {}
    for name, payload in payloads.items():
        doc = {"provenance": model_provenance if name == "model" else provenance, "data": payload}
        out[f"{DATA_DIR}/{name}.json"] = (json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                                      ensure_ascii=False) + "\n").encode("utf-8")
    page_data = {k: payloads[k] for k in ("history", "plumbing", "clock", "model")}
    template = (repo / TEMPLATE).read_text(encoding="utf-8")
    if "/*__DATA__*/null" not in template:
        raise VisualError("the template has no /*__DATA__*/null slot")
    page = template.replace("/*__DATA__*/null", json.dumps(page_data, sort_keys=True, separators=(",", ":"),
                                                            ensure_ascii=False).replace("</", "<\\/"))
    out[PAGE] = fill(page, fills).encode("utf-8")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--check", action="store_true", help="write nothing; fail if an output is stale")
    parser.add_argument("--commit", help="stamp this commit instead of reading git history")
    parser.add_argument("--repo", default=str(ROOT), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    repo = Path(args.repo)
    try:
        outputs = generate(repo, args.commit)
    except (VisualError, LookAheadError) as exc:
        sys.exit(f"emit_visual: {exc}")
    stale = [rel for rel, data in outputs.items()
             if not (repo / rel).exists() or (repo / rel).read_bytes() != data]
    if args.check:
        if stale:
            sys.exit("emit_visual: stale, regenerate with `python3 scripts/emit_visual.py`: " + ", ".join(stale))
        print("emit_visual: up to date")
        return
    for rel, data in outputs.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes(data)
    print(f"emit_visual: wrote {', '.join(sorted(outputs))}")


if __name__ == "__main__":
    main()
