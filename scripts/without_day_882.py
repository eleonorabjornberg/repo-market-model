"""H5 step 3 (#882, finding #798): the scored results that informed H5 steps 2 to 4, with and without decision day 2019-09-18.

A scratch measurement, not a record: it reads score files and writes Markdown and JSON to the paths it is given, and
nothing into `docs/runs/`. It scores nothing itself. Each source (#758's `h5_step4_758.py`, #761's `spread_mr_variants_761.py`,
#688's `near_threshold_688.py`) is run once as published and once with `score ... --without-day 2019-09-18`, which leaves that
one decision day out of every window and changes nothing else; this script lines the two score files up. Development data,
not a verdict (scoring protocol v1, #640). No day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

    python3 scripts/without_day_882.py compare --name NAME --tracked TRACKED.json --with WITH.json --without WITHOUT.json --output OUT.json
    python3 scripts/without_day_882.py report --comparison OUT1.json OUT2.json ... --output report.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

#: the key that names a record's headline figure, in the order a record is read.
HEADLINES = ("skill", "headroom", "mean_difference", "difference")
#: a tolerance on the reproduction: the sum order of the bootstrap moves the last digits of a float.
REPRODUCTION_TOLERANCE = 1e-9


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def records(doc, path: str = "") -> Iterator[Tuple[str, dict]]:
    """Every dict of `doc` that carries a headline figure, with its path."""

    if isinstance(doc, dict):
        if any(_is_number(doc.get(k)) for k in HEADLINES):
            yield path, doc
        for key, value in doc.items():
            yield from records(value, f"{path}/{key}")


def headline(record: Mapping) -> Tuple[str, float]:
    for key in HEADLINES:
        if _is_number(record.get(key)):
            return key, float(record[key])
    raise ValueError("a record without a headline figure")


def bounds(record: Mapping) -> Optional[Tuple[float, float]]:
    """The record's interval for its headline, whichever way the source stored it, or None."""

    for key, value in record.items():
        if "interval" in key and isinstance(value, list) and len(value) == 2 and all(_is_number(v) for v in value):
            return float(value[0]), float(value[1])
    lower = [v for k, v in record.items() if "lower" in k and "one_sided" in k and _is_number(v)]
    upper = [v for k, v in record.items() if "upper" in k and "one_sided" in k and _is_number(v)]
    if lower and upper:
        return float(lower[0]), float(upper[0])
    return None


def _sign(x: float) -> int:
    return (x > 0) - (x < 0)


def bound_sign_change(a: Optional[Tuple[float, float]], b: Optional[Tuple[float, float]]) -> bool:
    """True when either bound of the interval changes sign (zero is its own sign) between `a` and `b`."""

    if a is None or b is None:
        return False
    return any(_sign(x) != _sign(y) for x, y in zip(a, b))


def max_difference(a, b) -> float:
    """The largest absolute difference between the numbers of two documents of one shape.

    Raises:
        ValueError: the documents differ in shape (a key, a length or a type).
    """

    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            raise ValueError(f"keys differ: {sorted(set(a) ^ set(b))[:3]}")
        return max((max_difference(a[k], b[k]) for k in a), default=0.0)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError("lengths differ")
        return max((max_difference(x, y) for x, y in zip(a, b)), default=0.0)
    if _is_number(a) and _is_number(b):
        return abs(float(a) - float(b))
    if a != b:
        raise ValueError(f"values differ: {a!r} and {b!r}")
    return 0.0


def compare(name: str, tracked: Mapping, with_day: Mapping, without_day: Mapping) -> dict:
    """The reproduction of `tracked` by `with_day`, and every record of `with_day` beside its record without the day."""

    reproduction: dict
    try:
        reproduction = {"max_abs_difference": max_difference(tracked, with_day), "same_shape": True}
    except ValueError as error:
        reproduction = {"max_abs_difference": None, "same_shape": False, "note": str(error)}
    without = dict(records(without_day))
    rows = []
    for path, rec in records(with_day):
        if path not in without:
            continue
        key, value = headline(rec)
        _, value_without = headline(without[path])
        interval, interval_without = bounds(rec), bounds(without[path])
        rows.append({
            "path": path, "metric": key,
            "n": rec.get("n", rec.get("days")), "n_without": without[path].get("n", without[path].get("days")),
            "with": value, "without": value_without,
            "interval_with": interval, "interval_without": interval_without,
            "bound_sign_change": bound_sign_change(interval, interval_without),
        })
    return {"name": name, "reproduction": reproduction, "rows": rows}


def _fmt(x: Optional[float]) -> str:
    return "" if x is None else f"{x:+.3f}"


def _interval(x: Optional[Sequence[float]]) -> str:
    return "" if x is None else f"[{x[0]:+.3f}, {x[1]:+.3f}]"


def render(comparisons: Sequence[Mapping], headline_filter=lambda path: True) -> str:
    lines: List[str] = []
    for comp in comparisons:
        repro = comp["reproduction"]
        lines += [f"## {comp['name']}", ""]
        if repro["same_shape"]:
            lines.append(f"Reproduction of the tracked score file: largest absolute difference {repro['max_abs_difference']:.2e}.")
        else:
            lines.append(f"Reproduction of the tracked score file: the shape differs ({repro['note']}).")
        changed = [r for r in comp["rows"] if r["bound_sign_change"]]
        lines += ["", f"Records compared: {len(comp['rows'])}; records in which a bound of the interval changes sign: {len(changed)}.", ""]
        lines += ["| record | metric | days (without) | with | without | interval with | interval without | bound changes sign |",
                  "|---|---|---|---|---|---|---|---|"]
        for r in comp["rows"]:
            if headline_filter(r["path"]) or r["bound_sign_change"]:
                lines.append(
                    f"| `{r['path']}` | {r['metric']} | {r['n']} ({r['n_without']}) | {_fmt(r['with'])} | {_fmt(r['without'])} | "
                    f"{_interval(r['interval_with'])} | {_interval(r['interval_without'])} | {'yes' if r['bound_sign_change'] else ''} |"
                )
        lines.append("")
    return "\n".join(lines)


def compare_command(args) -> int:
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
    document = compare(args.name, load(args.tracked), load(args.with_), load(args.without))
    Path(args.output).write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"name": args.name, "records": len(document["rows"]), "reproduction": document["reproduction"]}))
    return 0


def report_command(args) -> int:
    comparisons = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.comparison]
    everything = "# With and without decision day 2019-09-18 (#882)\n\nDevelopment data, not a verdict.\n\n" + render(comparisons)
    Path(args.output).write_text(everything, encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--name", required=True)
    c.add_argument("--tracked", required=True)
    c.add_argument("--with", dest="with_", required=True)
    c.add_argument("--without", required=True)
    c.add_argument("--output", required=True)
    c.set_defaults(func=compare_command)
    r = sub.add_parser("report")
    r.add_argument("--comparison", nargs="+", required=True)
    r.add_argument("--output", required=True)
    r.set_defaults(func=report_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
