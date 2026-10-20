---
name: publish-record
description: Publish a scored record into docs/runs/ of repo-market-model under docs/decisions/publish-rule.md. Use when a directive says a record is to be published, or a re-score replaces a published figure.
---

# Publish a record

The rule is `docs/decisions/publish-rule.md`; this is the order of work.

1. **Check the record is publishable.** It was scored at commit `R`. It may be published only if
   `git diff --name-only R origin/main -- src/ metadata/ tests/fixtures/snapshots/` prints nothing. If it prints
   anything, re-score at a commit where it is empty. Never publish with an explanation instead.
2. **Never edit a published record in place.** A changed figure is a new record, or the old one is archived with a note
   saying why. A provisional result is marked by the register, not edited.
3. **One commit carries the records and every page rendered from them:** add the records, run
   `python3 scripts/emit_results.py`, and commit both together. Generated blocks are never hand-edited.
4. **Then, in a later commit,** regenerate `docs/status.json` with `python3 scripts/emit_status.py` if the records are
   top-level in `docs/runs/` (it is stamped with the commit that changed its inputs).
5. Do not commit the results page, its data or the assembled log: they are built on main (#928).
6. Run `python3 scripts/pre_review.py --base origin/main` and `tests/test_generated_results.py`.

Publishing changes a published figure: it needs Eleonora's ruling (a `needs-eleonora` question), unless the directive
cites one. A new input joins the published declaration only after her ruling; until then it is merged present but off.
