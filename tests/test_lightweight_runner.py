import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

import run as runner


class LightweightRunnerTests(unittest.TestCase):
    def test_prepare_route_points_can_skip_randomization(self):
        loc = [{"lat": 1.0, "lng": 2.0}]

        with mock.patch.object(runner, "fixLockT", return_value=loc) as fix_lock_t:
            with mock.patch.object(runner, "randLoc") as rand_loc:
                with mock.patch.object(runner, "bd09Towgs84", side_effect=lambda point: point.copy()):
                    result = runner.prepare_route_points(loc, 3.2, 0.5, randomize=False)

        self.assertEqual(loc, result)
        fix_lock_t.assert_called_once_with(loc, 3.2, 0.5)
        rand_loc.assert_not_called()

    def test_run_prepared_lap_skips_nearby_points_but_keeps_timing(self):
        points = [
            {"lat": 0.0, "lng": 0.0},
            {"lat": 0.0, "lng": 0.000001},
            {"lat": 0.0, "lng": 0.0001},
        ]
        sent = []
        slept = []

        runner.run_prepared_lap(
            object(),
            points,
            dt=1.0,
            min_distance=5.0,
            set_location=lambda _simulation, **point: sent.append(point),
            now=lambda: 0.0,
            sleep=slept.append,
        )

        self.assertEqual([points[0], points[2]], sent)
        self.assertEqual([1.0, 2.0, 3.0], slept)

    def test_run_can_reuse_cached_route_points(self):
        loc = [{"lat": 1.0, "lng": 2.0}]
        points = [{"lat": 3.0, "lng": 4.0}]
        calls = []

        def stop_after_two_laps(_simulation, prepared_points, **_kwargs):
            calls.append(prepared_points)
            if len(calls) == 2:
                raise KeyboardInterrupt

        with mock.patch.object(runner, "prepare_route_points", return_value=points) as prepare:
            with redirect_stdout(StringIO()):
                with self.assertRaises(KeyboardInterrupt):
                    runner.run(
                        object(),
                        loc,
                        3.2,
                        dt=0.5,
                        speed_variation=0.0,
                        randomize=False,
                        cache_route=True,
                        run_lap=stop_after_two_laps,
                    )

        prepare.assert_called_once_with(loc, 3.2, 0.5, False)
        self.assertEqual([points, points], calls)


if __name__ == "__main__":
    unittest.main()
