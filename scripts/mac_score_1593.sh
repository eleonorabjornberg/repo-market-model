#!/usr/bin/env bash
# The Mac run of #1593: the frozen candidate against gbm_funding_cal_direct on quarter-end turns and year-ends, from #1036's walks. No refit.
# Run from a clone of the branch (the paste on the PR does). It reads ~/rmm-1027/WALKS read-only and never rebuilds a walk; it stops before anything else if the
# walks, PUB.csv or AUG3.csv are missing. It commits only the result, the page and the research-log entry, and pushes. Log: ~/1593.log, ending in PUSHED.
set -euo pipefail
cd "$(dirname "$0")/.."
BASE="${BASE:-$HOME/rmm-1027}"
WALKS="${WALKS:-$BASE/WALKS}"
PUB="${PUB:-$BASE/PUB.csv}"
SCRATCH="${SCRATCH:-$BASE/AUG3.csv}"

for f in "$WALKS" "$PUB" "$SCRATCH"; do
  if [ -e "$f" ]; then echo "present: $f"; else echo "STOP: $f is MISSING; this run never rebuilds the walks or the panels."; exit 1; fi
done
# shellcheck disable=SC1091
source ~/rmm-venv/bin/activate   # Python 3.11.17, numpy and scikit-learn at the versions CI's ml job pins
python -c "import sys, numpy, sklearn; print(sys.version, numpy.__version__, sklearn.__version__)"
export PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1

python scripts/qe_vs_calendar_gbm_1593.py check-walks "$WALKS"
python -m repo_model.cli verify-panel "$PUB" --manifest metadata/funding_panel_manifest.json

DAY="$(TZ=America/New_York date +%F)"
RESULT=docs/research/qe-vs-calendar-gbm-1593/result.json
PAGE=docs/research/qe-vs-calendar-gbm-1593-result.md
LOG="docs/research/log/${DAY}-model-01593-H5-step3.md"
python scripts/qe_vs_calendar_gbm_1593.py score --published "$PUB" --panel "$SCRATCH" --walks "$WALKS" --output "$RESULT"
python scripts/qe_vs_calendar_gbm_1593.py page --score "$RESULT" --output "$PAGE"
python scripts/qe_vs_calendar_gbm_1593.py log --score "$RESULT" --output "$LOG" --date "$DAY"
python scripts/check_research_log.py check-block "$LOG"

# nothing but the three outputs may have changed
others="$(git status --porcelain --untracked-files=all | grep -v -e " $RESULT\$" -e " $PAGE\$" -e " $LOG\$" || true)"
if [ -n "$others" ]; then echo "STOP: files other than the result, page and log entry changed:"; echo "$others"; exit 1; fi

git add "$RESULT" "$PAGE" "$LOG"
git commit -m "#1593: Mac run, the candidate against the calendar-aware GBM on quarter-end turns and year-ends"
git push origin HEAD
echo PUSHED
