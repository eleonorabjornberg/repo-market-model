# Decision: directives, sessions and pull requests

**Status: decided.** `CLAUDE.md` summarises it for agent sessions. This page is how Eleonora runs it.

## The rule

- **Work starts from a directive**: a GitHub issue labelled `directive`, whose body names a goal, acceptance
  criteria, constraints and the files to read. Longer briefs live in `docs/pivot/directives/`, and the issue points
  to one.
- **One cloud session works one directive** on its own branch from `origin/main`, and ends in one pull request.
  Nothing is pushed to `main` directly.
- **The pull request is the report.** Its template asks for the change, the evidence (base SHA, panel digest, paired
  results with intervals), what was checked, and what was not.
- **Findings do not get fixed out of scope.** A session that finds something beyond its directive opens an issue
  labelled `finding`. A judgement call becomes an issue labelled `needs-eleonora`.
- **A pull request merges** when CI (`tests.yml`) is green and Eleonora has approved it. Publishing follows
  `docs/decisions/publish-rule.md`.
- **Decision records are hers.** A session may draft one when a directive asks for it, and it is in force once merged.

## Running it

**Start a session.** Open a new session in the `rmm` environment with one line:

```
Work issue #N in eleonorabjornberg/repo-market-model. Read CLAUDE.md first.
```

Use the stronger model for directives that change scoring or data code, and a lighter one for documentation. Start
a fresh session for every directive rather than continuing a long one.

**Review a pull request.** Read, in this order:
1. "Not checked, or for Eleonora".
2. The evidence table: is it paired against the stated benchmark, with an interval, split by regime?
3. CI.
4. The diff.

Then approve and merge, or comment. To have comments addressed, start a session with
`Address the review comments on PR #N`.

```
gh pr list --repo eleonorabjornberg/repo-market-model
gh pr view N --repo eleonorabjornberg/repo-market-model --comments
gh pr checks N --repo eleonorabjornberg/repo-market-model
gh pr merge N --repo eleonorabjornberg/repo-market-model --merge --delete-branch
```

**Turn findings into directives.** After each merged pull request, or at least weekly, triage the open `finding` and
`needs-eleonora` issues. Each one ends one of three ways:
- **Ruled:** a small pull request lands the decision record, drafted by a session if you like, and the issue is closed.
- **Made a directive:** relabelled `directive`, with acceptance criteria added.
- **Closed with a reason.**

A planning session in Cowork can do the reading for you: it lists the open pull requests and issues, summarises them,
and drafts the next directives for your approval. It never merges.

```
gh issue list --repo eleonorabjornberg/repo-market-model --label finding
gh issue list --repo eleonorabjornberg/repo-market-model --label needs-eleonora
```

**Keep the roadmap honest.** `docs/pivot/plan.md` §7 is the sequence. A pull request that completes a step updates
that step's line in the same pull request, so the plan never lags the tree.

## Legacy gates

The ownership gate, its CI job and its Claude Code hook are retired, by directive 04.
