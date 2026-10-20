---
name: register-producer
description: Record a script that fits through a guarded fitter in the provisional calendar register of repo-market-model. Use when a change adds or changes a call to ml.fit_gradient_boosted_quantiles or ml.fit_depth_limited_quantiles, or tests/test_provisional_register.py fails with a new producer.
---

# Register a producer

`docs/research/provisional-calendar-register.md` lists every result from a model that did not read calendar days at
the target day, or learned them one row off (#1028, calendar first). `tests/test_provisional_register.py` fails when a
script calls a guarded fitter and has no row.

1. **Classify the producer:**
   - `a`: no calendar day-type input at the target day;
   - `b`: a calendar or scheduled column trained one day off, a one-step fit (`training_pairs` unset);
   - `a+b`: both;
   - not in the class: it fits on direct pairs (`training_pairs="direct"`) and reads the calendar columns. It goes in the
     "not in the class" table with the reason.
2. **Add its row.** If `metadata/provisional/` exists (PR #1049), add one file for the producer under
   `metadata/provisional/producers/<script stem>.json` and run `python3 scripts/provisional_register.py` to regenerate
   the page's tables; never edit the generated tables by hand. Otherwise edit the producers table of the page.
3. **A result** of a class producer also gets a row (`results/pr_<PR>.json` under #1049's layout) and is marked
   "provisional: calendar not read at the target day" on the results page.
4. A new one-step fit of a calendar or scheduled column raises `ValueError` from the guard. The fix is direct pairs or
   dropping the column, never a new allow-list entry: that is Eleonora's decision.
5. Run `tests/test_provisional_register.py` and `test_one_step_guard`.
