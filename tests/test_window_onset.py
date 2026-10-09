"""The five-day-window onset declaration (#460) agrees with the judge's and with its script."""

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "window_onset.json").read_text())
JUDGE = pj.load_declaration()


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("window_onset_script", ROOT / "scripts" / "window_onset.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WindowOnsetDeclarationTests(unittest.TestCase):
    def test_every_candidate_is_declared_to_the_judge_in_its_judged_form(self):
        for name, spec in DECLARED["candidates"].items():
            entry = JUDGE.candidates[name + DECLARED["judged_form"]]
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(entry["track"], "W (#460)")
            self.assertEqual(sorted(entry["features"]), sorted(DECLARED["features"][spec["features"]]))

    def test_the_window_is_the_judges_week_ahead_window_and_ends_before_the_lockbox(self):
        self.assertEqual(DECLARED["target"]["window_days"], JUDGE.week_days)
        self.assertEqual(JUDGE.week_combine, "max")
        self.assertEqual(DECLARED["scoring"]["last_day"], JUDGE.last_day.isoformat())
        self.assertEqual(DECLARED["horizons"], list(JUDGE.horizons))
        self.assertEqual(DECLARED["thresholds_bp"], [float(t) if t % 1 else int(t) for t in JUDGE.thresholds])

    def test_the_candidates_are_not_in_the_confirmation_look(self):
        for name in DECLARED["candidates"]:
            self.assertNotIn(name + DECLARED["judged_form"], JUDGE.confirmation_candidates)


class HorizonFilesTests(unittest.TestCase):
    """The five horizon files give each decision day's probability to each of the five days it covers."""

    def test_the_week_ahead_maximum_over_the_files_is_the_window_probability(self):
        script = _script()
        calendar = [date(2024, 1, 1) + timedelta(days=k) for k in range(12)]
        scored = tuple(calendar[1:9])
        report = SimpleNamespace(
            taus=(5.0,), scored_dates=scored, forecast=tuple((0.1 * (k + 1),) for k in range(len(scored)))
        )
        last = calendar[-1]
        files = {h: script.by_horizon(report, calendar, last, h)["5"] for h in range(1, 6)}
        for k, when in enumerate(scored):
            decision = k  # calendar index of the decision day = index of the scored day - 1
            values = [
                files[h][calendar[decision + h].isoformat()] for h in range(1, 6) if decision + h < len(calendar)
            ]
            self.assertEqual(set(values), {0.1 * (k + 1)})


if __name__ == "__main__":
    unittest.main()
