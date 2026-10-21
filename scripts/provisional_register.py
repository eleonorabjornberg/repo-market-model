#!/usr/bin/env python3
"""The provisional register (#1028): which merged results come from a model that does not read calendar days at the target day.

Each row of the register is its own file under `metadata/provisional/` (`ENTRIES`), one folder per table:

* `producers/<script stem>.json`: a script that calls one of the two gradient-boosted quantile fitters of `src/repo_model/ml.py`
  (`FITTER` names them), whose default training pairs are one-step (`training_pairs` unset), with the model, its calendar or
  scheduled inputs and its class;
* `results/pr_<pull request>.json`: a merged result whose figures come from such a model, with the log entries and page figures
  to mark, and its re-run order key (`order`: any number; the table numbers the rows 1, 2, ... in the order of the keys, so a
  new result takes a free key between two others and renumbers no other file);
* `cleared/<declaration stem>.json`: a declaration that names a calendar or scheduled column and is read at the target day (or
  is no model).

A directive that adds a producer adds its own file; nobody edits a shared table. The three tables of
`docs/research/provisional-calendar-register.md` (`REGISTER`) are generated from the files, each between
`<!-- generated: register:<table> -->` and `<!-- end generated: register:<table> -->`; the prose around them is hand-written.

    python3 scripts/provisional_register.py            # rewrite the page's three tables from the files
    python3 scripts/provisional_register.py --check    # exit 1 when the page is not what the files generate

Class `a`: the model has no calendar day-type input. Class `b`: a calendar or scheduled column is trained one day off (the #914
class: a one-step pair learns the column from row p for the spread of row p + 1, and serving reads it from the target's own row,
rule 2 of `src/repo_model/asof.py`). `a+b`: both. `series`: the result reads the series of such a model as data (its conclusion
is about a test, not the model).

Read by `scripts/research_view.py` (the mark on the results page) and `tests/test_provisional_register.py` (completeness against
the tree). Standard library only. Nothing here edits a result: a registered result stays as it was published. The entry files
sit in a folder of their own, so the `metadata/*.json` scans of the declarations (here, `tests/test_model_declarations.py`) do
not read them, and no checksummed declaration is touched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REGISTER = "docs/research/provisional-calendar-register.md"
ENTRIES = "metadata/provisional"
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
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from repo_model.contract import TARGET_DAY_COLUMNS  # noqa: E402

#: Every column written about the target day (#1070): the shared declaration, `contract.TARGET_DAY_COLUMNS` (calendar and
#: FOMC columns), with the scheduled fields above. The scan of the declarations reads this.
CALENDAR_COLUMNS = tuple(dict.fromkeys(CALENDAR_COLUMNS + tuple(sorted(TARGET_DAY_COLUMNS))))
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

#: Each table's columns, lower-cased, as `load` keys its rows.
TABLES = {
    "producers": ("script", "declaration", "model", "calendar or scheduled inputs", "pairing", "class"),
    "results": ("order", "directive", "pull request", "hypothesis", "result", "declaration", "model", "pairing", "class",
                "on the page", "what it concluded"),
    "cleared": ("declaration", "script", "pairing", "why"),
}
#: The fields of an entry file, by table. Paths are plain; the other text fields are Markdown, shown as written.
FIELDS = {
    "producers": ("script", "declarations", "model", "calendar_inputs", "pairing", "class"),
    "results": ("order", "directive", "pull_request", "hypothesis", "result", "declarations", "model", "pairing", "class",
                "on_the_page", "concluded"),
    "cleared": ("declaration", "script", "pairing", "why"),
}
PAIRINGS = {"producers": PRODUCER_PAIRINGS, "results": RESULT_PAIRINGS, "cleared": CLEARED_PAIRINGS}


class RegisterError(ValueError):
    """An entry file or the register page is malformed; the results page is not built."""


def begin(name):
    return f"<!-- generated: register:{name} -->"


def end(name):
    return f"<!-- end generated: register:{name} -->"


def entry_path(kind, entry):
    """The path, under the repository, an entry file must have: its table's folder and its key."""
    if kind == "producers":
        name = Path(entry["script"]).stem
    elif kind == "results":
        name = f"pr_{entry['pull_request']}"
    else:
        name = Path(entry["declaration"]).stem
    return f"{ENTRIES}/{kind}/{name}.json"


def _check(kind, entry, where):
    fields = set(FIELDS[kind])
    if set(entry) != fields:
        raise RegisterError(f"{where}: fields {sorted(set(entry))}, not {sorted(fields)} "
                            f"(missing {sorted(fields - set(entry))}, unknown {sorted(set(entry) - fields)})")
    for field in fields:
        value = entry[field]
        if field in ("declarations", "on_the_page"):
            ok = isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value)
        elif field in ("directive", "pull_request"):
            ok = isinstance(value, int) and not isinstance(value, bool) and value > 0
        elif field == "order":
            ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        elif field == "script" and kind == "cleared":
            ok = value is None or (isinstance(value, str) and value.strip())
        else:
            ok = isinstance(value, str) and value.strip()
        if not ok:
            raise RegisterError(f"{where}: field {field!r} is {value!r}")
    if "class" in entry and entry["class"] not in CLASSES:
        raise RegisterError(f"{where}: class {entry['class']!r} is not one of {CLASSES}")
    if entry["pairing"] not in PAIRINGS[kind]:
        raise RegisterError(f"{where}: pairing {entry['pairing']!r} is not one of {PAIRINGS[kind]}")
    if entry_path(kind, entry) != where:
        raise RegisterError(f"{where}: this entry's file is {entry_path(kind, entry)}")


