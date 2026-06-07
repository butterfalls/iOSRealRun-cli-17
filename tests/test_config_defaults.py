import unittest

from config import Config


class ConfigDefaultsTests(unittest.TestCase):
    def test_lightweight_options_have_defaults(self):
        config = Config({})

        self.assertEqual(0.5, config.locationUpdateInterval)
        self.assertEqual(1.0, config.minLocationDistance)
        self.assertFalse(config.randomizeRoute)
        self.assertTrue(config.cacheRoute)
        self.assertEqual(0.0, config.speedVariation)
        self.assertTrue(config.lowPriority)


if __name__ == "__main__":
    unittest.main()
