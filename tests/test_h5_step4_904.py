"""The Mac run of #904 (H5 step 4 on two named panels): `scripts/h5_step4_904.py`.

The script only plans and checks. It runs `scripts/h5_step4_758.py` unchanged, once per panel, and builds each panel with
the chain of #903 at the commit that gives the digest Eleonora named (#904, ruling of 19 October 2026, option (c) on #900).
Three things are pinned here.

* Each panel is built at its own commit and its `DERIV.csv` is refused unless it has the ruled digest (`ValueError`).
* The walks are made once: they read the published and `AUG2D` panels, which are byte-identical at both commits, so the
  candidate rows are the same for both panels. Only the cross-fitted ceiling and the reachable line (`fit`) differ.
* Scoring keeps the declared tolerance (`metadata/h5_step4_758.json`, deviation 1) and edits no declaration.

No look-ahead, availability or staleness guard is added (the date guard is `h5_step4_758.refuse_after_last_day`), so no
mutation is recorded.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("h5_step4_904", ROOT / "scripts" / "h5_step4_904.py")
step = importlib.util.module_from_spec(_spec)
sys.modules["h5_step4_904"] = step
_spec.loader.exec_module(step)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.plan = step.plan(Path("w"))

    def names(self):
        return [item.name for item in self.plan]

    def test_the_two_panels_are_the_ruled_ones(self):
        self.assertEqual([panel.commit for panel in step.PANELS], ["ec534758", "71cf91d2"])
        self.assertEqual([panel.digest[:8] for panel in step.PANELS], ["1e5b748a", "69f22bc6"])

    def test_each_panel_is_built_at_its_own_commit(self):
        for panel in step.PANELS:
            item = next(i for i in self.plan if i.name == f"chain:{panel.name}")
            self.assertIn(panel.commit, item.argv)
            self.assertTrue(item.produces.name == "DERIV.csv")

    def test_the_walks_are_made_once_for_both_panels(self):
        walks = [i for i in self.plan if i.name.startswith("walk:")]
        self.assertEqual(len(walks), 10)
        self.assertEqual({(i.name.split(":")[1]) for i in walks}, {f"{v}_h{h}" for v in ("gbm_funding", "c_two_part_new") for h in range(1, 6)})
        for i in walks:
            self.assertIn("--panel", i.argv)
            self.assertTrue(any(a.endswith("AUG2D.csv") for a in i.argv))

    def test_each_panel_has_its_own_fit_and_score(self):
        for panel in step.PANELS:
            fit = next(i for i in self.plan if i.name == f"fit:{panel.name}")
            self.assertEqual(fit.argv[fit.argv.index("--panel") + 1], str(Path("w") / panel.name / "DERIV.csv"))
            score = next(i for i in self.plan if i.name == f"score:{panel.name}")
            self.assertEqual(score.argv[score.argv.index("--tolerance") + 1], "0.01")
            self.assertIn(str(Path("w") / panel.name / "fits.json"), score.argv)

    def test_the_order_puts_a_panel_before_its_fit_and_the_fit_before_its_score(self):
        order = self.names()
        for panel in step.PANELS:
            self.assertLess(order.index(f"chain:{panel.name}"), order.index(f"fit:{panel.name}"))
            self.assertLess(order.index(f"fit:{panel.name}"), order.index(f"score:{panel.name}"))
            self.assertLess(order.index("walk:gbm_funding_h1"), order.index(f"score:{panel.name}"))

    def test_no_step_touches_the_declaration_or_a_published_record(self):
        for item in self.plan:
            text = " ".join(item.argv)
            self.assertNotIn("docs/runs", text)
            self.assertNotIn("metadata/", text)


class VerifyTests(unittest.TestCase):
    def test_a_panel_with_another_digest_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "DERIV.csv"
            path.write_text("not the panel\n")
            with self.assertRaises(ValueError):
                step.verify_panel(step.PANELS[0], path)

    def test_a_panel_with_the_ruled_digest_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "DERIV.csv"
            path.write_text("x\n")
            panel = step.Panel("t", "abc", step.sha256(path))
            step.verify_panel(panel, path)


if __name__ == "__main__":
    unittest.main()
