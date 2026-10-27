"""H1 infrastructure (#1090, finding #1088): the pooled workers of the design and power studies run under `spawn`.

macOS starts pool workers by `spawn`: a child unpickles a function by importing its module by name. A worker defined in
a script that was loaded by path (`confirmation_design_for_886`, `scaled_score_967`) has no importable name there, so
every pooled job failed with `ModuleNotFoundError`. These tests run the pooled paths in a `spawn` context, with
`scripts/` off `sys.path`, as the Mac does, and compare each to the serial result.

Failing first, on main: all four tests raised `multiprocessing.TimeoutError` in the parent, while each spawn child died
on unpickle with `ModuleNotFoundError: No module named 'confirmation_design_for_886'` (the three postcovid_886 design-path
tests) or `'scaled_score_967'` (scaled_score_1013's pool). After the move the workers live in
`repo_model.confirmation_workers` and `repo_model.scaled_score_workers`, which a child imports by name.
"""

import importlib.util
import json
import multiprocessing
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = str(ROOT / "scripts")


def load(name, as_name=None):
    spec = importlib.util.spec_from_file_location(as_name or name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[as_name or name] = module
    spec.loader.exec_module(module)
    return module


def history(seed=3, n=420):
    rng = random.Random(seed)
    dates = [date(2020, 1, 1) + timedelta(days=i) for i in range(n)]
    b = [1.0 + rng.random() * rng.random() for _ in range(n)]
    e = [0.05 * x + rng.gauss(0.0, 0.3) for x in b]
    return dates, b, e


class OffScripts:
    """`scripts/` is not on the path: a spawn child on the Mac finds only what is installed."""

    def __enter__(self):
        self.saved = list(sys.path)
        sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != Path(SCRIPTS)]
        return self

    def __exit__(self, *exc):
        sys.path[:] = self.saved


def spawn_pool(processes=2, **kwargs):
    return multiprocessing.get_context("spawn").Pool(processes, **kwargs)


def run(pool, function, jobs):
    """`pool.map` that cannot hang: a child that cannot unpickle the function dies and the pool waits for it forever."""

    return pool.map_async(function, jobs).get(timeout=60)


class TestPostcovid886DesignPathUnderSpawn(unittest.TestCase):
    def test_the_design_values_job_runs_in_a_spawn_pool_and_equals_the_serial_value(self):
        pc = load("postcovid_886", "postcovid_886_spawn")
        cd = pc.load_script("confirmation_design_for_886", "confirmation_design.py")
        dates, b, e = history()
        series = cd.Series(dates, b, e, dates, e)
        design = cd.Design("T", 60, (1, 2), False)
        jobs = [(design, series, 3000)] * 2
        serial = [pc.design_values(job) for job in jobs]
        with OffScripts(), spawn_pool() as pool:
            pooled = run(pool, pc.design_values, jobs)
        self.assertEqual(json.dumps(pooled, sort_keys=True), json.dumps(serial, sort_keys=True))

    def test_the_path_workers_run_in_a_spawn_pool_with_their_initializer(self):
        pc = load("postcovid_886", "postcovid_886_spawn")
        cd = pc.load_script("confirmation_design_for_886", "confirmation_design.py")
        dates, b, e = history()
        series = cd.Series(dates, b, e, dates, e)
        design = cd.Design("T", 60, (1, 2), False)
        histories = {("T", h): cd.history_slice(series, h) for h in ("full", "post-2020")}
        critical = {"T": {str(n): 1.0 for n in design.checkpoints[1:]}}
        jobs = [(design, h, 0.05, 1.0, seed) for seed in range(12) for h in ("full", "post-2020")]
        cd.init_worker(histories, critical)
        serial = [cd.run_path(job) for job in jobs]
        with OffScripts(), spawn_pool(initializer=cd.init_worker, initargs=(histories, critical)) as pool:
            pooled = run(pool, cd.run_path, jobs)
        self.assertEqual(pooled, serial)

    def test_the_calibration_job_runs_in_a_spawn_pool(self):
        pc = load("postcovid_886", "postcovid_886_spawn")
        cd = pc.load_script("confirmation_design_for_886", "confirmation_design.py")
        dates, b, e = history()
        series = cd.Series(dates, b, e, dates, e)
        design = cd.Design("T", 60, (1, 2), False)
        job = (design, series, 3000)
        with OffScripts(), spawn_pool() as pool:
            pooled = run(pool, cd.calibrate_design, [job])
        self.assertEqual(json.dumps(pooled[0], sort_keys=True), json.dumps(cd.calibrate_design(job), sort_keys=True))


class TestScaledScore1013PoolUnderSpawn(unittest.TestCase):
    def test_calibration_and_path_workers_run_with_scripts_off_the_path(self):
        script = load("scaled_score_1013")
        base = script.base
        dates, b, e = history()
        design = base.Design("T", 60, (1, 2), "raw")
        jobs = [(design, e, 3000), (design, e, 3000, -1.0)]
        serial = [base.calibrate(job) for job in jobs]
        with OffScripts(), spawn_pool() as pool:
            pooled = run(pool, base.calibrate, jobs)
        self.assertEqual(json.dumps(pooled, sort_keys=True), json.dumps(serial, sort_keys=True))
        critical = {"T": serial[0][1]["critical"]}
        paths = [(design, 0.05, seed, generator) for seed in range(12) for generator in ("stationary", "circular")]
        base._init({"T": (b, e)}, critical)
        expected = [base.run_path(job) for job in paths]
        with OffScripts(), spawn_pool(initializer=base._init, initargs=({"T": (b, e)}, critical)) as pool:
            self.assertEqual(run(pool, base.run_path, paths), expected)


if __name__ == "__main__":
    unittest.main()
