#!/usr/bin/env bash
# #1169: the studentized-bound re-score of #1023 on Eleonora's Mac (needs-mac). Minutes if ~/rmm-1023-work/CELLS.json exists;
# otherwise the #634 walks and #844's cells are rebuilt first (hours; a finished walk is skipped on re-run).
# It commits docs/research/ordinary-day-p5-1023/{result.json,cells.json} and the page, and pushes the branch.
set -euo pipefail
BRANCH=directive/1169-studentized-column
[ -d ~/rmm-1169 ] || git clone -b "$BRANCH" https://github.com/eleonorabjornberg/repo-market-model ~/rmm-1169
cd ~/rmm-1169 && git fetch origin && git checkout "$BRANCH" && git merge --ff-only "origin/$BRANCH"
source ~/rmm-venv/bin/activate   # Python 3.11.17, numpy and scikit-learn at the versions CI's ml job pins
python -c "import sys, numpy, sklearn; print(sys.version, numpy.__version__, sklearn.__version__)"
W=~/rmm-1023-work; mkdir -p "$W/OUT"
export PYTHONPATH=src
{
if [ ! -f "$W/CELLS.json" ]; then
  python -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output "$W/PUBLISHED.csv" --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
  python scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output "$W/AUG.csv"
  python scripts/tax_date_market_days.py scripts/measurement_fields.py panel --panel "$W/AUG.csv" --output "$W/AUG2.csv"
  python scripts/tax_date_market_days.py scripts/satiation_distance_598.py panel --panel "$W/AUG2.csv" --output "$W/AUG2D.csv"
  for h in 1 2 3 4 5; do
    for v in gbm_funding c_two_part_new; do
      [ -f "$W/OUT/${v}_h$h.json" ] || python scripts/spread_distribution_634.py walk --variant "$v" --horizon "$h" --published "$W/PUBLISHED.csv" --panel "$W/AUG2D.csv" --output "$W/OUT/${v}_h$h.json"
    done
    [ -f "$W/OUT/exceed_h$h.json" ] || python scripts/spread_distribution_634.py exceedance --horizon "$h" --published "$W/PUBLISHED.csv" --output "$W/OUT/exceed_h$h.json"
  done
  python scripts/ordinary_day_p5_844.py cells --panel "$W/PUBLISHED.csv" --walks "$W/OUT" --output "$W/CELLS.json"
fi
python scripts/ordinary_day_p5_1023.py score --cells "$W/CELLS.json" --output docs/research/ordinary-day-p5-1023/result.json --workers 4
python scripts/ordinary_day_p5_1023.py page --result docs/research/ordinary-day-p5-1023/result.json --output docs/research/ordinary-day-p5-1023-result.md
} > ~/1169.log 2>&1
cp "$W/CELLS.json" docs/research/ordinary-day-p5-1023/cells.json
git add docs/research/ordinary-day-p5-1023 docs/research/ordinary-day-p5-1023-result.md
git commit -m "#1169: Mac re-score with the studentized bound" && git push origin HEAD
echo PUSHED
