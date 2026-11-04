#!/usr/bin/env python3
"""Build a decision-cards page from a JSON spec.

Usage: python3 build.py spec.json out.html

spec.json:
{
  "title": "Decision Docket",                 # browser tab, 2-4 words
  "heading": "Decisions waiting for you",
  "subtitle": "Project X, 2026-11-04. Tap an option to record it ...",
  "footer": "Recommendations are marked Rec. Details are in the file named on each card.",
  "groups": ["Settings", "Analysis"],          # filter chips, in order
  "decisions": [
    {"id": "q6", "group": "Settings", "tag": "Q6", "title": "...",
     "ctx": "one or two sentences", "blocks": "what it blocks (optional)",
     "flag": "warning (optional)",
     "opts": [["a", "Option A", true], ["b", "Option B"]],   # true = recommended
     "where": "file with the full options"}
  ]
}
Text is inserted as text (no HTML). Checks ids are unique, every group is
listed, and every card has at least two options.
"""
import html
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"


def js(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def main(spec_path, out_path):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    decisions, groups = spec["decisions"], spec["groups"]
    ids = [d["id"] for d in decisions]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        sys.exit(f"duplicate ids: {sorted(dupes)}")
    for d in decisions:
        if d["group"] not in groups:
            sys.exit(f"{d['id']}: group {d['group']!r} not in groups")
        if len(d.get("opts", [])) < 2:
            sys.exit(f"{d['id']}: needs at least two options")
    page = TEMPLATE.read_text()
    subs = {
        "__TITLE__": html.escape(spec.get("title", "Decision Docket")),
        "__HEADING__": html.escape(spec.get("heading", "Decisions waiting for you")),
        "__SUBTITLE__": html.escape(spec.get("subtitle", "")),
        "__FOOTER__": html.escape(spec.get("footer", "")),
        "__DECISIONS__": js(decisions),
        "__GROUPS__": js(groups),
    }
    for key, val in subs.items():
        page = page.replace(key, val, 1)
    pathlib.Path(out_path).write_text(page)
    print(f"wrote {out_path}: {len(decisions)} cards in {len(groups)} groups")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
