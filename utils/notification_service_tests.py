import unittest
from unittest.mock import patch

from utils.notification_service import Message


class TestNotificationService(unittest.TestCase):

    @patch.dict('os.environ', {'OFFLINE_RUNNERS': None})
    def test_error_out_no_offline_runners(self):
        Message.error_out('Test Title')
        # Add assertions here to check the output

    @patch.dict('os.environ', {'OFFLINE_RUNNERS': ''})
    def test_error_out_empty_offline_runners(self):
        Message.error_out('Test Title')
        # Add assertions here to check the output

    @patch.dict('os.environ', {'OFFLINE_RUNNERS': '["runner1", "runner2"]'})
    def test_error_out_valid_offline_runners(self):
        Message.error_out('Test Title')
        # Add assertions here to check the output

if __name__ == '__main__':
    unittest.main()
