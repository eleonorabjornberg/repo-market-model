#!/usr/bin/env python3
"""The research sections of the results page (#645): executive summary, current best performer, H1 to H10.

Read by `scripts/emit_visual.py`. Everything shown is parsed from tracked sources:

- `docs/research/plan.md`: each hypothesis's goal, test, kill criterion, next step and status;
- `docs/research/hypotheses/H<n>.md`: its owner, question, milestones and progress markers;
- `docs/research/log.md`: its log view (every entry tagged `[H<n>]`);
- `docs/research/milestones.json`: the two facts no other source holds, which milestones are done (each with the
  tracked file that shows it) and a step floor for a hypothesis whose work predates the log.

Nothing is typed into the page. A figure with no source reads "not measured"; a figure from development days
carries the label `DEV_LABEL`. Standard library only.
"""
from __future__ import annotations

import html
import importlib.util
import json
import re
from pathlib import Path

_spec = importlib.util.spec_from_file_location("check_research_log", Path(__file__).with_name("check_research_log.py"))
check_research_log = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_research_log)

PLAN = "docs/research/plan.md"
LOG = "docs/research/log.md"
PROGRESS = "docs/research/milestones.json"
HYPOTHESES = "docs/research/hypotheses"
INPUTS = (PLAN, LOG, PROGRESS, HYPOTHESES)

DEV_LABEL = "development, not a verdict"
NOT_MEASURED = "not measured"
#: The six steps every hypothesis follows (`docs/research/plan.md`, "Every hypothesis follows the same steps").
STEPS = ("Question", "Groundwork", "Development", "Registration", "Confirmation", "Verdict")
REPOSITORY = "eleonorabjornberg/repo-market-model"


class ResearchError(ValueError):
    """A source is missing something the page must show; the page is not built."""


def esc(text):
    return html.escape(text, quote=True)


REF_LIST = re.compile(r"#\d+(?:,\s*(?:and\s+)?#\d+)+")
REF_PARENS = re.compile(r"\s*\(\s*#\d+(?:[,;\s]+(?:and\s+)?#\d+)*\s*\)")
GITHUB_ITEM = re.compile(r"\[([^\]]+)\]\(https://github\.com/[^)\s]*/(?:issues|pull)/\d+[^)\s]*\)")


def lay(text):
    """The text without issue or pull request numbers: the page is for a lay reader (`LayReaderPageTests`).

    A link to an issue keeps its words and loses its target; a reference becomes "a tracked directive" (or
    "tracked directives"), and a parenthesis holding only references goes. Returns None when no words are left.
    """
    out = GITHUB_ITEM.sub(r"\1", text)
    out = REF_PARENS.sub("", out)
    out = REF_LIST.sub("tracked directives", out)
    out = re.sub(r"(?<![\w&/])#\d+\b", "a tracked directive", out)
    out = re.sub(r"\bThe a tracked directive\b", "A tracked directive", out)
    words = re.sub(r"tracked directives?|a tracked directive", "", out)
    return out.strip() if re.search(r"[A-Za-z0-9]", words) else None


def inline(text):
    """Escape a Markdown fragment, rendering `code` and **bold**; issue numbers are removed (`lay`)."""
    out = esc(lay(text) or "")
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", out)


def read(repo, rel):
    return (Path(repo) / rel).read_text(encoding="utf-8")


# ---------------------------------------------------------------- parsing


def parse_plan(text):
    """The hypotheses of the plan, in order: id, title, role (primary/secondary/None), bullets, status."""
    found = []
    for block in re.split(r"(?m)^(?=## )", text):
        head = re.match(r"## (H\d+)(?: \((primary|secondary) goal\))?[.:]?\s*(.*)$", block.splitlines()[0]) if block else None
        if not head:
            continue
        bullets = {}
        for line in block.splitlines()[1:]:
            m = re.match(r"^- \*\*([^*:]+?):?\*\*:?\s*(.*)$", line)
            if m:
                bullets[m.group(1).strip().lower()] = m.group(2).strip()
        found.append({"id": head.group(1), "role": head.group(2), "title": head.group(3).rstrip("."),
                      "bullets": bullets})
    if not found:
        raise ResearchError(f"{PLAN} names no hypothesis")
    return found


def bullet(entry, *names):
    for name in names:
        if name in entry["bullets"]:
            return entry["bullets"][name]
    return None


