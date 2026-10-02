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
issue in the pinned "Directive queue" issue is reviewed and merged by the "Directive reviewer" routine (a Claude Code cloud session in the `rmm` environment), not by her. The review session is a separate Claude Code session from the one that implemented the change, and does not change code. It merges only when CI is green and the directive's acceptance criteria are met. It
escalates instead of merging (the pull request labelled `needs-eleonora`) when the pull request:

- asks her a question, or its session opened a `needs-eleonora` issue (other than a publishing question under the rule
  below);
- changes `docs/decisions/` beyond recording a decision its directive says she has made;
- states a verdict on an exit criterion, or a public claim not generated from a record;
- lacks a required recorded mutation, or one that was not killed, or has any `expectedFailure`;
- moves the panel digest when its directive does not rebuild the panel, or reaches well outside its directive;
- leaves the reviewer unsure.

**Escalations do not stop independent work.** Decided by Eleonora, 1 October 2026. An escalated pull request waits
on her, and the queue is not put on `hold` for it. The loop moves on to the next queued item that does not depend on
it. A queue line `- #N (after #A, #B)` marks a dependency: #N waits until #A and #B are closed. An item whose pull
request waits on her is skipped, never re-worked. `hold` is kept for states that block every item: a permission
denial, red CI on `main`, or a run that stalled.

**A question about publishing does not hold back the measurement.** Decided by Eleonora, 2 October 2026. Some
directives score a new input or setting and end by asking her whether it joins the published declaration, or for a
verdict. Such a pull request merges under delegated review with the input present but off in the published
declaration, so no published figure moves. The question is not asked in the pull request: its session opens a
separate `needs-eleonora` issue with the evidence table and a link to the merged pull request, and that issue is the
only thing that waits on her. Neither the question nor its issue is an escalation of the pull request, and the issue
does not block queued directives that build on the merged code. Turning the input on in the published declaration is
a later pull request, made after her ruling.

**Mechanical escalations are ruled under her delegation.** Decided by Eleonora, 1 October 2026. The orchestrating
Claude session that starts the queue's routine rules on these, in a comment starting `**Ruling` and saying "decided
under Eleonora's delegation", and the queue moves on:

- a merge conflict, or CI that does not start;
- a change to the cloud environment or its setup script that the directive needs;
- an acceptance criterion read as met only because the directive removes the code the criterion would protect.

Everything else on the list above stays hers. That covers a question the pull request asks her, a change to
`docs/decisions/`, a verdict or public claim, a threshold, a data meaning, and a published figure.

A finding that blocks the next queued directive may be made a directive and inserted into the queue by the review
session. Other findings wait for her triage. When the queue is done, merging returns to her.

**Pure follow-ups go through the queue too.** Decided by Eleonora, 1 October 2026. A follow-up that only applies a
ruling she has already posted is queued as a directive and merged under delegated review like any other. Examples:
wording that brings a page in line with a ruling, a record's path after it moves, a stale reference in a directive's
text. The directive cites the ruling by link. Recording that ruling in `docs/decisions/` counts as recording a
decision she has made. The reviewer escalates such a pull request if it changes code, a record in `docs/runs/`, or
what the project claims beyond what the cited ruling says.
