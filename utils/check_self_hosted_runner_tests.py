import unittest
from unittest.mock import MagicMock, mock_open, patch

from utils.check_self_hosted_runner import get_runner_status


class TestCheckSelfHostedRunner(unittest.TestCase):

    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_runner_status_no_target_runners(self, mock_open, mock_run):
        mock_run.return_value.stdout.decode.return_value = '{}'
        get_runner_status(None, 'token')
        mock_open.assert_called_once_with('offline_runners.txt', 'w')

    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_runner_status_empty_target_runners(self, mock_open, mock_run):
        mock_run.return_value.stdout.decode.return_value = '{}'
        get_runner_status([], 'token')
        mock_open.assert_called_once_with('offline_runners.txt', 'w')

    @patch('sys.exit')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_no_token(self, mock_args, mock_exit):
        mock_args.return_value = MagicMock(token=None)
        with self.assertRaises(SystemExit):
            if __name__ == "__main__":
                mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