def section(text, label):
    """The text of a bold-labelled paragraph (`**Label.** text`, `**Label**` then bullets), or None."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^\*\*{re.escape(label)}(?:\.\*\*|\*\*)\s*(.*)$", line)
        if not m:
            continue
        body = [m.group(1)] if m.group(1) else []
        for later in lines[i + 1:]:
            if not later.strip():
                if body:
                    break
                continue
            if later.startswith("**") or later.startswith("## "):
                break
            body.append(later)
        return "\n".join(body).strip()
    return None


def parse_manual(hid, text):
    """A manual's question, owner, milestones (id, text) and progress markers."""
    question = section(text, "Question")
    owner = section(text, "Owner")
    milestone_text = section(text, "Milestones") or section(text, "Milestones (done when)") or ""
    milestones = [(m.group(1), m.group(2).strip())
                  for m in (re.match(r"^- (M\d+)\.\s*(.*)$", line) for line in milestone_text.splitlines()) if m]
    markers_text = section(text, "Progress markers") or section(text, "Markers") or ""
    bullets = [line[2:].strip() for line in markers_text.splitlines() if line.startswith("- ")]
    if bullets:
        markers = [b.rstrip(".") for b in bullets]
    else:
        markers = [part.strip().rstrip(".") for part in re.split(r";", markers_text) if part.strip()]
    if not question:
        raise ResearchError(f"{HYPOTHESES}/{hid}.md has no **Question.**")
    if not milestones:
        raise ResearchError(f"{HYPOTHESES}/{hid}.md has no milestone list (`- M1. ...` under **Milestones**)")
    return {"question": question, "owner": owner, "milestones": milestones, "markers": markers}


def parse_log_entries(text):
    """Log entries as dicts, keyed by hypothesis."""
    by_h = {}
    for number, match, heading, fields in check_research_log.parse_log(text):
        if not match:
            raise ResearchError(f"{LOG} line {number}: malformed heading {heading!r}")
        date, hid, step, groundwork, ref = match.group("date", "hyp", "step", "groundwork", "ref")
        by_h.setdefault(hid, []).append({"date": date, "step": int(step) if step else None, "groundwork": groundwork,
                                         "ref": ref, "line": number, "fields": fields})
    return by_h


def load(repo):
    """Everything the page shows, as plain data."""
    plan = parse_plan(read(repo, PLAN))
    progress = json.loads(read(repo, PROGRESS))
    log = parse_log_entries(read(repo, LOG))
    done = progress.get("milestones", {})
    for key, item in done.items():
        if not (Path(repo) / item["evidence"]).exists():
            raise ResearchError(f"{PROGRESS}: {key} cites {item['evidence']}, which is not tracked")
    hypotheses = []
    for entry in plan:
        hid = entry["id"]
        manual = parse_manual(hid, read(repo, f"{HYPOTHESES}/{hid}.md"))
        known = {f"{hid}.{mid}" for mid, _ in manual["milestones"]}
        stray = sorted(k for k in done if k.startswith(hid + ".") and k not in known)
        if stray:
            raise ResearchError(f"{PROGRESS}: {stray} are not milestones of the {hid} manual")
        entries = log.get(hid, [])
        floor = progress.get("steps", {}).get(hid, 1)
        step = max([floor] + [e["step"] for e in entries if e["step"] is not None])
        status_text = (bullet(entry, "status") or "").split(".")[0].strip().lower()
        status = status_text.split(",")[0]
        hypotheses.append({
            "id": hid, "role": entry["role"], "title": entry["title"], "plan": entry["bullets"], "status_text": status_text,
            "manual": manual, "log": entries, "step": step, "status": status,
            "done": {mid for mid, _ in manual["milestones"] if f"{hid}.{mid}" in done},
            "evidence": {mid: done[f"{hid}.{mid}"]["evidence"] for mid, _ in manual["milestones"]
                         if f"{hid}.{mid}" in done}})
    unknown = sorted(set(log) - {h["id"] for h in hypotheses})
    if unknown:
        raise ResearchError(f"{LOG} names {unknown}, which the plan does not")
    return hypotheses


# ---------------------------------------------------------------- rendering


def verdicts(hypotheses):
    """A hypothesis whose plan status is supported or killed has a verdict; otherwise it is open."""
    return [h for h in hypotheses if h["status"] in ("supported", "killed")]


