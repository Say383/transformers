import unittest
from os import os
from unittest.mock import patch

from utils.check_self_hosted_runner import get_runner_status


class TestGetRunnerStatus(unittest.TestCase):
    @patch.dict(os.environ, {"TOKEN": ""})
    def test_get_runner_status_no_token(self):
        with self.assertRaises(ValueError) as context:
            get_runner_status(["runner1", "runner2"], "")
        self.assertTrue("A token that has actions:read permission." in str(context.exception))

    @patch.dict(os.environ, {"TOKEN": "sample_token"})
    def test_get_runner_status_with_token(self):
        try:
            get_runner_status(["runner1", "runner2"], "sample_token")
        except Exception as e:
            self.fail(f"get_runner_status() raised {type(e).__name__} unexpectedly!")

if __name__ == "__main__":
    unittest.main()
