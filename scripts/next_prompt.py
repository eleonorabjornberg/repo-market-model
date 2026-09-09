#!/usr/bin/env python3
"""Find and surface the current PROMPT.txt for a track, so handing it off doesn't
mean hunting through dated docs/block-*/ folders by hand.

Each round's directives name the live prompt as e.g.
`docs/block-2026-09-09-track-a-queue/PROMPT.txt`. This script finds the most
recently dated `*-track-<a|b>-queue` folder, prints where to run the agent and
the prompt's full text, ready to paste into a fresh CLI session in that
worktree. It does not launch anything itself — it only finds and prints.

Standard library only.

    python3 scripts/next_prompt.py a     # Track A (feature/data-layer, ../rmm-data)
    python3 scripts/next_prompt.py b     # Track B (feature/model-eval, ../rmm-model)
    python3 scripts/next_prompt.py a --path-only    # just the PROMPT.txt path
    python3 scripts/next_prompt.py a --cmd          # just the ready-to-run `claude` command

Edit TRACKS below if a worktree moves or a track's queue-folder naming changes.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TRACKS = {
    "a": {"branch": "feature/data-layer", "worktree": ROOT.parent / "rmm-data",
          "queue_glob": "block-*-track-a-queue"},
    "b": {"branch": "feature/model-eval", "worktree": ROOT.parent / "rmm-model",
          "queue_glob": "block-*-track-b-queue"},
}

DATE_RE = re.compile(r"block-(\d{4}-\d{2}-\d{2})-")


def latest_queue_dir(track):
    candidates = list((ROOT / "docs").glob(TRACKS[track]["queue_glob"]))
    if not candidates:
        return None
    def date_key(p):
        m = DATE_RE.search(p.name)
        return m.group(1) if m else ""
    return max(candidates, key=date_key)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in TRACKS:
        sys.exit("usage: next_prompt.py <a|b> [--path-only|--cmd]")
    track = sys.argv[1]
    info = TRACKS[track]

    queue_dir = latest_queue_dir(track)
    if queue_dir is None:
        sys.exit(f"no {info['queue_glob']} folder found under docs/ — nothing queued for track {track}.")

    prompt_path = queue_dir / "PROMPT.txt"
    if not prompt_path.exists():
        sys.exit(f"{queue_dir} has no PROMPT.txt.")

    if "--path-only" in sys.argv:
        print(prompt_path)
        return

    if "--cmd" in sys.argv:
        print(f"cd \"{info['worktree']}\" && claude \"$(cat \"{prompt_path}\")\"")
        return

    print(f"Track {track.upper()} — {info['branch']}")
    print(f"worktree: {info['worktree']}")
    print(f"prompt:   {prompt_path}")
    print()
    print(f"  cd \"{info['worktree']}\" && claude \"$(cat \"{prompt_path}\")\"")
    print()
    print("-" * 72)
    print(prompt_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