def first_open(h):
    for mid, text in h["manual"]["milestones"]:
        if mid not in h["done"]:
            return mid, text
    return None


def summary_html(hypotheses):
    goals = [h for h in hypotheses if h["role"]]
    goal_items = "".join(
        f'<li><b>{esc(h["role"].capitalize())} goal, {h["id"]}.</b> {inline(h["title"])}</li>'
        for h in sorted(goals, key=lambda h: h["role"] != "primary"))
    rows = "".join(
        f'<tr><th scope="row"><a href="#{h["id"].lower()}">{h["id"]}</a></th>'
        f'<td data-label="Step">{h["step"]} of {len(STEPS)}: {STEPS[h["step"] - 1]}</td>'
        f'<td data-label="Status">{esc(h["status_text"] or "open")}</td></tr>'
        for h in hypotheses)
    reached = verdicts(hypotheses)
    verdict_text = ("none yet" if not reached else "; ".join(f'{h["id"]}: {esc(h["status"])}' for h in reached))
    next_items = []
    for h in sorted([h for h in hypotheses if h["id"] == "H1" or h["role"]],
                    key=lambda h: (h["role"] != "primary", h["role"] != "secondary", h["id"])):
        opened = first_open(h)
        if opened:
            next_items.append(f'<li><b>{h["id"]}</b>, first open milestone {opened[0]}: {inline(opened[1])}</li>')
    return (
        '<div class="rs-box"><h3>The two goals</h3><ul>' + goal_items + '</ul></div>'
        '<div class="rs-box"><h3>Where each hypothesis stands</h3>'
        '<table class="rs-table" aria-label="Hypotheses by step"><thead><tr><th scope="col">Hypothesis</th>'
        '<th scope="col">Step</th><th scope="col">Status</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
        f'<div class="rs-box"><h3>Verdicts reached</h3><p>{verdict_text}. A verdict needs prospective confirmation '
        'days; development data never gives one '
        '(<a href="https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/decisions/scoring-protocol.md">'
        'scoring protocol v1</a>).</p></div>'
        '<div class="rs-box"><h3>Next on the critical path</h3><ul>' + "".join(next_items) + '</ul>'
        '<p class="rs-note">Each line is the first milestone not yet marked done in '
        '<code>docs/research/milestones.json</code>, for the two goals and for H1, whose checks block every '
        'registration.</p></div>')


def best_html(final):
    """The incumbent and the development leader (#645 §2). `final` is the page's final-test payload."""
    figs = (f'On the {final["days"]} days {final["first"]} to {final["last"]} the published declaration scored '
            f'{final["published"]:.2f} bp mean CRPS at h = 1, as that record scores it (not the protocol\u2019s '
            f'grid CRPS), against {final["persistence"]:.2f} bp for as-of persistence '
            f'(edge {final["mean"]:+.2f} bp, {final["level"]}% interval {final["lower"]:+.2f} to '
            f'{final["upper"]:+.2f}).')
    return (
        '<p class="rs-lede">No candidate is registered under the scoring protocol yet, so the incumbent stands: '
        'the published v1 funding declaration, which the protocol uses as its benchmark B3.</p>'
        '<div class="rs-box"><h3>Incumbent: published v1 funding declaration</h3>'
        f'<p>{esc(figs)} <span class="rs-tag">{esc(DEV_LABEL)}</span></p>'
        f'<p class="rs-note">From the published record <code>{esc(final["record"])}</code>, read by the final-test '
        'chapter below; this page scores nothing itself.</p></div>'
        '<div class="rs-box"><h3>Development leader</h3>'
        f'<p>{NOT_MEASURED}: no committed evidence names one by the protocol&rsquo;s primary score (grid CRPS over '
        f'h = 1&ndash;5). When one does, it appears here beside the incumbent, labelled '
        f'&ldquo;{esc(DEV_LABEL)}&rdquo;.</p></div>'
        '<p class="rs-note rs-q"><b>Question for Eleonora.</b> The default rule shown here is the best registered '
        'candidate under the protocol, else the incumbent, with the development leader beside it. It stands until '
        'she rules.</p>')


