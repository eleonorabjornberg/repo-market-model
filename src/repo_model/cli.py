"""Command-line entry point. Owned by the human, and by neither track.

This file is a dispatcher and nothing else. It names no subcommand, imports no
handler, and carries no track's vocabulary. Every command is contributed by a
track-owned registration module:

    src/repo_model/cli_data.py   Track A (data layer)
    src/repo_model/cli_eval.py   Track B (model and evaluation)

### Why this file is split

It previously belonged to nobody. It was in no track's `forbidden` list and not
in `SHARED`, so the ownership gate neither blocked an edit to it nor surfaced
one for review: both tracks could add a subcommand and nothing would say so
until the merge. That is the same hole as a field named in prose without a key
name -- the failure this project has now paid for four times.

Assigning the whole file to one track would only move the hole. `audit` and
`fetch` stand on the data layer; `backtest` stands on the benchmark side; and
the two subcommands next in line -- Track A's download adapters and Track B's
event holdout -- belong to different tracks. So the file is split at the seam
instead, which is what this project does with every shared shape: name it, make
it executable, and put it out of both tracks' reach.

The property that closes the hole: **adding a subcommand is a change to exactly
one track-owned module and requires no edit here.** `tests/test_contract.py`
asserts it, by checking that this file calls `add_parser` nowhere.

Stdlib only, by contract.
"""

from __future__ import annotations

import argparse
import sys

from . import cli_data, cli_eval

#: Registration modules, in the order their commands appear in `--help`.
#: A new *module* is added here by the human, once. A new *command* is not,
#: which is the entire point of the split.
REGISTRARS = (cli_data.register, cli_eval.register)


def build_parser() -> argparse.ArgumentParser:
    """Assemble the parser from every track's registration module.

    Each `register` receives the subparsers action and must call
    `set_defaults(handler=...)` on every subparser it adds. A handler takes the
    parsed namespace and returns a process exit code.
    """

    parser = argparse.ArgumentParser(prog="repo-model")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for register in REGISTRARS:
        register(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse, dispatch, and translate expected failures into exit code 2.

    The caught tuple is `(OSError, ValueError)` rather than the original
    `(DataContractError, OSError, ValueError)`. That is not a narrowing:
    `data.DataContractError` and `splits.SplitError` both subclass `ValueError`,
    so the old tuple already meant exactly this one. Writing it without the
    track-owned names is deliberate -- it keeps a track's exception vocabulary
    out of a human-owned file, so a track can add or rename its own error type
    without needing an edit here. A track wanting a *different* failure mode
    should catch it in its own handler and return an exit code.
    """

    args = build_parser().parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        # A subparser that registered no handler. A traceback here would blame
        # the user for a registration module's omission, so name the command
        # and the obligation instead.
        print(
            f"error: command {args.command!r} registered no handler; its "
            "registration module must call set_defaults(handler=...)",
            file=sys.stderr,
        )
        return 2

    try:
        return handler(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
