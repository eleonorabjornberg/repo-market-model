#!/usr/bin/env python3
"""The research sections of the results page (#645): executive summary, current best performer, H1 to H10.

Read by `scripts/emit_visual.py`. Everything shown is parsed from tracked sources:

- `docs/research/plan.md`: each hypothesis's goal, test, kill criterion, next step and status, and its "Critical path" section;
- `docs/research/hypotheses/H<n>.md`: its owner, question, milestones and progress markers;
- `docs/research/log.md`: its log view (every entry tagged `[H<n>]`);
- `docs/research/milestones.json`: the two facts no other source holds, which milestones are done (each with the
  tracked file that shows it and the merged pull request) and each hypothesis's phase on the plan's six-step scale.
  A log entry's step is the step of the hypothesis's own manual, so it never sets the phase.
- `docs/research/taglines.json`: each hypothesis's one plain-language line, the only part of it shown unfolded (#893).

Nothing is typed into the page. A figure with no source reads "not measured"; a figure from development days
carries the label `DEV_LABEL`. Standard library only.
"""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import re
from pathlib import Path

_spec = importlib.util.spec_from_file_location("check_research_log", Path(__file__).with_name("check_research_log.py"))
check_research_log = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_research_log)
_spec = importlib.util.spec_from_file_location("provisional_register", Path(__file__).with_name("provisional_register.py"))
provisional_register = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(provisional_register)

PLAN = "docs/research/plan.md"
LOG = "docs/research/log"
PROGRESS = "docs/research/milestones.json"
HYPOTHESES = "docs/research/hypotheses"
TAGLINES = "docs/research/taglines.json"
REGISTER = provisional_register.REGISTER
#: The committed records the development standings are read from (#1020): the step 4 record names the candidate; the
#: #960 score holds the paired grid-CRPS figures, and its declaration says how the intervals were drawn.
STEP4 = "docs/pivot/evidence/h5-step4/score.json"
STANDINGS = "docs/pivot/evidence/b1-calendar-960/score.json"
STANDINGS_DECLARATION = "metadata/b1_calendar_960.json"
#: The current H5 candidate (#1152): a small committed record of Eleonora's ruling. The standings read the candidate
#: from it and fall back to the step 4 record only when it is absent. Its scores are #1145's `result.json` (#1173).
CANDIDATE = "docs/research/h5-candidate.json"
CANDIDATE_SCORES = "docs/research/state-calendar-1145/result.json"
#: Every source the page is built from: the one list a new input is added to (#1059). `LOG` and `HYPOTHESES` are
#: directories; `input_files` expands them, and `emit_visual.py` stamps the page with the digest of each.
INPUTS = (PLAN, LOG, PROGRESS, HYPOTHESES, TAGLINES, REGISTER, STEP4, STANDINGS, STANDINGS_DECLARATION,
          CANDIDATE, CANDIDATE_SCORES)

DEV_LABEL = "development, not a verdict"
#: The mark on a figure from a registered result (#1028). It names no issue number: the page is for a lay reader.
PROVISIONAL_LABEL = "provisional: calendar not read at the target day"
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


def input_files(repo):
    """The tracked files the page is digested from: the files of `INPUTS`, then the hypothesis manuals. The log is not
    here: it is built from its entry files (#928), and `log_digest` is its digest."""
    files = [rel for rel in INPUTS if rel not in (LOG, HYPOTHESES)]
    return files + sorted(str(p.relative_to(repo)) for p in (Path(repo) / HYPOTHESES).glob("H*.md"))


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
                  for m in (re.match(r"^- (M\d+[a-z]?)\.\s*(.*)$", line) for line in milestone_text.splitlines()) if m]
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


def log_digest(repo):
    """SHA-256 of the log as `check_research_log.py assemble` builds it from the entry files (#928)."""
    header, files = check_research_log.read_entry_files(Path(repo) / LOG)
    corrections = check_research_log.read_corrections(Path(repo) / LOG)
    return hashlib.sha256(check_research_log.assemble(header, files, corrections).encode("utf-8")).hexdigest()


