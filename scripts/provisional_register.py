#!/usr/bin/env python3
"""The provisional register (#1028): which merged results come from a model that does not read calendar days at the target day.

The register is `docs/research/provisional-calendar-register.md`, a hand-written page with three tables, each under a marker
comment (`<!-- register:producers -->`, `<!-- register:results -->`, `<!-- register:cleared -->`):

* producers: the scripts that call one of the two gradient-boosted quantile fitters of `src/repo_model/ml.py` (`FITTER` names
  them), whose default training pairs are one-step (`training_pairs` unset), with the model, its calendar or scheduled inputs
  and its class;
* results: one row per merged result whose figures come from such a model, with the log entries and page figures to mark;
* cleared: the declarations that name a calendar or scheduled column and are read at the target day (or are no model).

Class `a`: the model has no calendar day-type input. Class `b`: a calendar or scheduled column is trained one day off (the #914
class: a one-step pair learns the column from row p for the spread of row p + 1, and serving reads it from the target's own row,
rule 2 of `src/repo_model/asof.py`). `a+b`: both. `series`: the result reads the series of such a model as data (its conclusion
is about a test, not the model).

Read by `scripts/research_view.py` (the mark on the results page) and `tests/test_provisional_register.py` (completeness against
the tree). Standard library only. Nothing here edits a result: a registered result stays as it was published.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REGISTER = "docs/research/provisional-calendar-register.md"
#: The calendar and scheduled columns of rule 2 (`src/repo_model/asof.py`): served from the target row. A name matches as a
#: substring, so `treasury_settlement` also covers its `_bills` and `_coupons` parts.
CALENDAR_COLUMNS = (
    "treasury_settlement",
    "quarter_end",
    "tax_date",
    "days_to_month_end",
    "iorb_announced_change_bps",
    "iorb_days_to_announced_change",
)
#: The fitters whose default training pairs are one-step.
FITTER = re.compile(r"fit_(?:gradient_boosted|depth_limited)_quantiles")
CLASSES = ("a", "b", "a+b", "series")
RESULT_PAIRINGS = ("one_step",)
PRODUCER_PAIRINGS = ("one_step", "one_step+direct")
CLEARED_PAIRINGS = ("direct", "as_of_read", "none")
#: Library modules that name a fitter in order to refuse a one-step fit (#947), not to make one.
GUARDS = ("src/repo_model/one_step_guard.py",)
#: A word in a result row's "On the page" cell: the incumbent's figures at the top of the results page.
INCUMBENT = "incumbent"

TABLES = {
    "producers": ("script", "declaration", "model", "calendar or scheduled inputs", "pairing", "class"),
    "results": ("order", "directive", "pull request", "hypothesis", "result", "declaration", "model", "pairing", "class",
                "on the page", "what it concluded"),
    "cleared": ("declaration", "script", "pairing", "why"),
}


class RegisterError(ValueError):
    """The register page is malformed; the results page is not built."""


def cells(line):
    return [cell.strip().replace("`", "") for cell in line.strip().strip("|").split("|")]


def parse_table(lines, name):
    """The first Markdown table in `lines`: its rows as dicts keyed by the lower-cased header cells."""
    rows = [line for line in lines if line.lstrip().startswith("|")]
    if len(rows) < 3:
        raise RegisterError(f"{REGISTER}: the {name} table has no row")
    header = tuple(cell.lower() for cell in cells(rows[0]))
    if header != TABLES[name]:
        raise RegisterError(f"{REGISTER}: the {name} table's columns are {header}, not {TABLES[name]}")
    out = []
    for line in rows[2:]:
        values = cells(line)
        if len(values) != len(header):
            raise RegisterError(f"{REGISTER}: a {name} row has {len(values)} cells, not {len(header)}: {line[:80]}")
        out.append(dict(zip(header, values)))
    return out


def load(repo):
    """`{"producers": [...], "results": [...], "cleared": [...]}` from the register page."""
    text = (Path(repo) / REGISTER).read_text(encoding="utf-8")
    out = {}
    for name in TABLES:
        marker = f"<!-- register:{name} -->"
        if text.count(marker) != 1:
            raise RegisterError(f"{REGISTER} must carry {marker} exactly once")
        after = text.split(marker, 1)[1].splitlines()[1:]
        block = []
        for line in after:
            if line.lstrip().startswith("|"):
                block.append(line)
            elif block:
                break
        out[name] = parse_table(block, name)
    return out


def page_cells(row):
    """The log-entry stems (and `incumbent`) a result row's "On the page" cell names."""
    return [word.strip() for word in row["on the page"].split(",") if word.strip() and word.strip() != "none"]


def marked_entries(tables):
    """The stems of the log entry files whose figures are provisional."""
    return {stem for row in tables["results"] for stem in page_cells(row) if stem != INCUMBENT}


def marks_incumbent(tables):
    """True when the register registers the figures shown for the incumbent at the top of the results page."""
    return any(INCUMBENT in page_cells(row) for row in tables["results"])


def declarations_naming_a_calendar_column(repo):
    """`metadata/*.json` declarations whose text names a calendar or scheduled column."""
    found = []
    for path in sorted((Path(repo) / "metadata").glob("*.json")):
        text = path.read_text(encoding="utf-8")
        if any(column in text for column in CALENDAR_COLUMNS):
            json.loads(text)
            found.append(f"metadata/{path.name}")
    return found


def one_step_fitter_callers(repo):
    """Scripts and library modules that name a one-step-capable fitter, other than `ml.py` (which defines them) and `GUARDS`."""
    root = Path(repo)
    found = []
    for folder in ("scripts", "src/repo_model"):
        for path in sorted((root / folder).glob("*.py")):
            if path.name == "ml.py" or f"{folder}/{path.name}" in GUARDS:
                continue
            if FITTER.search(path.read_text(encoding="utf-8")):
                found.append(f"{folder}/{path.name}")
    return found
