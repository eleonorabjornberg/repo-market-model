"""`scripts/pre_review.py` runs the checks CI runs (`.github/workflows/`), by the same command lines."""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("pre_review", ROOT / "scripts" / "pre_review.py")
pre_review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pre_review)


class PreReviewTests(unittest.TestCase):
    def test_every_check_is_one_ci_runs(self):
        workflows = "".join(path.read_text() for path in (ROOT / ".github" / "workflows").glob("*.yml"))
        ran = {" ".join(line.split()) for line in re.findall(r"python3 (?:-B )?(scripts/\S+\.py[^\n$]*)", workflows)}
        for command in pre_review.commands():
            self.assertIn(" ".join(command[2:]), ran)

    def test_the_base_adds_the_two_base_relative_checks(self):
        without = pre_review.commands()
        with_base = pre_review.commands("origin/main")
        self.assertEqual(with_base[:len(without)], without)
        self.assertEqual([c[2:] for c in with_base[len(without):]],
                         [["scripts/check_research_log.py", "check", "--base", "origin/main"],
                          ["scripts/check_built_outputs.py", "--base", "origin/main"]])


if __name__ == "__main__":
    unittest.main()
