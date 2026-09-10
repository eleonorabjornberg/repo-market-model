#!/usr/bin/env python3
"""Cut the tracked FR 2004 extract out of the untracked history export.

The New York Fed's primary-dealer history export (1998-01-28 onward, every
series, ~26 MB) sits gitignored under `data/raw/fr2004/`. What the model reads
from it is one column, `dealer_treasury_position` = `PDPOSGST-TOT`, and the
components that total is checked against. Those are tracked, and only those
(human decision, 10 Sep): too large to commit whole, too important to leave
where no clone and no test can see it.

Lines are copied byte for byte from the export, header included, so an
adapter parses the extract exactly as it would parse the export. Kept:
`PDPOSGST-TOT`, and every `PDPOSGS-*`, `PDPOSGSC-*` and `PDPOSTIPS-*` series
whose name does not end in `C`. The `C`-suffixed siblings are not in the total
(docs/DATA_QUALITY_DECISIONS.md, "Dealer Treasury positions"); a glob that
admits them overshoots it.

A sidecar `<extract>.manifest.json` records the export's digest and size, the
extract's own digest, and per series the first and last as-of date. The
export carries no retrieval manifest of its own, so no retrieval time is
claimed here.

Before writing, the script checks the identity the extract exists to carry:
on every as-of date with a total, the total equals the sum of the components
present that date, and it refuses if any date disagrees by 0.5 (the unit is
millions, and the export is integral). `--check` runs that check and compares
the committed extract with a fresh cut, writing nothing.

    python3 scripts/extract_fr2004.py
    python3 scripts/extract_fr2004.py --check
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "data/raw/fr2004/fr2004_pd_positions_historical.csv"
EXTRACT = ROOT / "tests/fixtures/snapshots/fr2004/pdposgst_tot_and_components.csv"
SIDECAR = EXTRACT.with_name(EXTRACT.name + ".manifest.json")
TOTAL = "PDPOSGST-TOT"
PREFIXES = ("PDPOSGS-", "PDPOSGSC-", "PDPOSTIPS-")


def kept(series):
    return series == TOTAL or (series.startswith(PREFIXES) and not series.endswith("C"))


def cut(raw):
    lines = raw.splitlines(keepends=True)
    out = [lines[0]]
    for line in lines[1:]:
        row = next(csv.reader([line]))
        if kept(row[1]):
            out.append(line)
    return "".join(out)


def check_identity(text):
    by_date = {}
    for as_of, series, value in list(csv.reader(io.StringIO(text)))[1:]:
        by_date.setdefault(as_of, {})[series] = value
    eras = {}
    for as_of, values in sorted(by_date.items()):
        if TOTAL not in values:
            continue
        parts = sorted(name for name in values if name != TOTAL)
        numbers = [values[name] for name in [TOTAL] + parts]
        if any(not number.strip().lstrip("-").isdigit() for number in numbers):
            raise SystemExit(f"refusing: {as_of} carries a non-integral or suppressed value")
        total = int(values[TOTAL])
        summed = sum(int(values[name]) for name in parts)
        if abs(total - summed) >= 0.5:
            raise SystemExit(f"refusing: {as_of} total {total} != components {summed}")
        era = eras.setdefault(tuple(parts), [as_of, as_of])
        era[1] = as_of
    return [
        {"first": first, "last": last, "components": list(parts)}
        for parts, (first, last) in sorted(eras.items(), key=lambda item: item[1][0])
    ]


def manifest(raw_bytes, text):
    spans = {}
    for as_of, series, _value in list(csv.reader(io.StringIO(text)))[1:]:
        span = spans.setdefault(series, [as_of, as_of])
        span[0], span[1] = min(span[0], as_of), max(span[1], as_of)
    return {
        "source": EXPORT.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "source_byte_count": len(raw_bytes),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "series": {name: {"first": a, "last": b} for name, (a, b) in sorted(spans.items())},
        "identity_eras": check_identity(text),
        "generator": "scripts/extract_fr2004.py",
    }


def main(argv):
    raw_bytes = EXPORT.read_bytes()
    text = cut(raw_bytes.decode("utf-8"))
    record = json.dumps(manifest(raw_bytes, text), indent=2, sort_keys=True) + "\n"
    if "--check" in argv:
        drift = [
            path.relative_to(ROOT).as_posix()
            for path, expected in ((EXTRACT, text), (SIDECAR, record))
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        if drift:
            print("differs from a fresh cut: " + ", ".join(drift), file=sys.stderr)
            return 1
        print("FR 2004 extract agrees with the export; identity exact in every era.")
        return 0
    EXTRACT.parent.mkdir(parents=True, exist_ok=True)
    EXTRACT.write_bytes(text.encode("utf-8"))
    SIDECAR.write_text(record, encoding="utf-8")
    print("wrote %s and %s" % (EXTRACT.relative_to(ROOT), SIDECAR.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
