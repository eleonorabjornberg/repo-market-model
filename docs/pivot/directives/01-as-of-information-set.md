# Directive: the as-of information set

Implements `docs/decisions/information-set.md`. Work it as one pull request.

Repo `eleonorabjornberg/repo-market-model`, branch `asof/information-set` from `origin/main`. Read `docs/pivot/lag-assessment.md`
first. Implement: (1) per-field as-of reads using
`baseline._declared_availability` at the decision instant (16:00 on the panel day before T), replacing
`_feature_index` at every call site (baseline 3243/5315/6410, event_eval 594, ml 2933/3032, tail_diagnostics 347);
(2) a declared scheduled-input class read at T: the calendar, and Treasury settlements under a new `treasury_auctions`
availability declaration dated from the auction results time (approved 30 Sep). Verify that instant from Treasury's
published auction procedure, pick a conservative time, and record the evidence in the declaration's note; (3) training labels admissible only if observable at the fold's decision instant; one fold grid regardless of
declaration; (4) a staleness guard, red first, whose p−1 mutation must fail, with `_check_decision_relative_availability`
still passing on every fold; (5) `--refit-every N`, recorded in the declaration. Write tests before code. Do not
touch `docs/runs/` or the README in this PR. Acceptance: CI green with `REPO_MODEL_REQUIRE_ML=1`. Persistence under
the new rule gives MAE 2.509 ± 0.01 on the 2,039-day grid. gbm (4 features, none, refit 21) is within 2% of the
scouting 2.342. Report any mismatch rather than tuning to it.
