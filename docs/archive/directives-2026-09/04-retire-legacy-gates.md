# Directive: retire the legacy ownership gates

Can run at any time. Work it as one pull request. It touches CI and `.claude/`, so it needs Eleonora's review.

**Goal.** Remove the machinery that enforced a file-ownership split between two branches the project no longer uses.

**Do:**
- Remove the `ownership` job from `.github/workflows/tests.yml`.
- Remove `.github/check_ownership.py` and `.claude/hooks/ownership_guard.py`, the `PreToolUse` hook entry in
  `.claude/settings.json`, and the tests that exist only to test those files (for example `tests/test_ownership_hook.py`).
- Any other test that imports `check_ownership` for a *current* purpose keeps that purpose, rewritten without the
  ownership concept. Say which in the pull request.
- Remove references to the gate from current documents. Leave `docs/archive/` untouched.

**Acceptance.**
- CI green, with the `ownership` job gone.
- Zero `expectedFailure`.
- `grep -rn "check_ownership\|ownership_guard" --include=*.py --include=*.yml --include=*.json .` finds nothing
  outside `docs/archive/`.
