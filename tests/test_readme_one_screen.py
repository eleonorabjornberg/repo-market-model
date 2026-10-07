"""The README is one screen (#344), and what it gave up is still published and still generated.

Eleonora's scope of 5 October 2026 on #120: the README's first screen is the question, the live site, the
status, the verdict and how to run it. The key findings, the tail clause and the plain-words headline moved to
`PROJECT_GUIDE.md`; the use limitation stayed, because it limits every claim on the page.

**Mutation, recorded.** The three blocks put back into `README.md` (the pre-#344 layout, replayed by moving the
`key-findings` block back by hand): `test_the_findings_are_not_on_the_front_door` raised `AssertionError`.
Unmutated control green before and after.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "PROJECT_GUIDE.md").read_text(encoding="utf-8")
MOVED = ("key-findings", "tail", "headline")


class ReadmeOneScreenTests(unittest.TestCase):

    def test_the_findings_are_not_on_the_front_door(self):
        for name in MOVED:
            self.assertNotIn("<!-- generated: %s -->" % name, README)
            self.assertIn("<!-- generated: %s -->" % name, GUIDE)

    def test_the_front_door_keeps_what_limits_and_orients(self):
        for name in ("status", "landing", "use-limitation"):
            self.assertIn("<!-- generated: %s -->" % name, README)
        self.assertIn("(https://eleonorabjornberg.github.io/repo-market-model/)", README)
        self.assertIn("## Quick start", README)

    def test_the_readme_is_short_and_links_the_guide(self):
        self.assertLessEqual(len(README.splitlines()), 90)
        self.assertIn("(PROJECT_GUIDE.md", README)

    def test_every_link_the_readme_makes_resolves(self):
        for text, name in ((README, "README.md"), (GUIDE, "PROJECT_GUIDE.md")):
            for target in re.findall(r"\]\(([^)\s#]+)(?:#[^)]*)?\)", text):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                self.assertTrue((ROOT / target).exists(), "%s links %s, which does not exist" % (name, target))

    def test_the_colab_badge_opens_a_notebook_that_is_tracked(self):
        match = re.search(r"colab\.research\.google\.com/github/[^/]+/[^/]+/blob/main/(\S+?\.ipynb)\)", README)
        self.assertIsNotNone(match)
        self.assertTrue((ROOT / match.group(1)).exists())


if __name__ == "__main__":
    unittest.main()
