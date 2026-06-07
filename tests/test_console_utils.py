import unittest

import console_utils


class ConsoleModeTests(unittest.TestCase):
    def test_without_quick_edit_clears_quick_edit_and_keeps_other_flags(self):
        existing_flag = 0x0008
        mode = console_utils.ENABLE_QUICK_EDIT_MODE | existing_flag

        result = console_utils.without_quick_edit(mode)

        self.assertEqual(0, result & console_utils.ENABLE_QUICK_EDIT_MODE)
        self.assertEqual(console_utils.ENABLE_EXTENDED_FLAGS, result & console_utils.ENABLE_EXTENDED_FLAGS)
        self.assertEqual(existing_flag, result & existing_flag)


if __name__ == "__main__":
    unittest.main()