def log_html(h):
    if not h["log"]:
        return '<p class="rs-note">No log entry yet.</p>'
    items = []
    for e in h["log"]:
        link = f'<a href="{BLOB}{LOG}#L{e["line"]}">log entry</a>'
        f = e["fields"]
        items.append(
            f'<li><b>{e["date"]}</b>, {"groundwork " + e["groundwork"] if e["step"] is None else "step " + str(e["step"])}, {link}, tier {esc(f.get("Tier", ""))}'
            + (f' <span class="rs-tag">{esc(DEV_LABEL)}</span>' if f.get("Tier") == "development" else "")
            + f'<br>{inline(f.get("Result", ""))}<br><i>Against kill:</i> {inline(f.get("Against kill", ""))}</li>')
    return '<ul class="rs-log">' + "".join(items) + '</ul>'


def row(label, text):
    """A definition row, or nothing when the text is empty once issue numbers are gone."""
    return f"<dt>{label}</dt><dd>{inline(text)}</dd>" if text and lay(text) else ""


def hypothesis_html(h):
    m, p = h["manual"], h["plan"]
    goal = p.get("target") or p.get("targets")
    open_questions = p.get("open questions")
    kill = p.get("kill") or p.get("kill or fix") or NOT_MEASURED
    tests = p.get("test") or p.get("tests")
    miles = "".join(
        f'<li class="{"done" if mid in h["done"] else "open"}"><b>{mid}</b> '
        f'<span class="rs-state">{"done" if mid in h["done"] else "open"}</span> {inline(text)}'
        + (f' <a href="{BLOB}{esc(h["evidence"][mid])}">evidence</a>' if mid in h["done"] else "") + '</li>'
        for mid, text in m["milestones"])
    markers = "".join(f'<li>{inline(x)}: <span class="rs-nm">{NOT_MEASURED}</span></li>' for x in m["markers"]) \
        or f'<li>{NOT_MEASURED}</li>'
    role = f' <span class="rs-tag">{esc(h["role"])} goal</span>' if h["role"] else ""
    return (
        f'<article class="rs-h" id="{h["id"].lower()}" aria-labelledby="{h["id"].lower()}-t">'
        f'<h3 id="{h["id"].lower()}-t">{h["id"]}. {inline(h["title"])}{role}</h3>'
        f'<dl><dt>Question</dt><dd>{inline(m["question"])}</dd>'
        + row("Goal", goal) + row("Open questions", open_questions) + row("Test", tests)
        + f'<dt>Kill criterion</dt><dd>{inline(kill[:1].upper() + kill[1:])}</dd>'
        f'<dt>Owner</dt><dd>{inline(m["owner"] or NOT_MEASURED)}</dd>'
        f'<dt>Step</dt><dd>{h["step"]} of {len(STEPS)}: {STEPS[h["step"] - 1]}; status {esc(h["status_text"] or "open")}</dd>'
        f'<dt>Milestones</dt><dd><ul class="rs-miles">{miles}</ul></dd>'
        f'<dt>Progress markers</dt><dd><ul>{markers}</ul></dd>'
        f'<dt>Development variants</dt><dd><span class="rs-nm">{NOT_MEASURED}</span> '
        f'(the running count belongs to the progress page, which is not built yet)</dd>'
        f'</dl><details><summary>Research log for {h["id"]}</summary>{log_html(h)}</details></article>')


BLOB = f"https://github.com/{REPOSITORY}/blob/main/"


def hypotheses_html(hypotheses):
    return "".join(hypothesis_html(h) for h in hypotheses)


def payload(hypotheses):
    """The page's research data, for `docs/visual/data/research.json`."""
    return [{"id": h["id"], "role": h["role"], "title": h["title"], "step": h["step"], "status": h["status"],
             "question": h["manual"]["question"], "owner": h["manual"]["owner"],
             "milestones": [{"id": mid, "text": text, "done": mid in h["done"],
                             "evidence": h["evidence"].get(mid)} for mid, text in h["manual"]["milestones"]],
             "markers": h["manual"]["markers"],
             "log": [{"step": e["step"], "groundwork": e["groundwork"], "line": e["line"]} for e in h["log"]]}
            for h in hypotheses]


def fills(repo, final):
    hypotheses = load(repo)
    return {"research_summary": summary_html(hypotheses), "research_best": best_html(final),
            "research_hypotheses": hypotheses_html(hypotheses)}, payload(hypotheses)
