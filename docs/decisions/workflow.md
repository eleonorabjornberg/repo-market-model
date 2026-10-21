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

## Confirmed exceptions to "never merges"

The planning-session line above ("It never merges") stays as written. This note records what Eleonora herself
confirmed about the process record. It quotes two of her own comments on #269, which she typed in the web UI
(`performed_via_github_app` null, per #256), unedited. The first:
<https://github.com/eleonorabjornberg/repo-market-model/issues/269#issuecomment-6019863374>

> #153 and #236 were my merges. I made the switch call without reviewing 2026 data, because leaps were less relevant to the actual spread I'm trying to forecast.

The second:
<https://github.com/eleonorabjornberg/repo-market-model/issues/269#issuecomment-6019982763>

> I approved the merges of #216 (the final-test pre-registration) and #224 (its amendment). The orchestrating session merged both on my instruction, given off GitHub, before the 2026 days were opened

So #153 and #236 are recorded as her merges, and the 4 October primary-cell switch as her call. Nothing here
records more than these two comments say.

## Market colour stays off repository threads

Decided by Eleonora, 6 October 2026 (#269, item 15; context #219). Commentary about market conditions on days in the
blind tier of `docs/decisions/lockbox.md` is kept off repository threads (issues, pull requests, comments and
commit messages) until those days are scored. It protects the blind tier: a comment on what the market did is
information about outcomes that no forecast built afterwards may be seen to have used.

## Legacy gates

The ownership gate, its CI job and its Claude Code hook are retired, by directive 04.

## Delegated review (in force until Eleonora revokes it)

Decided by Eleonora, 30 September 2026, and extended on 2 October 2026 (#112). Until Eleonora revokes it in writing (a comment on the "Directive queue" issue, or a change to this record), a pull request that closes an
issue in the pinned "Directive queue" issue is reviewed and merged by the "Directive loop" routine (a Claude Code cloud session in the `rmm` environment, hourly; since 1 October it both reviews and implements, and its instructions are in `.claude/routines/directive-loop.md`), not by her. The review session is a separate Claude Code session from the one that implemented the change, never reviews a pull request its own session opened, and does not change code in the pull request it reviews. It merges only when CI is green and the directive's acceptance criteria are met. It
escalates instead of merging (the pull request labelled `needs-eleonora`) when the pull request:

- asks her a question, or its session opened a `needs-eleonora` issue (other than a publishing question under the rule
  below, or a question she has since ruled on under "A ruled question no longer holds a pull request" below);
- changes `docs/decisions/` beyond recording a decision its directive says she has made;
- states a verdict on an exit criterion, or a public claim not generated from a record;
- lacks a required recorded mutation, or one that was not killed, or has any `expectedFailure`;
- changes `metadata/lockbox.json`, which opens a lockbox tier: opening one decides what has been seen;
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
text. The directive cites the ruling by link. A follow-up pull request that adds or changes a decision record under
`docs/decisions/` is the exception: it is always merged by Eleonora herself, whatever ruling it records (Eleonora,
19 October 2026, on #943; see the list of her own actions under "A ruled question no longer holds a pull request"). The
reviewer escalates such a pull request if it changes code, a record in `docs/runs/`, or what the project claims beyond
what the cited ruling says.

**A ruled question no longer holds a pull request.** Decided by Eleonora, 19 October 2026 (in chat, relayed; in force
once she merges this section). A pull request labelled `needs-eleonora` only because it waits on a judgement call may
be merged by the delegated reviewer once Eleonora has ruled on that call, and the pull request implements exactly the
ruling. Her ruling is either her own comment on GitHub, or a comment starting
"**Ruling (Eleonora, <date>; relayed by the orchestrating session):**" that the orchestrating session posts after she
has ruled in chat. A relayed ruling names the pull request or the finding, and states the decision. The reviewer then
removes `needs-eleonora`, reviews the pull request under the rules above, and merges it. A pull request that does
more or less than the ruling, or that is escalated for any other reason on the list above, still waits on her.

These still need her own action on GitHub (a comment, review or merge by `eleonorabjornberg` with
`performed_via_github_app` null and no app footer), as ruled on 6 October 2026 (#256); a ruling relayed from chat
never stands in for it:

- opening any lockbox tier;
- changing a pre-registered primary test;
- approving a model for the live record;
- changing the live model pin;
- registering a candidate;
- merging a decision record under `docs/decisions/`;
- any change to `CLAUDE.md` or `.claude/`.

## Merging, conflicts and long runs

**Status: draft, in force once Eleonora merges it.** Asked for by her on 17 October 2026, after a day in which most
merges were lost to conflicts and to work that ran out of time in the cloud.

**A fix for what blocks every pull request merges first.** When a pull request removes a cause that holds back every
other one (a conflict that every merge creates, or a CI run that every push waits for), Eleonora may name it first in
the top block of the "Directive queue" issue. Until it merges, no other pull request is merged by anyone. Reviews,
fixes and implementation go on, and a review that would merge ends "MERGE (held: merge after #N)" instead. The rule
lapses when the named pull requests have merged; the orchestrating session then removes the line.

**Ready means ready now.** The orchestrating session tells Eleonora that a pull request is ready for her own merge
(a decision record, or anything else only she may merge) only when CI is green on its current head and it merges
cleanly into `main` at that moment. From then until she has merged it, no other pull request is merged, so it stays
clean for her.

**Long runs go to her Mac.** A step expected to take more than about two hours (walk-forward refits, power studies,
long simulations) is not run in a cloud session, where it can run out of time and lose its work. The session commits
the script and the exact commands, pushes its branch, and comments `needs-mac:` with the commands on its pull request.
The orchestrating session hands Eleonora one paste for her Mac in the 5 pm catch-up, which she runs overnight: a fresh clone of that branch, the project's virtual
environment at the declared Python, output to a log file, and a push of the results to the same branch. The pull
request records the Python, numpy and scikit-learn versions of that environment. Her pushed results are then finished
by a cloud session like any other branch.

## Fewer round trips

Merged by Eleonora on 20 October 2026 (#1041); amended by her on 21 October 2026. Asked for by her on 20 October 2026, after a review of the
workflow found that since 6 October about three in five commits that were not merges of a pull request were merges of
`main` into a branch or regenerated files, that about a third of reviews asked for changes a local check would have
caught, and that about half the comments on pull requests were claims and heartbeats.

**A branch is merged with `main` only when `main` changed what it depends on.** Before merging, the reviewer merges
`main` into the branch only when, since the branch's merge base, `main` changed `src/`, `metadata/`,
`tests/fixtures/snapshots/`, or a file the branch also changes, or when GitHub reports a conflict. Otherwise a pull
request whose CI is green on its head merges as it is, and the push CI on `main` checks the combination. Red CI on
`main` is a `hold`, as before. "Ready means ready now" keeps its meaning for her own merges.

**Checks run before review, and review starts on green.** A session runs `python3 scripts/pre_review.py --base
origin/main` and the test modules its change touches before it asks for review; the full suite runs in the pull
request's CI, in its shards, not in the session (Eleonora, 21 October 2026: a cloud session running the whole suite
outlasted its run). The reviewer starts only when every check on the pull request's head has completed, and a red
check sends it back without a review.

**Claims are labels, not comments.** A session claims a pull request with the label `reviewing` or `fixing` and
removes it when done. It keeps one status comment per pull request and edits it, instead of posting "Reviewing", "Still
reviewing" or "Still fixing".

**Long runs go to her Mac, overnight** (Eleonora, 21 October 2026, replacing the long-run workflow first). A step
expected to take more than about two hours goes to her Mac under the rule above: the orchestrating session hands her
its paste in the 5 pm catch-up, she runs it overnight, and the results come back as a commit on the same branch.
`.github/workflows/long-run.yml` stays on `main` but is not part of the routine path.

**Her questions come as options.** A question batched for her lists numbered options and the default that applies if
she does not answer by the next batch. The default is never a change to what the project claims.

**The queue lists open work only.** The orchestrating session removes a line from the "Directive queue" issue once its
issue is closed; the issue's edit history keeps the removed lines.

**Mechanical commits carry a neutral author.** When the orchestrating session commits to someone else's branch (a
merge of `main`, regenerated files), the commit's author and committer are "repo-market-model orchestrator", never
Eleonora's name and never an AI's name, in line with her rule on attribution (#489).

## Forensic audit

Decided by Eleonora, 9 October 2026 (#483). A "Forensic auditor" routine runs once a day at 7:45 am ET, in its own
Claude Code session with the repository attached. It does not run after merges. It audits everything merged since its
previous run and files one `finding` issue per gap, with file and line evidence. It also posts a daily digest as a
comment on the issue "Forensic audit digest".

The auditor never edits code, opens pull requests, changes a rule, or queues a directive. The orchestrating session
triages its findings into directives under the usual rules. A finding that touches the bar, a threshold, a data
meaning or a decision record goes to Eleonora.
