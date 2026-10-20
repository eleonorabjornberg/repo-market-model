"""The three files that are built on main and never committed (#928), built here for the tests that read them.

`site/index.html`, `docs/visual/data/` and `docs/research/log.md` are gitignored. A pull request changes their inputs
(entry files, records, code) and never the outputs, so a test that reads one calls `ensure()` first. It builds all
three from the tree under test, once per process, and the copy it writes is the one that tree would publish: a test
sees the page this pull request would produce, never a stale one.

The progress page and its data (`docs/pivot/progress.md`, `docs/research/progress.json`) are built on main too, but
no test reads them from disk: `tests/test_emit_progress.py` builds them in memory or in a temporary directory, because
ordering the candidates needs the full history.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_built = False


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ensure():
    """Write the page, its data and the assembled log from the tree, once per process."""
    global _built
    if _built:
        return
    log = _load("check_research_log", "check_research_log.py")
    header, files = log.read_entry_files()
    log.LOG.write_text(log.assemble(header, files, log.read_corrections()), encoding="utf-8")
    visual = _load("emit_visual", "emit_visual.py")
    for rel, data in visual.generate(ROOT).items():
        (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / rel).write_bytes(data)
    _built = True
