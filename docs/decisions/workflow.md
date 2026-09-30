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

## Delegated review (in force until directive 06 merges)

Decided by Eleonora, 30 September 2026. Until the directive 06 pull request merges, a pull request that closes an
issue in the pinned "Directive queue" issue is reviewed and merged by the review session in
`.github/workflows/directive-loop.yml`, not by her. The review session is a separate Claude Code session with
read-only repository access. It merges only when CI is green and the directive's acceptance criteria are met. It
escalates instead of merging (the pull request labelled `needs-eleonora`, the queue on `hold`) when the pull request:

- asks her a question, or its session opened a `needs-eleonora` issue;
- changes `docs/decisions/` beyond recording a decision its directive says she has made;
- states a verdict on an exit criterion, or a public claim not generated from a record;
- lacks a required recorded mutation, or one that was not killed, or has any `expectedFailure`;
- moves the panel digest when its directive does not rebuild the panel, or reaches well outside its directive;
- leaves the reviewer unsure.

A finding that blocks the next queued directive may be made a directive and inserted into the queue by the review
session. Other findings wait for her triage. When the queue is done, merging returns to her.
