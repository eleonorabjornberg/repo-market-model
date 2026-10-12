"""Which scored days change state under the own-leg read (#586): counts per horizon, by year, and the risky set.

A scratch measurement: it writes the JSON it is given. Scored days are 2018-06-29 to 2025-12-31.

    PYTHONPATH=src python3 scripts/own_leg_days.py --output OUT/days.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    from repo_model import pressure_judge as pj

    spec = importlib.util.spec_from_file_location("pressure_judge_script", REPO / "scripts" / "pressure_judge.py")
    script = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = script
    spec.loader.exec_module(script)
    declaration = pj.load_declaration()
    out = {"horizons": {}}
    for h in declaration.horizons:
        new = script._scarcity_states(h, declaration.last_day)
        old = script._same_row_scarcity_states(h, declaration.last_day)
        if new.keys() != old.keys():
            raise SystemExit("the two reads score different days")
        changed = sorted(d for d in new if new[d] != old[d])
        entered = [d for d in changed if (new[d] or 0) >= 2 > (old[d] or 0)]
        left = [d for d in changed if (old[d] or 0) >= 2 > (new[d] or 0)]
        out["horizons"][str(h)] = {
            "days": len(new),
            "changed": len(changed),
            "up": sum((new[d] or 0) > (old[d] or 0) for d in changed),
            "down": sum((new[d] or 0) < (old[d] or 0) for d in changed),
            "by_year": dict(sorted(Counter(str(d.year) for d in changed).items())),
            "enter_risky_set": len(entered),
            "leave_risky_set": len(left),
            "risky_set_days_before": sum((v or 0) >= 2 for v in old.values()),
            "risky_set_days_after": sum((v or 0) >= 2 for v in new.values()),
            "state_counts_before": dict(sorted(Counter(str(v) for v in old.values()).items())),
            "state_counts_after": dict(sorted(Counter(str(v) for v in new.values()).items())),
        }
        if h == 1:
            out["h1_changed_days"] = [[d.isoformat(), old[d], new[d]] for d in changed]
        print(json.dumps({"horizon": h, "changed": len(changed)}), flush=True)
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
