# Records scored under the purge rule

These records were scored before `docs/decisions/information-set.md` took effect. They were moved here, unedited, by
the re-scoring pull request for directive 03 (#27), as that decision requires.

**The rule they were scored under.** Every input was read at the feature row chosen by the purge: the latest panel
row dated at least `derived.purge_days` (6) calendar days before the scored day. That rule never leaks, but it reads
every input about a week late, so these records do not measure a next-business-day forecast.
`docs/pivot/lag-assessment.md` sets out the evidence. Each record's `derived.purge_days` names the rule, and
`provenance.code.commit` names the commit that scored it.

**The panel they were scored on.** SHA-256 `d8b716cf…`: the panel from before `reserve_balances` and `tga` were
carried in USD billions (#41), and before `quarter_end` became the last business day of the quarter (#44). The panel
manifest beside them, `funding_panel.manifest.json`, is that panel's.

**What they are still good for.** They are valid measurements of the conservative design, and they are the baseline
for the comparison in the directive 03 pull request of which earlier conclusions survive, change or reverse
(`docs/pivot/lag-assessment.md` §4). No page is generated from them: `scripts/emit_results.py` renders from the
records at the top level of `docs/runs/` only.

**The labels they were scored on (#155).** Every record here compared the floating-point spread with each threshold,
so a day exactly on τ counted as above τ: SOFR 2.00 less IORB 1.95 is 5.000000000000004 bp, labelled above +5 bp.
`docs/decisions/pressure-probability.md` says the event is the spread, in whole basis points, strictly above τ, and
the code reads it that way from #155. Their +5 and +10 bp event figures (Brier, average precision, skill, the
benchmark pairs) therefore count some days on the threshold as pressure days. They are not re-scored, and the
records themselves are unedited.
