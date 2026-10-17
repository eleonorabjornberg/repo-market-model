#!/usr/bin/env python3
"""The research sections of the results page (#645): executive summary, current best performer, H1 to H10.

Read by `scripts/emit_visual.py`. Everything shown is parsed from tracked sources:

- `docs/research/plan.md`: each hypothesis's goal, test, kill criterion, next step and status, and its "Critical path" section;
- `docs/research/hypotheses/H<n>.md`: its owner, question, milestones and progress markers;
- `docs/research/log.md`: its log view (every entry tagged `[H<n>]`);
- `docs/research/milestones.json`: the two facts no other source holds, which milestones are done (each with the
  tracked file that shows it) and a step floor for a hypothesis whose work predates the log;
- `docs/research/taglines.json`: each hypothesis's one plain-language line, the only part of it shown unfolded (#893).

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
TAGLINES = "docs/research/taglines.json"
INPUTS = (PLAN, LOG, PROGRESS, HYPOTHESES, TAGLINES)

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
    taglines = json.loads(read(repo, TAGLINES)).get("taglines", {})
    stray = sorted(set(taglines) - {entry["id"] for entry in plan})
    if stray:
        raise ResearchError(f"{TAGLINES}: {stray} are not hypotheses of the plan")
    for key, item in done.items():
        if not (Path(repo) / item["evidence"]).exists():
            raise ResearchError(f"{PROGRESS}: {key} cites {item['evidence']}, which is not tracked")
    hypotheses = []
    for entry in plan:
        hid = entry["id"]
        tagline = str(taglines.get(hid, "")).strip()
        if not tagline or not lay(tagline) or lay(tagline) != tagline:
            raise ResearchError(f"{TAGLINES}: {hid} has no tagline, or its tagline cites an issue")
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
            "id": hid, "role": entry["role"], "title": entry["title"], "tagline": tagline, "plan": entry["bullets"], "status_text": status_text,
            "manual": manual, "log": entries, "step": step, "status": status,
            "done": {mid for mid, _ in manual["milestones"] if f"{hid}.{mid}" in done},
            "evidence": {mid: done[f"{hid}.{mid}"]["evidence"] for mid, _ in manual["milestones"]
                         if f"{hid}.{mid}" in done}})
    unknown = sorted(set(log) - {h["id"] for h in hypotheses})
    if unknown:
        raise ResearchError(f"{LOG} names {unknown}, which the plan does not")
    return hypotheses


CRITICAL_PATH = "Critical path"
LINK = re.compile(r"^- (CP\d+)\. (H\d+\.M\d+) \(gates ((?:H\d+)(?:, H\d+)*)\)\. Waits on: (.+)$")


def load_critical_path(repo, hypotheses):
    """The plan's "Critical path" section (#704): ordered links, each a milestone of a manual.

    A link reads `- CP<n>. H<k>.M<j> (gates H5, H9). Waits on: CP<a>; free text.` It is refused when the section
    is missing, a milestone is in no manual, or a link waits on a link that does not come before it. A link is
    done only if `docs/research/milestones.json` says its milestone is.
    """
    text = read(repo, PLAN)
    found = re.search(rf"(?ms)^## {CRITICAL_PATH}\s*$(.*?)(?=^## |\Z)", text)
    if not found:
        raise ResearchError(f"{PLAN} has no '## {CRITICAL_PATH}' section")
    milestones = {f'{h["id"]}.{mid}': mtext for h in hypotheses for mid, mtext in h["manual"]["milestones"]}
    done = {f'{h["id"]}.{mid}' for h in hypotheses for mid in h["done"]}
    links = []
    for line in found.group(1).splitlines():
        if not line.startswith("- CP"):
            continue
        m = LINK.match(line)
        if not m:
            raise ResearchError(f"{PLAN} {CRITICAL_PATH}: malformed link {line!r}")
        cid, milestone, gates, waits = m.groups()
        if milestone not in milestones:
            raise ResearchError(f"{PLAN} {CRITICAL_PATH}: {cid} names {milestone}, which no manual has")
        for goal in gates.split(", "):
            if goal not in {h["id"] for h in hypotheses}:
                raise ResearchError(f"{PLAN} {CRITICAL_PATH}: {cid} gates {goal}, which the plan does not have")
        earlier = {l["id"] for l in links}
        for ref in re.findall(r"\bCP\d+\b", waits):
            if ref not in earlier:
                raise ResearchError(f"{PLAN} {CRITICAL_PATH}: {cid} waits on {ref}, which does not come before it")
        links.append({"id": cid, "milestone": milestone, "text": milestones[milestone],
                      "gates": gates.split(", "), "waits": waits, "done": milestone in done})
    if not links:
        raise ResearchError(f"{PLAN} {CRITICAL_PATH} has no link")
    return links


# ---------------------------------------------------------------- rendering


def verdicts(hypotheses):
    """A hypothesis whose plan status is supported or killed has a verdict; otherwise it is open."""
    return [h for h in hypotheses if h["status"] in ("supported", "killed")]


def first_open(h):
    for mid, text in h["manual"]["milestones"]:
        if mid not in h["done"]:
            return mid, text
    return None


def joined(items):
    """"a", "a and b", "a, b and c"."""
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def ref(h):
    return f'<a href="#{h["id"].lower()}">{h["id"]}</a>'


def lowered(tagline):
    """A tagline as a clause inside a sentence: no closing stop, a lower-case first word unless it is a name."""
    text = tagline.rstrip(".")
    first = text.split(" ", 1)[0]
    return text if (first.isupper() and len(first) > 1) or any(c.isdigit() for c in first) else text[:1].lower() + text[1:]


def summary_html(hypotheses, links):
    """The executive summary as an abstract (#893): prose, the goals and every hypothesis named in running text.

    No table and no list: where each hypothesis stands is in its own fold in section 2.
    """
    goals = sorted((h for h in hypotheses if h["role"]), key=lambda h: h["role"] != "primary")
    others = [h for h in hypotheses if not h["role"]]
    goal_text = " ".join(
        f'<b>{esc(h["role"].capitalize())} goal</b> ({ref(h)}): {inline(lowered(h["tagline"]))}.' for h in goals)
    reached = verdicts(hypotheses)
    verdict_text = ("none yet" if not reached else "; ".join(f'{ref(h)}, {esc(h["status"])}' for h in reached))
    nexts = {}
    for h in goals:
        opened = next((l for l in links if h["id"] in l["gates"] and not l["done"]), None)
        if opened:
            nexts.setdefault(opened["id"], (opened, []))[1].append(h["id"])
    next_text = " ".join(
        f'For {"both goals" if len(gated) == len(goals) > 1 else joined(gated)} it is {link["id"]} '
        f'({link["milestone"]}), {inline(lowered(link["text"]))}, which waits on {inline(link["waits"].rstrip("."))}.'
        for link, gated in nexts.values())
    return (
        '<div class="abstract">'
        '<p>This study forecasts the overnight cost of borrowing cash against U.S. Treasuries, measured as SOFR '
        f'minus the Fed&rsquo;s rate on reserves, and asks what drives it. It has two goals. {goal_text} '
        f'{joined([ref(h) for h in others])} support those goals or follow from them; section 2 gives each one '
        'line, with its step, tests and milestones folded beneath it.</p>'
        f'<p><b>Verdicts reached:</b> {verdict_text}. A verdict needs prospective confirmation days; development '
        'data never gives one '
        '(<a href="https://github.com/eleonorabjornberg/repo-market-model/blob/main/docs/decisions/scoring-protocol.md">'
        'scoring protocol v1</a>). Every figure from development days below is marked '
        f'&ldquo;{esc(DEV_LABEL)}&rdquo;. <b>Next on the critical path.</b> {next_text}</p>'
        '<p class="rs-note">The next link is the first in the plan&rsquo;s &ldquo;Critical path&rdquo; section that '
        'gates the goal and whose milestone is not marked done in <code>docs/research/milestones.json</code>.</p>'
        '</div>')


def best_html(final):
    """The incumbent and the development leader (#645 §2). `final` is the page's final-test payload."""
    figs = (f'On the {final["days"]} days {final["first"]} to {final["last"]} the published declaration scored '
            f'{final["published"]:.2f} bp mean CRPS at h = 1, as that record scores it (not the protocol’s '
            f'grid CRPS), against {final["persistence"]:.2f} bp for as-of persistence '
            f'(edge {final["mean"]:+.2f} bp, {final["level"]}% interval {final["lower"]:+.2f} to '
            f'{final["upper"]:+.2f}).')
    callouts = (
        f'<div class="callouts side"><aside class="callout" aria-label="Key figure: the incumbent&rsquo;s edge">'
        f'<span class="big">{final["mean"]:+.2f}<small>bp</small></span>'
        f'<span class="cap">The published declaration&rsquo;s edge in mean CRPS over as-of persistence at h = 1, on '
        f'{final["days"]} days; {final["level"]}% interval {final["lower"]:+.2f} to {final["upper"]:+.2f}.</span>'
        f'<span class="rs-tag">{esc(DEV_LABEL)}</span></aside>'
        f'<aside class="callout" aria-label="Key figure: the incumbent&rsquo;s score">'
        f'<span class="big">{final["published"]:.2f}<small>bp against {final["persistence"]:.2f}</small></span>'
        f'<span class="cap">Mean CRPS at h = 1 of the published declaration and of as-of persistence, as that record '
        f'scores it; lower is better.</span><span class="rs-tag">{esc(DEV_LABEL)}</span></aside></div>')
    return (
        '<p class="lede">No candidate is registered under the scoring protocol yet, so the incumbent stands: '
        'the published v1 funding declaration, which the protocol uses as its benchmark B3.</p>'
        + callouts +
        '<p><span class="runin">The incumbent.</span> '
        f'{esc(figs)} <span class="rs-tag">{esc(DEV_LABEL)}</span></p>'
        '<p><span class="runin">The development leader.</span> '
        f'<span class="rs-nm">{NOT_MEASURED}</span>: no committed evidence names one by the protocol&rsquo;s primary '
        'score (grid CRPS over h = 1&ndash;5). When one does, it appears here beside the incumbent, labelled '
        f'&ldquo;{esc(DEV_LABEL)}&rdquo;.</p>'
        f'<p class="rs-note">The incumbent&rsquo;s figures are from the published record <code>{esc(final["record"])}</code>, '
        'read by the final-test section below; this page scores nothing itself.</p>'
        '<aside class="rs-q"><b>Question for Eleonora.</b> The default rule shown here is the best registered '
        'candidate under the protocol, else the incumbent, with the development leader beside it. It stands until '
        'she rules.</aside>')


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
    """One hypothesis (#893): one line, its id and tagline, over a native <details> fold holding all the rest."""
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
    hid = h["id"].lower()
    return (
        f'<article class="rs-h" id="{hid}" aria-labelledby="{hid}-t">'
        f'<details class="rs-fold"><summary><span class="rs-id" id="{hid}-t">{h["id"]}</span> '
        f'<span class="rs-line">{inline(h["tagline"])}</span></summary>'
        f'<div class="rs-body"><p class="rs-title"><span class="runin">In the plan.</span> {inline(h["title"])}.{role}</p>'
        f'<dl><dt>Question</dt><dd>{inline(m["question"])}</dd>'
        + row("Goal", goal) + row("Open questions", open_questions) + row("Test", tests)
        + f'<dt>Kill criterion</dt><dd>{inline(kill[:1].upper() + kill[1:])}</dd>'
        f'<dt>Owner</dt><dd>{inline(m["owner"] or NOT_MEASURED)}</dd>'
        f'<dt>Step</dt><dd>{h["step"]} of {len(STEPS)}: {STEPS[h["step"] - 1]}; status {esc(h["status_text"] or "open")}</dd>'
        f'<dt>Milestones</dt><dd><ul class="rs-miles">{miles}</ul></dd>'
        f'<dt>Progress markers</dt><dd><ul>{markers}</ul></dd>'
        f'<dt>Development variants</dt><dd><span class="rs-nm">{NOT_MEASURED}</span> '
        f'(the running count belongs to the progress page, which is not built yet)</dd>'
        f'</dl><details class="rs-logfold"><summary>Research log for {h["id"]}</summary>{log_html(h)}</details>'
        f'</div></details></article>')


BLOB = f"https://github.com/{REPOSITORY}/blob/main/"


def steps_html():
    """The plan's six steps, for the margin beside the hypotheses (#893)."""
    return ('<aside class="side sidenote" aria-label="The six steps"><p class="label">The six steps</p><ol>'
            + "".join(f"<li>{esc(step)}</li>" for step in STEPS)
            + '</ol><p>Development is on past days and never gives a verdict; confirmation is on days still to come.</p>'
            '</aside>')


def hypotheses_html(hypotheses):
    return "".join(hypothesis_html(h) for h in hypotheses)


def payload(hypotheses):
    """The page's research data, for `docs/visual/data/research.json`."""
    return [{"id": h["id"], "role": h["role"], "title": h["title"], "tagline": h["tagline"], "step": h["step"], "status": h["status"],
             "question": h["manual"]["question"], "owner": h["manual"]["owner"],
             "milestones": [{"id": mid, "text": text, "done": mid in h["done"],
                             "evidence": h["evidence"].get(mid)} for mid, text in h["manual"]["milestones"]],
             "markers": h["manual"]["markers"],
             "log": [{"step": e["step"], "groundwork": e["groundwork"], "line": e["line"]} for e in h["log"]]}
            for h in hypotheses]


def fills(repo, final):
    hypotheses = load(repo)
    links = load_critical_path(repo, hypotheses)
    return {"research_summary": summary_html(hypotheses, links), "research_best": best_html(final),
            "research_steps": steps_html(),
            "research_hypotheses": hypotheses_html(hypotheses)}, payload(hypotheses)