def entries(repo):
    """`{"producers": [...], "results": [...], "cleared": [...]}`: the entry files, in table order, each with its `_file`."""
    out = {}
    for kind in TABLES:
        rows = []
        for path in sorted((Path(repo) / ENTRIES / kind).glob("*.json")):
            where = f"{ENTRIES}/{kind}/{path.name}"
            try:
                entry = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                raise RegisterError(f"{where}: {error}") from error
            if not isinstance(entry, dict):
                raise RegisterError(f"{where}: not a JSON object")
            _check(kind, entry, where)
            rows.append(dict(entry, _file=where))
        if kind == "results":
            orders = [row["order"] for row in rows]
            if len(set(orders)) != len(orders):
                raise RegisterError(f"{ENTRIES}/results: two files share an order key")
            rows.sort(key=lambda row: row["order"])
        elif kind == "producers":
            rows.sort(key=lambda row: row["script"])
        else:
            rows.sort(key=lambda row: row["declaration"])
        out[kind] = rows
    return out


def _paths(values):
    return ", ".join(f"`{value}`" for value in values) or "none"


def _cells(kind, entry, number):
    """The Markdown cells of one row."""
    if kind == "producers":
        return [f"`{entry['script']}`", _paths(entry["declarations"]), entry["model"], entry["calendar_inputs"],
                entry["pairing"], entry["class"]]
    if kind == "results":
        return [str(number), f"#{entry['directive']}", f"#{entry['pull_request']}", entry["hypothesis"], entry["result"],
                _paths(entry["declarations"]), entry["model"], entry["pairing"], entry["class"],
                ", ".join(entry["on_the_page"]) or "none", entry["concluded"]]
    return [f"`{entry['declaration']}`", f"`{entry['script']}`" if entry["script"] else "none", entry["pairing"], entry["why"]]


def _rows(repo):
    return {kind: [_cells(kind, entry, number) for number, entry in enumerate(rows, 1)]
            for kind, rows in entries(repo).items()}


def render(repo):
    """`{table: block}`: each table's generated block, markers included."""
    out = {}
    for kind, rows in _rows(repo).items():
        header = [column[0].upper() + column[1:] for column in TABLES[kind]]
        lines = [begin(kind),
                 f"<!-- Generated by scripts/provisional_register.py from {ENTRIES}/{kind}/. Do not edit by hand: add or "
                 f"change a file there and run `python3 scripts/provisional_register.py`. -->",
                 "| " + " | ".join(header) + " |",
                 "|" + "---|" * len(header)]
        lines += ["| " + " | ".join(row) + " |" for row in rows]
        lines.append(end(kind))
        out[kind] = "\n".join(lines)
    return out


def _span(text, name):
    if text.count(begin(name)) != 1 or text.count(end(name)) != 1:
        raise RegisterError(f"{REGISTER} must carry {begin(name)} and {end(name)} exactly once")
    start = text.index(begin(name))
    stop = text.index(end(name)) + len(end(name))
    if stop < start:
        raise RegisterError(f"{REGISTER}: {end(name)} comes before {begin(name)}")
    return start, stop


def stale(repo):
    """The tables whose block on the page is not what the entry files generate."""
    text = (Path(repo) / REGISTER).read_text(encoding="utf-8")
    out = []
    for kind, block in render(repo).items():
        start, stop = _span(text, kind)
        if text[start:stop] != block:
            out.append(kind)
    return out


def write(repo):
    """Rewrite the page's three blocks from the entry files; the prose is left as it is."""
    path = Path(repo) / REGISTER
    text = path.read_text(encoding="utf-8")
    for kind, block in render(repo).items():
        start, stop = _span(text, kind)
        text = text[:start] + block + text[stop:]
    path.write_text(text, encoding="utf-8")


def cells(line):
    return [cell.strip().replace("`", "") for cell in line.strip().strip("|").split("|")]


def _row(kind, values):
    return dict(zip(TABLES[kind], values))


def load(repo):
    """`{"producers": [...], "results": [...], "cleared": [...]}`: each table's rows as the page shows them, keyed by the
    lower-cased column names, with the code marks dropped. Read from the entry files, not the page."""
    return {kind: [_row(kind, [cell.strip().replace("`", "") for cell in row]) for row in rows]
            for kind, rows in _rows(repo).items()}


def parse_page(text):
    """The same tables, read back from the page's generated blocks (the test that the page says what the files say)."""
    out = {}
    for kind in TABLES:
        start, stop = _span(text, kind)
        lines = [line for line in text[start:stop].splitlines() if line.lstrip().startswith("|")]
        out[kind] = [_row(kind, cells(line)) for line in lines[2:]]
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--check", action="store_true", help="exit 1 when the page is not what the entry files generate")
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parent.parent
    try:
        if args.check:
            tables = stale(repo)
            if tables:
                print(f"{REGISTER}: the {', '.join(tables)} table(s) are not what {ENTRIES}/ generates; run "
                      f"`python3 scripts/provisional_register.py` and commit the page", file=sys.stderr)
                return 1
            print(f"{REGISTER} is current")
            return 0
        write(repo)
    except RegisterError as error:
        print(error, file=sys.stderr)
        return 1
    print(f"wrote {REGISTER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
