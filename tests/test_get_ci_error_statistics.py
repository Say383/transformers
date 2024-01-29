import json
import os
import unittest
from collections import Counter
from unittest.mock import MagicMock, patch

from utils.get_ci_error_statistics import (download_artifact, get_all_errors,
                                           get_artifacts_links,
                                           get_errors_from_single_artifact,
                                           get_job_links, get_model,
                                           make_github_table,
                                           make_github_table_per_model,
                                           reduce_by_error, reduce_by_model)


class TestGetCiErrorStatistics(unittest.TestCase):
    @patch("utils.get_ci_error_statistics.requests")
    def test_get_job_links(self, mock_requests):
        # Mock the API response
        mock_result = {
            "jobs": [
                {"name": "job1", "html_url": "https://example.com/job1"},
                {"name": "job2", "html_url": "https://example.com/job2"},
            ],
            "total_count": 2,
        }
        mock_requests.get.return_value.json.return_value = mock_result

        # Call the function
        workflow_run_id = "12345"
        token = "TOKEN"
        result = get_job_links(workflow_run_id, token)

        # Assert the result
        expected_result = {
            "job1": "https://example.com/job1",
            "job2": "https://example.com/job2",
        }
        self.assertEqual(result, expected_result)

        # Assert API call
        expected_url = "https://api.github.com/repos/huggingface/transformers/actions/runs/12345/jobs?per_page=100"
        expected_headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer TOKEN"}
        mock_requests.get.assert_called_once_with(expected_url, headers=expected_headers)

    @patch("utils.get_ci_error_statistics.requests")
    def test_get_artifacts_links(self, mock_requests):
        # Mock the API response
        mock_result = {
            "artifacts": [
                {"name": "artifact1", "archive_download_url": "https://example.com/artifact1.zip"},
                {"name": "artifact2", "archive_download_url": "https://example.com/artifact2.zip"},
            ],
            "total_count": 2,
        }
        mock_requests.get.return_value.json.return_value = mock_result

        # Call the function
        workflow_run_id = "12345"
        token = "TOKEN"
        result = get_artifacts_links(workflow_run_id, token)

        # Assert the result
        expected_result = {
            "artifact1": "https://example.com/artifact1.zip",
            "artifact2": "https://example.com/artifact2.zip",
        }
        self.assertEqual(result, expected_result)

        # Assert API call
        expected_url = "https://api.github.com/repos/huggingface/transformers/actions/runs/12345/artifacts?per_page=100"
        expected_headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer TOKEN"}
        mock_requests.get.assert_called_once_with(expected_url, headers=expected_headers)

    @patch("utils.get_ci_error_statistics.requests")
    def test_download_artifact(self, mock_requests):
        # Mock the API response
        mock_result = MagicMock()
        mock_result.headers = {"Location": "https://example.com/download"}
        mock_requests.get.return_value = mock_result
        mock_response = MagicMock()
        mock_response.content = b"artifact content"
        mock_requests.get.return_value.content = mock_response.content

        # Call the function
        artifact_name = "artifact1"
        artifact_url = "https://example.com/artifact1.zip"
        output_dir = "output"
        token = "TOKEN"
        download_artifact(artifact_name, artifact_url, output_dir, token)

        # Assert file is written
        expected_file_path = os.path.join(output_dir, "artifact1.zip")
        self.assertTrue(os.path.exists(expected_file_path))

        # Assert API calls
        expected_url = "https://example.com/artifact1.zip"
        expected_headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer TOKEN"}
        mock_requests.get.assert_called_with(artifact_url, headers=expected_headers, allow_redirects=False)
        mock_requests.get.assert_called_with(expected_url, allow_redirects=True)
        mock_response.write.assert_called_once_with(mock_response.content)

    def test_get_errors_from_single_artifact(self):
        # Create a mock zipfile
        mock_zipfile = MagicMock()
        mock_zipfile.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zipfile.open.side_effect = [
            MagicMock(readline=lambda: b"error_line: error\n"),
            MagicMock(readline=lambda: b"FAILED test1\n"),
            MagicMock(readline=lambda: b"job1\n"),
        ]

        # Call the function
        artifact_zip_path = "artifact.zip"
        job_links = {"job1": "https://example.com/job1"}
        result = get_errors_from_single_artifact(artifact_zip_path, job_links)

        # Assert the result
        expected_result = [["error_line", "error", "test1", "https://example.com/job1"]]
        self.assertEqual(result, expected_result)

        # Assert zipfile calls
        mock_zipfile.open.assert_any_call("failures_line.txt")
        mock_zipfile.open.assert_any_call("summary_short.txt")
        mock_zipfile.open.assert_any_call("job_name.txt")

    @patch("utils.get_ci_error_statistics.os")
    def test_get_all_errors(self, mock_os):
        # Mock the artifact directory
        mock_os.listdir.return_value = ["artifact1.zip", "artifact2.zip"]
        mock_os.path.join.side_effect = lambda dir, file: f"{dir}/{file}"
        mock_os.path.isdir.return_value = False

        # Mock the get_errors_from_single_artifact function
        mock_get_errors_from_single_artifact = MagicMock()
        mock_get_errors_from_single_artifact.side_effect = [
            [["error1", "error1", "test1", None]],
            [["error2", "error2", "test2", None]],
        ]

        # Call the function
        artifact_dir = "artifacts"
        job_links = {"job1": "https://example.com/job1"}
        result = get_all_errors(artifact_dir, job_links)

        # Assert the result
        expected_result = [["error1", "error1", "test1", None], ["error2", "error2", "test2", None]]
        self.assertEqual(result, expected_result)

        # Assert function calls
        mock_get_errors_from_single_artifact.assert_any_call("artifacts/artifact1.zip", job_links)
        mock_get_errors_from_single_artifact.assert_any_call("artifacts/artifact2.zip", job_links)

    def test_reduce_by_error(self):
        # Create a mock Counter
        mock_counter = MagicMock()
        mock_counter.most_common.return_value = [("error1", 2), ("error2", 1)]

        # Call the function
        logs = [["error1", "error1", "test1", None], ["error2", "error2", "test2", None]]
        result = reduce_by_error(logs, error_filter=["error1"])

        # Assert the result
        expected_result = {"error2": {"count": 1, "failed_tests": [("test2", "error2")]}}

        self.assertEqual(result, expected_result)

        # Assert Counter calls
        mock_counter.update.assert_called_once_with(["error1", "error2"])
        mock_counter.most_common.assert_called_once_with()

    def test_get_model(self):
        # Call the function
        test = "tests/models/test_model.py::TestModel::test_method"
        result = get_model(test)

        # Assert the result
        expected_result = "test_model"
        self.assertEqual(result, expected_result)

    def test_reduce_by_model(self):
        # Call the function
        logs = [["error1", "error1", "test1", None], ["error2", "error2", "test2", None]]
        result = reduce_by_model(logs, error_filter=["error1"])

        # Assert the result
        expected_result = {"test_model": {"count": 2, "errors": {"error1": 1, "error2": 1}}}

        self.assertEqual(result, expected_result)

    def test_make_github_table(self):
        # Call the function
        reduced_by_error = {"error1": {"count": 2}, "error2": {"count": 1}}
        result = make_github_table(reduced_by_error)

        # Assert the result
        expected_result = "| no. | error | status |\n|-:|:-|:-|\n| 2 | error1 |  |\n| 1 | error2 |  |"

        self.assertEqual(result, expected_result)

    def test_make_github_table_per_model(self):
        # Call the function
        reduced_by_model = {"test_model": {"count": 2, "errors": {"error1": 1, "error2": 1}}}
        result = make_github_table_per_model(reduced_by_model)

        # Assert the result
        expected_result = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n| test_model | 2 | error1 | 1 |"

        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
