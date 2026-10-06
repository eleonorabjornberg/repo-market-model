"""The phase status `scripts/emit_status.py` reads from PLAN.md's headings.

A phase can be **closed for now** (Eleonora, 5 October 2026, #234): she stopped
working it with items still open, and started the next one. That is neither
"complete" nor "in progress", and the status file must say which it is rather
than fold it into either. A closed-for-now phase is not published as finished,
and it is not published as open work beside the current phase either: it is
listed on its own.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("emit_status", ROOT / "scripts" / "emit_status.py")
emit_status = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(emit_status)


def plan(*markers):
    """A PLAN.md with one heading per marker, numbered from 0."""
    lines = []
    for number, marker in enumerate(markers):
        suffix = " (%s)" % marker if marker else ""
        lines += ["## Phase %d — Name %d%s" % (number, number, suffix), "",
                  "Exit criterion: exit %d." % number, ""]
    return emit_status.parse_plan("\n".join(lines))


class ClosedForNowTest(unittest.TestCase):

    def test_closed_phases_before_the_current_one_are_allowed(self):
        phases = plan("complete", "closed for now", "closed for now", "in progress", "")
        self.assertEqual(emit_status.current_phase(phases), (3, "in progress"))

    def test_closed_phases_are_not_published_as_open_alongside(self):
        phases = plan("complete", "closed for now", "in progress", "in progress", "")
        self.assertEqual(emit_status.alongside(phases, 3), [{"number": 2, "name": "Name 2"}])

    def test_closed_phases_are_listed_on_their_own(self):
        phases = plan("complete", "closed for now", "closed for now", "in progress", "")
        self.assertEqual(emit_status.closed_for_now(phases, 3),
                         [{"number": 1, "name": "Name 1"}, {"number": 2, "name": "Name 2"}])

    def test_nothing_in_progress_is_still_refused(self):
        phases = plan("complete", "closed for now", "")
        with self.assertRaises(emit_status.PlanError):
            emit_status.current_phase(phases)

    def test_a_closed_phase_after_the_current_one_is_refused(self):
        phases = plan("complete", "in progress", "closed for now", "")
        with self.assertRaises(emit_status.PlanError):
            emit_status.current_phase(phases)

    def test_an_unmarked_phase_before_the_current_one_is_still_refused(self):
        phases = plan("complete", "", "in progress", "")
        with self.assertRaises(emit_status.PlanError):
            emit_status.current_phase(phases)

    def test_the_published_plan_parses(self):
        phases = emit_status.parse_plan((ROOT / "PLAN.md").read_text(encoding="utf-8"))
        number, state = emit_status.current_phase(phases)
        self.assertEqual(state, "in progress")


if __name__ == "__main__":
    unittest.main()
