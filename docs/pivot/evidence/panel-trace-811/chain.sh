#!/bin/bash
# The scratch-panel chain used to trace #811 (docs/pivot/panel-trace-811-result.md): a git worktree of the tree to test, an output directory, an optional --end.
# usage: chain.sh TREE OUTDIR [END]    (prints the sha256 of PUB.csv and DERIV.csv)
# usage: chain.sh TREE OUTDIR [END]
set -e
T=$1; O=$2; END=$3; mkdir -p $O; cd $T
export PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1
E=""; [ -n "$END" ] && E="--end $END"
python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output $O/PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00 >$O/build.log 2>&1
python3 scripts/pressure_v1_1.py panel --output $O/AUG.csv $E
python3 scripts/measurement_fields.py panel --panel $O/AUG.csv --output $O/AUG2.csv
python3 scripts/satiation_distance_598.py panel --panel $O/AUG2.csv --output $O/AUG2D.csv $E
python3 scripts/net_settlement.py panel --panel $O/AUG2D.csv --output $O/AUG3.csv
python3 scripts/policy_features.py panel --panel $O/AUG3.csv --output $O/AUG4.csv
python3 scripts/fed_liquidity.py panel --panel $O/AUG4.csv --output $O/AUG5.csv
python3 scripts/nowcast.py panel --panel $O/AUG5.csv --output $O/AUG6.csv --summary $O/nowcast_panel.json $E
python3 scripts/dvp_segment_inputs.py panel --panel $O/PUB.csv --output $O/DVP.csv
python3 scripts/early_warning_inputs.py panel --panel $O/PUB.csv --output $O/EW.csv
python3 scripts/source_screen.py panel --panel $O/AUG6.csv --extra $O/DVP.csv $O/EW.csv --output $O/SCREEN.csv
python3 scripts/derived_features_631.py panel --panel $O/SCREEN.csv --output $O/DERIV.csv
sha256sum $O/PUB.csv $O/DERIV.csv
