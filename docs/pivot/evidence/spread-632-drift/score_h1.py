"""Score rebuilt #632 variants at h = 1 on the ordinary days (development data, not a verdict). Args: label=path ..."""
import importlib.util, json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, "scripts")
import repo_model.pressure_judge as pj
spec = importlib.util.spec_from_file_location("sd", "scripts/spread_distribution_632.py"); sd = importlib.util.module_from_spec(spec); spec.loader.exec_module(sd)
S = Path(sys.argv[1]); H = 1
base = pj.load_declaration(); tau = base.primary
rows = sd.load_daily_panel(S / "PUBLISHED.csv")
judge = sd._load("pressure_judge")
bench = json.loads((S / "o/bench_h1.json").read_text())
cols = {n: c[f"{tau:g}"] for n, c in bench["forecasts"].items()}
runs = {}
for a in sys.argv[2:]:
    label, path = a.split("=")
    for n, c in json.loads(Path(path).read_text())["forecasts"].items():
        cols[f"{n} [{label}]"] = c[f"{tau:g}"]
days = sorted(date.fromisoformat(d) for d in cols[base.climatology])
grid = pj.build_grid(base, H, rows, days, sd.load_split_declaration(sd.SPLITS), scarcity_state=judge._scarcity_states(H, base.last_day))
keep = [i for i, l in enumerate(grid.groups["day_type"]) if l == "ordinary"]
y = [grid.outcomes[tau][i] for i in keep]
print(f"ordinary days {len(keep)}, above +5 bp {sum(y)}")
prev = {}
for n, c in cols.items():
    p = [c[days[i].isoformat()] for i in keep]
    rel = sd.reliability(p, y)
    key = n.split(" [")[0]
    mx = "" if key not in prev else f"{max(abs(a-b) for a,b in zip(p, prev[key])):.4f}"
    if " [" in n: prev.setdefault(key, p)
    print(f"{n:75s} AUROC {sd.auroc(p,y):.4f} slope {rel[0]:.3f} intercept {rel[1]:.3f} maxdiff_vs_first {mx}")
