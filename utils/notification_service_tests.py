import json
import os
import unittest

from utils.notification_service import Message


class TestErrorOut(unittest.TestCase):
    def setUp(self):
        if "OFFLINE_RUNNERS" in os.environ:
            del os.environ["OFFLINE_RUNNERS"]

    def test_error_out_no_offline_runners(self):
        try:
            Message.error_out("title")
        except Exception as e:
            self.fail(f"error_out raised {type(e)} unexpectedly!")

    def test_error_out_invalid_offline_runners(self):
        os.environ["OFFLINE_RUNNERS"] = "{invalid_json"
        try:
            Message.error_out("title")
        except Exception as e:
            self.fail(f"error_out raised {type(e)} unexpectedly!")

    def test_error_out_valid_offline_runners(self):
        os.environ["OFFLINE_RUNNERS"] = json.dumps(["runner1", "runner2"])
        try:
            Message.error_out("title")
        except Exception as e:
            self.fail(f"error_out raised {type(e)} unexpectedly!")

if __name__ == '__main__':
    unittest.main()
