"""Fill in or check the hashes of `metadata/confirmation_preregistration.json` (#585). It scores nothing.

    PYTHONPATH=src python3 scripts/confirmation_preregistration.py freeze   # rewrite the hashes from the tree
    PYTHONPATH=src python3 scripts/confirmation_preregistration.py check    # exit 1 and name each mismatch

`freeze` is a drafting aid: it recomputes `judge.files`, every candidate's `files`, the judge's declaration digest
(`confirmation.candidates` left out) and the panel digest from the working tree, and leaves every other field as
written. Changing a frozen file after the pre-registration is in force is a decision (docs/decisions/confirmation-preregistration.md),
not a side effect of a pull request. `frozen_at.commit` is set by hand to the commit the hashes were taken on.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import confirmation  # noqa: E402


def freeze() -> None:
    path = REPO / confirmation.DEFAULT_PREREGISTRATION
    document = json.loads(path.read_text(encoding="utf-8"))
    for files in [document["judge"]["files"]] + [entry["files"] for entry in document["candidates"]]:
        for name in files:
            files[name] = confirmation.digest_file(REPO / name)
    declaration = document["judge"]["declaration"]
    declaration["sha256"] = confirmation.judge_declaration_digest(
        json.loads((REPO / declaration["path"]).read_text(encoding="utf-8"))
    )
    document["panel"]["sha256"] = json.loads((REPO / document["panel"]["manifest"]).read_text(encoding="utf-8"))["sha256"]
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list) -> int:
    if argv[1:] == ["freeze"]:
        freeze()
        return 0
    if argv[1:] == ["check"]:
        problems = confirmation.verify()
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
