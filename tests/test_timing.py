import unittest

import run as runner


class SleepUntilTests(unittest.TestCase):
    def test_sleep_until_uses_sleep_for_remaining_interval(self):
        calls = []

        result = runner.sleep_until(10.0, now=lambda: 9.75, sleep=calls.append)

        self.assertEqual([0.25], calls)
        self.assertEqual(10.0, result)

    def test_sleep_until_does_not_sleep_when_behind_schedule(self):
        calls = []

        result = runner.sleep_until(10.0, now=lambda: 10.25, sleep=calls.append)

        self.assertEqual([], calls)
        self.assertEqual(10.25, result)


if __name__ == "__main__":
    unittest.main()
