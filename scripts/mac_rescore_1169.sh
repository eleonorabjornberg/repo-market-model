#!/usr/bin/env bash
# #1169: the studentized-bound re-score of #1023 on Eleonora's Mac (needs-mac). Minutes. It re-scores from ~/rmm-1023-work/CELLS.json
# and, if that file is missing, stops: rebuilding the #634 walks elsewhere does not reproduce the cells #1023 was scored on.
# It refuses to commit unless every existing value of result.json is unchanged (only `studentized` entries may be new),
# then commits result.json, cells.json and the page, and pushes the branch.
set -euo pipefail
BRANCH=directive/1169-studentized-column
[ -d ~/rmm-1169 ] || git clone -b "$BRANCH" https://github.com/eleonorabjornberg/repo-market-model ~/rmm-1169
cd ~/rmm-1169 && git fetch origin && git checkout "$BRANCH" && git merge --ff-only "origin/$BRANCH"
source ~/rmm-venv/bin/activate   # Python 3.11.17, numpy and scikit-learn at the versions CI's ml job pins
python -c "import sys, numpy, sklearn; print(sys.version, numpy.__version__, sklearn.__version__)"
W=~/rmm-1023-work
if [ ! -f "$W/CELLS.json" ]; then echo "STOP: $W/CELLS.json does not exist; the re-score needs the cells #1023 was scored on. Nothing was run." >&2; exit 1; fi
export PYTHONPATH=src
R=docs/research/ordinary-day-p5-1023/result.json
OLD=$(mktemp); git show "HEAD:$R" > "$OLD"
{
python scripts/ordinary_day_p5_1023.py score --cells "$W/CELLS.json" --output "$R" --workers 4
# the guard: no existing value may move; on any difference exit non-zero, commit nothing, and put the committed file back
python scripts/check_rescore_unchanged_1169.py --old "$OLD" --new "$R" || { git checkout -- "$R"; echo "GUARD FAILED: nothing committed" >&2; exit 1; }
python scripts/ordinary_day_p5_1023.py page --result "$R" --output docs/research/ordinary-day-p5-1023-result.md
} >> ~/1169.log 2>&1
cp "$W/CELLS.json" docs/research/ordinary-day-p5-1023/cells.json
git add docs/research/ordinary-day-p5-1023 docs/research/ordinary-day-p5-1023-result.md
git commit -m "#1169: Mac re-score with the studentized bound" && git push origin HEAD
echo PUSHED
