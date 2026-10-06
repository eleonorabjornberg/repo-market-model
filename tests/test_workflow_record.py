"""The governance edits of #281 (items 12, 13 and 15 of #269) stay in place."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / "docs" / "decisions" / "workflow.md").read_text(encoding="utf-8")
CI = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")


class WorkflowRecordTests(unittest.TestCase):
    def test_lockbox_json_is_on_the_escalation_list(self):
        listed = WORKFLOW.split("It\nescalates instead of merging")[1].split("**Escalations do not")[0]
        self.assertIn("`metadata/lockbox.json`", listed)

    def test_never_merges_stays_and_exceptions_cite_her_comment(self):
        self.assertIn("It never merges.", WORKFLOW)
        self.assertIn("issuecomment-6019863374", WORKFLOW)
        self.assertIn("#153 and #236 were my merges.", WORKFLOW)

    def test_exceptions_quote_her_second_comment_verbatim(self):
        self.assertIn("issuecomment-6019982763", WORKFLOW)
        self.assertIn(
            "> I approved the merges of #216 (the final-test pre-registration) and #224 (its amendment). "
            "The orchestrating session merged both on my instruction, given off GitHub, before the 2026 days were opened",
            WORKFLOW,
        )

    def test_market_colour_convention_is_written(self):
        self.assertIn("Market colour stays off repository threads", WORKFLOW)

    def test_ci_does_not_trigger_on_improvements(self):
        self.assertIsNone(re.search(r"branches:.*improvements", CI))


if __name__ == "__main__":
    unittest.main()