def parse_log_entries(text, file=None, by_h=None):
    """Log entries as dicts, keyed by hypothesis; `file` names the entry file the text came from (#928)."""
    by_h = {} if by_h is None else by_h
    for number, match, heading, fields in check_research_log.parse_log(text):
        if not match:
            raise ResearchError(f"{file or LOG} line {number}: malformed heading {heading!r}")
        date, hid, step, groundwork, ref = match.group("date", "hyp", "step", "groundwork", "ref")
        by_h.setdefault(hid, []).append({"date": date, "step": int(step) if step else None, "groundwork": groundwork,
                                         "ref": ref, "line": number, "fields": fields, "file": file})
    return by_h


def load(repo):
    """Everything the page shows, as plain data."""
    plan = parse_plan(read(repo, PLAN))
    progress = json.loads(read(repo, PROGRESS))
    log = {}
    for name, text in check_research_log.read_entry_files(Path(repo) / LOG)[1].items():
        parse_log_entries(text, name, log)
    registered = provisional_register.marked_entries(provisional_register.load(repo))
    for entries in log.values():
        for e in entries:
            e["provisional"] = Path(e["file"]).stem in registered
    unknown = sorted(registered - {Path(e["file"]).stem for entries in log.values() for e in entries})
    if unknown:
        raise ResearchError(f"{REGISTER} names log entries that do not exist: {unknown}")
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
        if hid not in progress.get("steps", {}):
            raise ResearchError(f"{PROGRESS}: {hid} has no phase under 'steps' (one of the plan's six steps)")
        step = progress["steps"][hid]
        manual_step = max((e["step"] for e in entries if e["step"] is not None), default=None)
        status_text = (bullet(entry, "status") or "").split(".")[0].strip().lower()
        status = status_text.split(",")[0]
        hypotheses.append({
            "id": hid, "role": entry["role"], "title": entry["title"], "tagline": tagline, "plan": entry["bullets"], "status_text": status_text,
            "manual": manual, "log": entries, "step": step, "manual_step": manual_step, "status": status,
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
        f'&ldquo;{esc(DEV_LABEL)}&rdquo;, and one from a model that did not read calendar days at the target day is '
        f'also marked &ldquo;{esc(PROVISIONAL_LABEL)}&rdquo; until it is re-run. <b>Next on the critical path.</b> {next_text}</p>'
        '<p class="rs-note">The next link is the first in the plan&rsquo;s &ldquo;Critical path&rdquo; section that '
        'gates the goal and whose milestone is not marked done in <code>docs/research/milestones.json</code>.</p>'
        '</div>')


def provisional_mark():
    """The mark on a figure from a registered result (#1028), linked to the register."""
    return (f'<span class="rs-tag rs-prov">{esc(PROVISIONAL_LABEL)} &middot; '
            f'<a href="{BLOB}{REGISTER}">register</a></span>')


#: The models of the standings table, in order, with the name the page prints for each.
STANDING_MODELS = (("B1", "B1"), ("B1_prime", "B1&prime;"), ("spread_mr_ctx", "spread_mr_ctx"))
#: The two groups of the #960 record the table shows: its pooled figure and its headline (ordinary targets).
STANDING_GROUPS = (("pooled", "all decision days", "all days"), ("target_type", "ordinary", "ordinary targets"))


#: The benchmarks the candidate's standings are set beside (#1152), in order, with the name the page prints.
CANDIDATE_BENCHMARKS = (("B1", "B1"), ("B1_prime", "B1&prime;"), ("B2", "B2"), ("gbm_funding", "gbm_funding"),
                        ("spread_mr_ctx", "spread_mr_ctx"))
#: The two groups of #1115's record the headline table shows: its pooled figure and ordinary targets.
CANDIDATE_GROUPS = (("pooled", "all decision days", "all decision days"), ("target_day_type", "ordinary", "ordinary targets"))
#: The splits of the second table: by regime and by target-day type (the protocol's split of a development figure).
CANDIDATE_SPLITS = (("regime", "by regime"), ("target_day_type", "by target-day type"))
#: What the page calls each evidence page of the candidate record: the page is for a lay reader, so no issue number.
EVIDENCE_NAMES = {1145: "state-scaled calendar study", 1115: "calendar-terms study",
                  1141: "walk-forward calibration study", 1255: "SRF-capped candidate study", 1288: "announced-settlement study"}
SPLIT_BENCHMARKS = (("B1", "B1"), ("B1_prime", "B1&prime;"))


def read_mean_d(interval):
    """The reading of a row from the interval on mean d, as the protocol reads it (ruling on #1009).

    d = S(benchmark) - S(candidate): better when the lower end is above zero, worse when the upper end is below
    zero, no difference otherwise. The two-sided 90% interval is the pair of one-sided 95% bounds.
    """
    if not interval:
        return NOT_MEASURED
    lo, hi = interval
    return "better" if lo > 0 else "worse" if hi < 0 else "no difference"


def _pair(group, model, bench):
    """One paired row of #1115's record, copied as it stands: mean d with its interval, skill with its interval."""
    pair = (((group or {}).get("grid_crps") or {}).get("vs") or {}).get(model, {}).get(bench)
    if not pair:
        return None
    return {"d": pair["difference"], "d_interval": pair.get("difference_interval"),
            "skill": pair["skill"], "skill_interval": pair.get("skill_interval")}


def candidate_standings(root):
    """The standings of the candidate `CANDIDATE` names, scored from the committed record it points to, or None.

    Nothing is computed: every mean, difference, skill and interval is copied from the record. None when the record
    does not hold the model it names, or the candidate file cannot be read.
    """
    try:
        rec = json.loads((root / CANDIDATE).read_text(encoding="utf-8"))
        scores_path = rec["scores"]["record"]
        score = json.loads((root / scores_path).read_text(encoding="utf-8"))
        model = rec["scores"]["model"]
        name = rec["candidate"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if model not in score.get("models", ()):
        return None
    declared = rec["scores"].get("benchmarks")
    pairs = [(x["key"], x["label"]) for x in declared] if declared else CANDIDATE_BENCHMARKS
    benches = [(b, shown) for b, shown in pairs if b in score["models"]]
    groups = []
    for key, label, caption in CANDIDATE_GROUPS:
        group = (score.get("groups") or {}).get(key, {}).get(label)
        means = ((group or {}).get("grid_crps") or {}).get("means")
        if not means or model not in means:
            continue
        rows = {b: {"mean": means.get(b), "pair": _pair(group, model, b)} for b, _ in benches}
        groups.append({"caption": caption, "days": group["days"], "own": means[model], "rows": rows})
    if not groups:
        return None
    splits = []
    for key, caption in CANDIDATE_SPLITS:
        rows = []
        for label, group in (score.get("groups") or {}).get(key, {}).items():
            means = ((group or {}).get("grid_crps") or {}).get("means") or {}
            if model not in means:
                continue
            rows.append({"label": label, "days": group["days"], "own": means[model],
                         "pairs": {b: _pair(group, model, b) for b, _ in SPLIT_BENCHMARKS}})
        splits.append({"caption": caption, "rows": rows})
    return {"kind": "candidate", "candidate": name, "benchmarks": benches, "groups": groups, "splits": splits,
            "first": score["notes"]["first"], "last": score["notes"]["last"], "date": rec["date"],
            "ruling": rec["ruling"], "replaces": rec.get("replaces"), "note": rec.get("note"),
            "description": rec.get("description"), "shown_as": rec["scores"].get("shown_as"), "provisional": rec.get("provisional", True),
            "missing": list(rec["scores"].get("not_supplied") or ()),
            "evidence": list(rec.get("evidence") or []), "record": scores_path, "file": CANDIDATE}


def standings(repo):
    """The development standings of the H5 candidate, read from committed records, or None.

    The candidate is the one `CANDIDATE` names (#1152); only when that file is absent does the step 4 record name it
    (#1020). Nothing is computed: every mean, skill and interval is copied from a committed record, the interval type
    from its declaration. None when no record names a candidate or the scoring record does not score it.
    """
    root = Path(repo)
    if (root / CANDIDATE).exists():
        return candidate_standings(root)
    try:
        step4 = json.loads((root / STEP4).read_text(encoding="utf-8"))
        score = json.loads((root / STANDINGS).read_text(encoding="utf-8"))
        declaration = json.loads((root / STANDINGS_DECLARATION).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    name = step4.get("best_candidate")
    if not name or name not in score.get("models", ()):
        return None
    groups = []
    for key, label, caption in STANDING_GROUPS:
        group = (score.get("groups") or {}).get(key, {}).get(label)
        metrics = ((group or {}).get("metrics") or {}).get("grid_crps")
        if not metrics:
            continue
        rows = {}
        for model, _ in ((name, name),) + tuple((m, m) for m, _ in STANDING_MODELS):
            pair = metrics["pairs"].get(f"{name} vs {model}")
            rows[model] = {"mean": metrics["means"].get(model),
                           "skill": pair["skill"] if pair else None,
                           "interval": pair.get("skill_interval") if pair else None}
        groups.append({"caption": caption, "days": group["days"], "rows": rows})
    if not groups:
        return None
    return {"candidate": name, "groups": groups, "first": score["notes"]["first"], "last": score["notes"]["last"],
            "interval": declaration["scoring"]["interval"], "rules": list(score.get("reading_rules") or []),
            "record": STANDINGS, "step4": STEP4}


def candidate_standings_html(st):
    """The standings of the candidate the committed ruling record names (#1152): mean d with its interval and reading."""
    candidate = esc(st["candidate"])
    #: When the scoring record is the candidate's base (#1259), the tables are the base's and say so.
    name = esc(st.get("shown_as") or st["candidate"])
    scored = (f'The tables are not {candidate}&rsquo;s own: they are {name}, scored on the record below; {candidate}&rsquo;s own '
              'scores are on the last evidence page. ') if st.get("shown_as") else ""

    def mean_d(pair):
        if not pair:
            return NOT_MEASURED
        lo = pair["d_interval"]
        text = f'{pair["d"]:+.2f}' + (f' [{lo[0]:+.2f}, {lo[1]:+.2f}]' if lo else " (no interval)")
        return f'{text}, {read_mean_d(lo)}'

    def skill(pair):
        if not pair:
            return NOT_MEASURED
        lo = pair["skill_interval"]
        return f'{100 * pair["skill"]:+.1f}%' + (f' [{100 * lo[0]:+.1f}%, {100 * lo[1]:+.1f}%]' if lo else "")

    def mean(x):
        return NOT_MEASURED if x is None else f"{x:.2f}"

    head = "".join(f'<th scope="col">Grid CRPS, {esc(g["caption"])} ({g["days"]} days)</th>'
                   f'<th scope="col">d = benchmark &minus; {name}, bp [90%], read</th>'
                   f'<th scope="col">{name}&rsquo;s skill [90%]</th>' for g in st["groups"])
    body = []
    for b, shown in st["benchmarks"]:
        cells = "".join(f'<td>{mean(g["rows"][b]["mean"])}</td><td>{mean_d(g["rows"][b]["pair"])}</td>'
                        f'<td>{skill(g["rows"][b]["pair"])}</td>' for g in st["groups"])
        body.append(f'<tr><th scope="row">{shown}</th>{cells}</tr>')
    body.append(f'<tr><th scope="row">{name}</th>' + "".join(
        f'<td>{mean(g["own"])}</td><td>&mdash;</td><td>&mdash;</td>' for g in st["groups"]) + '</tr>')
    split_head = "".join(f'<th scope="col">d against {shown} (bp) [90%], read</th>' for _, shown in SPLIT_BENCHMARKS)
    split_body = []
    for split in st["splits"]:
        split_body.append(f'<tr><th scope="rowgroup" colspan="{3 + len(SPLIT_BENCHMARKS)}">'
                          f'{esc(split["caption"].capitalize())}</th></tr>')
        for row in split["rows"]:
            split_body.append(
                f'<tr><th scope="row">{esc(row["label"])}</th><td>{row["days"]}</td><td>{mean(row["own"])}</td>'
                + "".join(f'<td>{mean_d(row["pairs"][b])}</td>' for b, _ in SPLIT_BENCHMARKS) + '</tr>')
    beside = ", ".join(shown for _, shown in st["benchmarks"][:-1]) + " and " + st["benchmarks"][-1][1]
    missing = ("".join(f"No row compares it with {esc(b)}: its walks were not supplied to the study that scored it. "
                       for b in st.get("missing") or ()))
    if st.get("provisional", True):
        mark = " " + provisional_mark()
        caveat = ('The candidate reads no calendar column, so every figure here is provisional until it is re-run with '
                  'calendar terms read at the target day; it is the best variant of its study, chosen after seeing the '
                  'development days, so the figures are optimistic for it. ')
    else:
        mark = ""
        caveat = ('The candidate reads the calendar at the target day on direct pairs, so its figures are not provisional '
                  'on that account; it was chosen after seeing the development days, so they are optimistic for it. ')
    links = ", ".join(
        f'<a href="{BLOB}{esc(e["page"])}">{esc(EVIDENCE_NAMES.get(e["issue"], "the study"))}</a>'
        + (f' (<a href="{BLOB}{esc(e["mean_d_page"])}">read on the mean-d bound</a>)' if e.get("mean_d_page") else "")
        for e in st["evidence"])
    return (
        '<p><span class="runin">The development standings.</span> '
        f'The H5 candidate is <b>{candidate}</b>, {esc(st["description"] or "the scaled mean reversion of the volatility-scaling study")}. '
        f'<a href="{esc(st["ruling"])}">Eleonora ruled on {esc(st["date"])}</a> that it replaces '
        f'{esc(st["replaces"] or "the previous candidate")}; the committed record is <code>{esc(st["file"])}</code> '
        f'and the evidence pages are {links}. Nothing is registered: registration remains her own action. '
        f'The tables set it beside {beside} on the decision days '
        f'{esc(st["first"])} to {esc(st["last"])}, from the record <code>{esc(st["record"])}</code>; '
        'every figure is copied from it. Mean grid CRPS in bp over horizons one to five, lower is better. '
        'd is the benchmark&rsquo;s score minus the candidate&rsquo;s, positive favouring the candidate; the '
        'interval is the studentized stationary bootstrap&rsquo;s two-sided 90% interval, whose ends are the one-sided '
        '95% bounds, and the reading follows the bound on mean d as the protocol does: better when the lower end is '
        'above zero, worse when the upper end is below, no difference otherwise. The skill interval is drawn '
        'separately and can fall on the other side of zero (Eleonora&rsquo;s ruling on which interval is read), so it is shown for reference and not read. '
        f'{scored}{missing}<span class="rs-tag">{esc(DEV_LABEL)}</span>{mark}</p>'
        f'<table class="rs-standings"><thead><tr><th scope="col">Model</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>'
        '<p class="rs-note"><b>Lens C&rsquo;s caveat.</b> B1&prime; is Lens C&rsquo;s calendar-aware persistence: '
        'B1 with its changes pooled by the target day&rsquo;s type. B1 stays the protocol&rsquo;s benchmark, '
        'but B1 alone is not the honest baseline, so the candidate&rsquo;s gain over B1&prime; is the one to weigh. '
        f'{caveat}The split below is the protocol&rsquo;s: a pooled figure alone is not a result.</p>'
        f'<table class="rs-standings"><thead><tr><th scope="col">Split</th><th scope="col">Days</th>'
        f'<th scope="col">{name}&rsquo;s grid CRPS</th>{split_head}</tr></thead>'
        f'<tbody>{"".join(split_body)}</tbody></table>')


def standings_html(st):
    """The development standings paragraph and table (#1020), or the plain "not measured" when nothing names a candidate."""
    if st and st.get("kind") == "candidate":
        return candidate_standings_html(st)
    if not st:
        return ('<p><span class="runin">The development standings.</span> '
                f'<span class="rs-nm">{NOT_MEASURED}</span>: no committed record names a candidate scored beside '
                f'B1, B1&prime; and spread_mr_ctx. When one does, it appears here, labelled &ldquo;{esc(DEV_LABEL)}&rdquo;.</p>')
    name = st["candidate"]

    def pct(x):
        return NOT_MEASURED if x is None else f"{100 * x:+.1f}%"

    def skill(row):
        if row["skill"] is None:
            return NOT_MEASURED
        lo = row["interval"]
        return pct(row["skill"]) + (f" [{pct(lo[0])}, {pct(lo[1])}]" if lo else " (no interval)")

    def mean(row):
        return NOT_MEASURED if row["mean"] is None else f'{row["mean"]:.2f}'

    mark = provisional_mark()
    head = "".join(f'<th scope="col">Grid CRPS, {esc(g["caption"])} ({g["days"]} days)</th>'
                   f'<th scope="col">{esc(name)}&rsquo;s skill against it</th>' for g in st["groups"])
    body = []
    for model, shown in STANDING_MODELS + ((name, esc(name)),):
        cells = []
        for g in st["groups"]:
            row = g["rows"].get(model) or {"mean": None, "skill": None, "interval": None}
            own = model == name
            cells.append(f'<td>{mean(row)}</td><td>{"&mdash;" if own else skill(row)}</td>')
        body.append(f'<tr><th scope="row">{shown}</th>{"".join(cells)}</tr>')
    rules = "".join(f"<li>{esc(rule)}</li>" for rule in st["rules"])
    return (
        '<p><span class="runin">The development standings.</span> '
        f'The step 4 record (<code>{esc(st["step4"])}</code>) names <b>{esc(name)}</b> as its best candidate. '
        f'The table sets it beside B1, B1&prime; (B1 with its changes pooled by the target day&rsquo;s type) and '
        f'spread_mr_ctx, on the decision days {esc(st["first"])} to {esc(st["last"])}, from the record '
        f'<code>{esc(st["record"])}</code>. No one of them is the leader: B1 alone is not the honest baseline. '
        f'Mean grid CRPS in bp, lower is better; skill is the share of the benchmark&rsquo;s mean score removed, '
        f'positive favours {esc(name)}. Intervals as recorded: {esc(st["interval"])}. '
        f'<span class="rs-tag">{esc(DEV_LABEL)}</span> {mark}</p>'
        f'<table class="rs-standings"><thead><tr><th scope="col">Model</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>'
        + (f'<p class="rs-note">The record&rsquo;s own reading rules:</p><ul>{rules}</ul>' if rules else ""))


def best_html(final, provisional=False, standing=None):
    """The incumbent and the development leader (#645 §2). `final` is the page's final-test payload.

    `provisional` marks the incumbent's figures when the register registers them (#1028). `standing` is
    `standings(repo)` (#1020): the development standings of the candidate the step 4 record names.
    """
    mark = f' {provisional_mark()}' if provisional else ""
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
        f'<span class="rs-tag">{esc(DEV_LABEL)}</span>{mark}</aside>'
        f'<aside class="callout" aria-label="Key figure: the incumbent&rsquo;s score">'
        f'<span class="big">{final["published"]:.2f}<small>bp against {final["persistence"]:.2f}</small></span>'
        f'<span class="cap">Mean CRPS at h = 1 of the published declaration and of as-of persistence, as that record '
        f'scores it; lower is better.</span><span class="rs-tag">{esc(DEV_LABEL)}</span>{mark}</aside></div>')
    return (
        '<p class="lede">No candidate is registered under the scoring protocol yet, so the incumbent stands: '
        'the published v1 funding declaration, which the protocol uses as its benchmark B3.</p>'
        + callouts +
        '<p><span class="runin">The incumbent.</span> '
        f'{esc(figs)} <span class="rs-tag">{esc(DEV_LABEL)}</span>{mark}</p>'
        + standings_html(standing) +
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
        link = f'<a href="{BLOB}{LOG}/{e["file"]}">log entry</a>'
        f = e["fields"]
        items.append(
            f'<li><b>{e["date"]}</b>, {"groundwork " + e["groundwork"] if e["step"] is None else "step " + str(e["step"])}, {link}, tier {esc(f.get("Tier", ""))}'
            + (f' <span class="rs-tag">{esc(DEV_LABEL)}</span>' if f.get("Tier") == "development" else "")
            + (f' {provisional_mark()}' if e.get("provisional") else "")
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
        f'<dt>Step</dt><dd>{h["step"]} of {len(STEPS)}: {STEPS[h["step"] - 1]}; status {esc(h["status_text"] or "open")}'
        + (f'; the manual&rsquo;s own step {h["manual_step"]}' if h["manual_step"] else "") + '</dd>'
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
    incumbent = provisional_register.marks_incumbent(provisional_register.load(repo))
    return {"research_summary": summary_html(hypotheses, links), "research_best": best_html(final, incumbent, standings(repo)),
            "research_steps": steps_html(),
            "research_hypotheses": hypotheses_html(hypotheses)}, payload(hypotheses)
