#!/usr/bin/env python3
"""Emit the visual layer: docs/visual/data/*.json and site/index.html (directive 06).

The descriptive half of the results page: the plumbing, eight years of the
spread, why pressure happens, and what is known at the decision time, plus how
the project was built. Nothing on the page is typed:

* The panel is rebuilt from the tracked fixtures with the repository's own
  `build` command and refused unless its SHA-256 is the published manifest's.
* Every event label and claim about market structure comes from
  `docs/visual/annotations.json`, each with a primary source. `metadata/` is
  read and never written.
* The administered rates in chapter 1 are parsed from a checksummed copy of the
  current FOMC implementation note, never transcribed.
* A placeholder left unfilled is an error, and so is a run record that does
  not declare the as-of information rule (`require_as_of`).
* The "Start here" block above the chapters is the newcomer layer (#141). Its
  terms come from `docs/visual/glossary.json`, each with a primary source, and
  days in a lockbox tier not yet opened (`metadata/lockbox.json`) are drawn
  grey, labelled "held out", and left out of every count and sentence it writes.

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

from repo_model import lockbox  # noqa: E402
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
GLOSSARY = "docs/visual/glossary.json"
LOCKBOX = "metadata/lockbox.json"
TEMPLATE = "site/template.html"
PAGE = "site/index.html"
DATA_DIR = "docs/visual/data"

#: What the commit stamp is the latest change to. Every file the script reads
#: directly, the fixtures the panel is built from, and the script itself.
INPUTS = (
    "scripts/emit_visual.py",
    TEMPLATE,
    "docs/visual/annotations.json",
    GLOSSARY,
    "docs/visual/sources",
    MANIFEST,
    SOURCES,
    EVENTS,
    THRESHOLDS,
    SPLITS,
    LOCKBOX,
    FIXTURES,
)

#: Run records the model chapters render. Empty until chapters 5 to 7 are built
#: (plan step 6); each one passes `load_run_record`, which fails closed.
MODEL_RECORDS = ()

#: An order-of-magnitude bound on reserve balances in USD billions, the unit the
#: panel carries since #41. Millions land above it, trillions below it.
RESERVE_BILLIONS = (100.0, 100_000.0)

CLIP_BP = 45  # top of the full-period scale; days above it are drawn off the frame

#: The newcomer layer's views (#141), in reading order: (section id, title, subtitle).
#: The "Start here" nav lists only those whose section the template carries, so
#: a half-built layer never shows a dead link.
NEWCOMER_VIEWS = (
    ("n1", "What is pressure?", "The line this project watches"),
    ("n2", "Why is this hard?", "Pressure days are rare"),
    ("n3", "When does it happen?", "Scarce cash and the calendar"),
    ("n4", "Who lends to whom", "The market map"),
    ("n5", "A quarter-end squeeze", "Step by step"),
)

#: Events from `annotations.json` that N1 marks on its chart, by date.
N1_EPISODES = ("2019-09-17", "2020-03-15", "2022-06-01", "2025-12-01")
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


def check_glossary(glossary):
    """Every glossary term has a unique key, a printed form, a definition and a primary source."""
    seen = set()
    for entry in glossary["terms"]:
        key = entry.get("key", "")
        if not re.fullmatch(r"\w+", key) or key in seen:
            raise VisualError(f"glossary entry {entry} has no unique key")
        seen.add(key)
        for field in ("term", "text", "definition"):
            if not str(entry.get(field, "")).strip():
                raise VisualError(f"glossary term {key!r} has no {field}")
        if not entry.get("match"):
            raise VisualError(f"glossary term {key!r} lists no pattern")
        if not any(str(entry.get("src", "")).startswith(prefix) for prefix in ALLOWED_SOURCES):
            raise VisualError(f"glossary term {key!r} has no primary-source URL")


def dfn_fills(glossary):
    """`{{dfn_<key>}}`: the term as a <dfn>, with a keyboard-reachable disclosure for its definition.

    The definition is in the page, not in a `title`: the term is an inline
    control (`role="button"`, in the tab order) that toggles it by tap, Enter or
    Space, and Esc closes it. A <button> would let a line break open beside the
    term and strand the punctuation after it.
    """
    out = {}
    for entry in glossary["terms"]:
        key = entry["key"]
        out[f"dfn_{key}"] = (
            f'<dfn id="term-{key}" data-term="{key}"><span class="term" role="button" tabindex="0" aria-expanded="false" '
            f'aria-controls="def-{key}">{html.escape(entry["text"])}</span></dfn>'
            f'<span class="def" id="def-{key}" role="note" hidden> <b>{html.escape(entry["term"])}:</b> '
            f'{html.escape(entry["definition"])} <a href="{entry["src"]}">Source</a></span><!--/def-->')
    return out


def newcomer_nav(template):
    """The "Start here" nav: the views the template carries, in reading order."""
    items = "".join(
        f'<li class="live"><b>N{i}</b><span><a href="#{sid}">{title}</a><small>{sub}</small></span></li>'
        for i, (sid, title, sub) in enumerate(NEWCOMER_VIEWS, 1) if f'<section id="{sid}"' in template)
    return f"<ol>{items}</ol>"


# ---------------------------------------------------------------- held-out days


def held_out_tiers(repo):
    """The lockbox tiers not yet opened, from `metadata/lockbox.json`; no date is typed here."""
    return [tier for tier in lockbox.load_lockbox(Path(repo) / LOCKBOX) if tier.opened is None]


def is_held(iso, tiers):
    d = date.fromisoformat(iso)
    return any(tier.opened is None and tier.contains(d) for tier in tiers)


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


# ---------------------------------------------------------------- the newcomer layer (#141)


def cluster_years(by_year):
    """The fewest years that hold more than half of the days, listed in date order.

    Years are taken by count, most first (the earlier year on a tie), until
    together they hold more than half; the rule reads only the counts.
    """
    total = sum(by_year.values())
    if not total:
        return []
    picked, held = [], 0
    for year, k in sorted(by_year.items(), key=lambda kv: (-kv[1], kv[0])):
        picked.append(year)
        held += k
        if 2 * held > total:
            break
    return sorted(picked)


def year_list(years):
    years = [str(y) for y in years]
    return years[0] if len(years) == 1 else ", ".join(years[:-1]) + " and " + years[-1]


def newcomer_n1(rows, tiers, thresholds, notes):
    """N1 "What is pressure?": what the page says about SOFR − IORB, from unlocked days only.

    The chart draws every panel day from the history series; days in a lockbox
    tier not yet opened are drawn grey and labelled "held out". Every count,
    share and sentence here is computed from `counted`, which leaves them out,
    so a locked day's value cannot move anything this view writes.
    """
    pressure_bp = int(thresholds["taus_bp"][0])
    held = lambda iso: is_held(iso, tiers)
    counted = [r for r in rows if not held(r["date"])]
    if not counted:
        raise VisualError("every panel day is held out; N1 has nothing to count")
    for r in counted:
        r["n1_s"] = int((Decimal(r["sofr"]) - Decimal(r["iorb"])) * 100)
    hot = [r for r in counted if r["n1_s"] > pressure_bp]
    by_year = {}
    for r in hot:
        by_year[int(r["date"][:4])] = by_year.get(int(r["date"][:4]), 0) + 1
    at_or_below = sum(1 for r in counted if r["n1_s"] <= 0)
    off = [r for r in counted if r["n1_s"] > CLIP_BP]
    spike = max(counted, key=lambda r: r["n1_s"])
    iorb_from = next(e["date"] for e in notes["events"] if e.get("role") == "iorb_from")
    by_date = {e["date"]: e for e in notes["events"]}
    missing = [d for d in N1_EPISODES if d not in by_date]
    if missing:
        raise VisualError(f"N1 marks events {missing} that annotations.json does not carry")
    episodes = [{"date": d, "src": by_date[d]["src"],
                 "text": by_date[d]["text"].format(spike_sofr=f"{float(spike['sofr']):.2f}%",
                                                   spike_bp=spike["n1_s"])}
                for d in N1_EPISODES if not held(d)]
    last = rows[-1]["date"]
    spans = [{"name": t.name, "start": t.start.isoformat(),
              "end": min(last, t.end.isoformat()) if t.end else last}
             for t in tiers if t.start.isoformat() <= last]
    clusters = cluster_years(by_year)
    rest = sorted(set(by_year) - set(clusters))
    data = {
        "held_out": spans, "pressure_bp": pressure_bp, "clip_bp": CLIP_BP, "iorb_from": iorb_from,
        "episodes": episodes,
        "counted": {"first": counted[0]["date"], "last": counted[-1]["date"], "n": len(counted),
                    "pressure": len(hot), "at_or_below_zero": at_or_below, "off_scale": len(off),
                    "by_year": {str(y): k for y, k in sorted(by_year.items())},
                    "cluster_years": clusters},
    }
    fills = {
        "n1_first": day(counted[0]["date"]), "n1_last": day(counted[-1]["date"]),
        "n1_pressure_of": f"{len(hot):,} of the {len(counted):,}",
        "n1_clusters": (f"Most of those days came in {year_list(clusters)}" if clusters else "There were none")
                       + (f"; the rest in {year_list(rest)}." if rest else "."),
        "n1_at_or_below": f"{at_or_below:,} of the {len(counted):,} days counted here "
                          f"({round(100 * at_or_below / len(counted))}%)",
        "n1_off_scale": days(len(off)),
        "n1_spike": f"{bp(spike['n1_s'])} bp on {day(spike['date'])}",
        "n1_src_triparty": notes["claims"]["triparty_actors"]["src"],
        "n1_held_note": (f"Days from {day(spans[0]['start'])} on are held out for the project's final test "
                         f"(<a href='https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/"
                         f"decisions/lockbox.md'>the lockbox rule</a>). They are drawn in grey, labelled "
                         f"&ldquo;held out&rdquo;, and left out of every count and sentence in this view."
                         if spans else "No day on this chart is held out."),
        "n1_iorb_from": day(iorb_from),
        "n1_episode_list": "".join(
            f"<li><time>{short_day(e['date'])}</time> {e['text']}. <a href='{e['src']}'>Source</a></li>"
            for e in episodes),
    }
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
    glossary = read_json(GLOSSARY, repo)
    check_annotations(notes)
    check_glossary(glossary)
    tiers = held_out_tiers(repo)
    for path in MODEL_RECORDS:
        load_run_record(repo / path)
    commit = commit or input_commit(repo)

    with tempfile.TemporaryDirectory() as tmp:
        raw, digest = build_panel(repo, manifest, tmp)
    rows = list(csv.DictReader(raw.decode().splitlines()))
    check_reserve_units(rows)
    decision = time.fromisoformat(manifest["decision_time"])

    n1, n1_fills = newcomer_n1([dict(r) for r in rows], tiers, thresholds, notes)
    hist, fills = history(rows, notes, thresholds, regimes, windows)
    fills.update(n1_fills)
    fills.update(dfn_fills(glossary))
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
    })

    inputs = {rel: sha256(repo / rel) for rel in
              (MANIFEST, SOURCES, EVENTS, THRESHOLDS, SPLITS, ANNOTATIONS, GLOSSARY, LOCKBOX, TEMPLATE,
               notes["implementation_note"]["path"])}
    provenance = {
        "commit": commit,
        "generator": "scripts/emit_visual.py",
        "panel": {"sha256": digest, "rows": len(rows), "first": rows[0]["date"], "last": last["date"],
                  "built_from": FIXTURES, "manifest": MANIFEST},
        "inputs": inputs,
    }
    build = {"process": notes["process"], "guards": notes["guards"], "validation": notes["validation"]}
    clock_data = {"decision_time": decision.strftime("%H:%M"), "inputs": clock_rows}
    payloads = {"history": hist, "plumbing": plumbing, "clock": clock_data, "build": build, "newcomer_n1": n1}
    out = {}
    for name, payload in payloads.items():
        doc = {"provenance": provenance, "data": payload}
        out[f"{DATA_DIR}/{name}.json"] = (json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                                      ensure_ascii=False) + "\n").encode("utf-8")
    page_data = {k: payloads[k] for k in ("history", "plumbing", "clock", "newcomer_n1")}
    template = (repo / TEMPLATE).read_text(encoding="utf-8")
    fills["newcomer_nav"] = newcomer_nav(template)
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
