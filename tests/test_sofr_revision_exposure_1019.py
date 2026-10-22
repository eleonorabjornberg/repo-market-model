"""#1019: exposure of the H5 labels to a SOFR revision, by revision size.

A revision of `m` basis points (the NY Fed revises only a change of more than one basis point, so m >= 2) moves a
day's spread by m. A day with whole-bp spread `s` is above `tau` when `s > tau`. Revised up from `s <= tau` it flips
when `s + m > tau`; revised down from `s > tau` it flips when `s - m <= tau`. So it can flip exactly when
`tau - m + 1 <= s <= tau + m`: for m = 2 that is the [tau - 1, tau + 2] window of #940, and it widens with m.

Recorded mutation (`return tau - size + 1, tau + size` -> `return tau - size + 1, tau + 2`): `test_window_widens_with_size`
raised AssertionError (Tuples differ: (-2, 2) != (-2, 3)).
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FlipWindowTests(unittest.TestCase):
    def setUp(self):
        self.script = _load("sofr_revision_exposure_1019")

    def test_two_bp_is_the_window_of_940(self):
        self.assertEqual(self.script.flip_window(5, 2), (4, 7))

    def test_window_widens_with_size(self):
        self.assertEqual(self.script.flip_window(0, 3), (-2, 3))
        self.assertEqual(self.script.flip_window(5, 5), (1, 10))
        self.assertEqual(self.script.flip_window(10, 10), (1, 20))

    def test_window_agrees_with_brute_force_label_flip(self):
        from repo_model.data import exceeds_bp

        for tau in (0, 5, 10):
            for m in (2, 3, 5, 10):
                lo, hi = self.script.flip_window(tau, m)
                for s in range(-40, 60):
                    flips = exceeds_bp(s + m, tau) != exceeds_bp(s, tau) or exceeds_bp(s - m, tau) != exceeds_bp(s, tau)
                    self.assertEqual(lo <= s <= hi, flips, (tau, m, s))

    def test_one_bp_revision_is_refused(self):
        with self.assertRaises(ValueError):
            self.script.flip_window(0, 1)

    def test_counts_are_nested_and_the_2bp_column_matches_940(self):
        result = self.script.build()
        original = _load("sofr_revisions_940").build()
        for key, cell in original["exposure"].items():
            self.assertEqual(result["exposure"][key]["by_size"]["2"], cell["days_within_reach_of_a_revision"])
            counts = [result["exposure"][key]["by_size"][str(m)] for m in (2, 3, 5, 10)]
            self.assertEqual(counts, sorted(counts))

    def test_committed_page_is_current(self):
        self.assertEqual(self.script.main(["--check"]), 0)

    def test_page_drops_upper_bound_wording(self):
        page = self.script.render(self.script.build())
        self.assertNotIn("is an upper bound", page)
        self.assertIn("days a 2 bp revision could flip", page)
        self.assertIn("sofr-revisions-940.md", page)


class OriginalPagePointerTests(unittest.TestCase):
    def test_original_page_points_to_the_correction(self):
        text = (ROOT / "docs" / "research" / "sofr-revisions-940.md").read_text(encoding="utf-8")
        self.assertIn("sofr-revision-exposure-1019-result.md", text)


if __name__ == "__main__":
    unittest.main()
