# Records scored under the purge rule

Every record in this folder was scored before the as-of information rule
(`docs/decisions/information-set.md`). They are kept as they were published and are
never edited.

**The rule they were scored under.** Each forecast read every input at the panel row
dated at least the derived purge gap (`derived.purge_days`, six days in every
record here) before the scored day. Training used only rows that cleared
that gap. The rule never leaks, but it reads inputs about a week stale, so these
records do not measure a next-day forecast (`docs/pivot/lag-assessment.md`). All were
scored on the panel with digest `d8b716cf…`, before `quarter_end` became the last
business day of the quarter (#44) and before `reserve_balances` and `tga` were
converted to USD billions (#41).

**What replaced them.** Directive 03 (#27) re-scored each record's own declaration
under the as-of rule, with `--refit-every 21`, through `scripts/rescore.py`. The
replacements are in `docs/runs/` under the same file names. `funding_panel.manifest.json`
is the build manifest of the panel the old persistence record was scored on.

`scripts/emit_results.py` renders only from `docs/runs/` at the top level, so nothing
here reaches a generated page.
