import os
import unittest
from unittest.mock import patch

from src.fortnite_api import fetch_progress


class TestFortniteApi(unittest.TestCase):
    def test_fetch_progress_returns_sample_without_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            result = fetch_progress("TestPlayer", "psn")
            self.assertEqual(result["display_name"], "TestPlayer")
            self.assertEqual(result["platform"], "psn")
            self.assertIn("sprite_progress", result)
            self.assertEqual(result["source"], "sample")

    def test_fetch_progress_defaults_invalid_platform_to_pc(self):
        with patch.dict(os.environ, {}, clear=True):
            result = fetch_progress("AnotherPlayer", "wrong")
            self.assertEqual(result["platform"], "pc")
            self.assertEqual(result["source"], "sample")


if __name__ == "__main__":
    unittest.main()
