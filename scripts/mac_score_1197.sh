#!/usr/bin/env bash
# The Mac run of #1197: (s3) against gbm_funding on her walks. Minutes. Run from a clone of the branch (the paste on the PR does).
# It reads ~/rmm-1027/WALKS read-only and never rebuilds a walk; it stops before anything else if the walks are missing.
# It commits only the result, the page and the research-log entry, and pushes. Log: ~/1197.log, ending in PUSHED.
set -euo pipefail
cd "$(dirname "$0")/.."
WALKS="${WALKS:-$HOME/rmm-1027/WALKS}"
WORK="${WORK:-$HOME/rmm-1197-work}"

if [ -d "$WALKS" ]; then echo "WALKS: present ($WALKS)"; else echo "STOP: $WALKS is MISSING; this run never rebuilds the walks."; exit 1; fi
# shellcheck disable=SC1091
source ~/rmm-venv/bin/activate   # Python 3.11.17, numpy and scikit-learn at the versions CI's ml job pins
python -c "import sys, numpy, sklearn; print(sys.version, numpy.__version__, sklearn.__version__)"
export PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1

python scripts/s3_vs_gbm_1197.py check-walks "$WALKS"
mkdir -p "$WORK"
python -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output "$WORK/PUB.csv" \
    --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
python -m repo_model.cli verify-panel "$WORK/PUB.csv" --manifest metadata/funding_panel_manifest.json

DAY="$(TZ=America/New_York date +%F)"
RESULT=docs/research/s3-vs-gbm-1197/result.json
PAGE=docs/research/s3-vs-gbm-1197-result.md
LOG="docs/research/log/${DAY}-model-01197-H5-step3.md"
python scripts/s3_vs_gbm_1197.py score --panel "$WORK/PUB.csv" --walks "$WALKS" --output "$RESULT" --workers 4
python scripts/s3_vs_gbm_1197.py page --score "$RESULT" --output "$PAGE"
python scripts/s3_vs_gbm_1197.py log --score "$RESULT" --output "$LOG" --date "$DAY"
python scripts/check_research_log.py check-block "$LOG"

# nothing but the three outputs may have changed
others="$(git status --porcelain --untracked-files=all | grep -v -e " $RESULT\$" -e " $PAGE\$" -e " $LOG\$" || true)"
if [ -n "$others" ]; then echo "STOP: files other than the result, page and log entry changed:"; echo "$others"; exit 1; fi

git add "$RESULT" "$PAGE" "$LOG"
git commit -m "#1197: Mac run, (s3) against gbm_funding"
git push origin HEAD
echo PUSHED
