import unittest
from unittest import mock
from unittest.mock import MagicMock

from utils import get_ci_error_statistics


class TestGetCIErrorStatistics(unittest.TestCase):
    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_job_links(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jobs": [
                {"name": "job1", "html_url": "https://example.com/job1"},
                {"name": "job2", "html_url": "https://example.com/job2"},
            ]
        }
        mock_get.return_value = mock_response

        # Call the function
        job_links = get_ci_error_statistics.get_job_links("workflow_run_id", token="token")

        # Check the expected job links
        expected_job_links = {"job1": "https://example.com/job1", "job2": "https://example.com/job2"}
        self.assertEqual(job_links, expected_job_links)

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_artifacts_links(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifacts": [
                {"name": "artifact1", "archive_download_url": "https://example.com/artifact1.zip"},
                {"name": "artifact2", "archive_download_url": "https://example.com/artifact2.zip"},
            ]
        }
        mock_get.return_value = mock_response

        # Call the function
        artifacts = get_ci_error_statistics.get_artifacts_links("workflow_run_id", token="token")

        # Check the expected artifact links
        expected_artifacts = {
            "artifact1": "https://example.com/artifact1.zip",
            "artifact2": "https://example.com/artifact2.zip",
        }
        self.assertEqual(artifacts, expected_artifacts)

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_download_artifact(self, mock_get, mock_open):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.headers = {"Location": "https://example.com/download"}
        mock_get.return_value = mock_response

        # Mock the open function
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call the function
        get_ci_error_statistics.download_artifact("artifact1", "https://example.com/artifact1.zip", "output_dir", "token")

        # Check that the file is written correctly
        mock_file.write.assert_called_once_with(mock_response.content)

    def test_get_errors_from_single_artifact(self):
        # Create a mock artifact zip file
        mock_zip = MagicMock()
        mock_zip.__enter__.return_value = mock_zip
        mock_zip.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zip.open.side_effect = [
            MagicMock(readline=lambda: b"1: error1\n"),
            MagicMock(readline=lambda: b"FAILED test1\n"),
            MagicMock(readline=lambda: b"job1\n"),
        ]

        # Call the function
        errors = get_ci_error_statistics.get_errors_from_single_artifact("artifact.zip", job_links={"job1": "https://example.com/job1"})

        # Check the expected errors
        expected_errors = [["1", "error1", "test1", "https://example.com/job1"]]
        self.assertEqual(errors, expected_errors)

    def test_get_all_errors(self):
        # Create mock artifact zip files
        mock_zip1 = MagicMock()
        mock_zip1.__enter__.return_value = mock_zip1
        mock_zip1.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zip1.open.side_effect = [
            MagicMock(readline=lambda: b"1: error1\n"),
            MagicMock(readline=lambda: b"FAILED test1\n"),
            MagicMock(readline=lambda: b"job1\n"),
        ]

        mock_zip2 = MagicMock()
        mock_zip2.__enter__.return_value = mock_zip2
        mock_zip2.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zip2.open.side_effect = [
            MagicMock(readline=lambda: b"2: error2\n"),
            MagicMock(readline=lambda: b"FAILED test2\n"),
            MagicMock(readline=lambda: b"job2\n"),
        ]

        # Call the function
        errors = get_ci_error_statistics.get_all_errors("artifact_dir", job_links={"job1": "https://example.com/job1", "job2": "https://example.com/job2"})

        # Check the expected errors
        expected_errors = [
            ["1", "error1", "test1", "https://example.com/job1"],
            ["2", "error2", "test2", "https://example.com/job2"],
        ]
        self.assertEqual(errors, expected_errors)

    def test_reduce_by_error(self):
        # Create a list of errors
        errors = [
            ["1", "error1", "test1", "https://example.com/job1"],
            ["2", "error2", "test2", "https://example.com/job2"],
            ["3", "error1", "test3", "https://example.com/job3"],
        ]

        # Call the function
        reduced_errors = get_ci_error_statistics.reduce_by_error(errors)

        # Check the expected reduced errors
        expected_reduced_errors = {
            "error1": {"count": 2, "failed_tests": [("test1", "https://example.com/job1"), ("test3", "https://example.com/job3")]},
            "error2": {"count": 1, "failed_tests": [("test2", "https://example.com/job2")]},
        }
        self.assertEqual(reduced_errors, expected_reduced_errors)

    def test_reduce_by_model(self):
        # Create a list of errors with models
        errors = [
            ["1", "error1", "test1", "https://example.com/job1"],
            ["2", "error2", "test2", "https://example.com/job2"],
            ["3", "error1", "test3", "https://example.com/job3"],
        ]

        # Call the function
        reduced_errors = get_ci_error_statistics.reduce_by_model(errors)

        # Check the expected reduced errors
        expected_reduced_errors = {
            "model1": {"count": 2, "errors": {"error1": 2}},
            "model2": {"count": 1, "errors": {"error2": 1}},
        }
        self.assertEqual(reduced_errors, expected_reduced_errors)

    def test_make_github_table(self):
        # Create a dictionary of errors with counts
        errors = {
            "error1": {"count": 2, "failed_tests": [("test1", "https://example.com/job1"), ("test3", "https://example.com/job3")]},
            "error2": {"count": 1, "failed_tests": [("test2", "https://example.com/job2")]},
        }

        # Call the function
        table = get_ci_error_statistics.make_github_table(errors)

        # Check the expected GitHub table
        expected_table = "| no. | error | status |\n|-:|:-|:-|\n| 2 | error1 |  |\n| 1 | error2 |  |\n"
        self.assertEqual(table, expected_table)

    def test_make_github_table_per_model(self):
        # Create a dictionary of errors with counts per model
        errors = {
            "model1": {"count": 2, "errors": {"error1": 2}},
            "model2": {"count": 1, "errors": {"error2": 1}},
        }

        # Call the function
        table = get_ci_error_statistics.make_github_table_per_model(errors)

        # Check the expected GitHub table per model
        expected_table = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n| model1 | 2 | error1 | 2 |\n| model2 | 1 | error2 | 1 |\n"
        self.assertEqual(table, expected_table)


if __name__ == "__main__":
    unittest.main()
