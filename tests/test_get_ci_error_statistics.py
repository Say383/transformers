import json
import os
import unittest
from collections import Counter
from io import StringIO
from unittest.mock import MagicMock, patch

from utils.get_ci_error_statistics import (download_artifact, get_all_errors,
                                           get_artifacts_links,
                                           get_errors_from_single_artifact,
                                           get_job_links, get_model,
                                           make_github_table,
                                           make_github_table_per_model,
                                           reduce_by_error, reduce_by_model)


class TestGetCiErrorStatistics(unittest.TestCase):
    @patch("utils.get_ci_error_statistics.requests.get")
    def test_get_job_links(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jobs": [
                {"name": "job1", "html_url": "https://example.com/job1"},
                {"name": "job2", "html_url": "https://example.com/job2"},
            ],
            "total_count": 2,
        }
        mock_get.return_value = mock_response

        # Call the function
        workflow_run_id = "12345"
        job_links = get_job_links(workflow_run_id)

        # Assert the result
        expected_job_links = {
            "job1": "https://example.com/job1",
            "job2": "https://example.com/job2",
        }
        self.assertEqual(job_links, expected_job_links)

    @patch("utils.get_ci_error_statistics.requests.get")
    def test_get_artifacts_links(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifacts": [
                {"name": "artifact1", "archive_download_url": "https://example.com/artifact1"},
                {"name": "artifact2", "archive_download_url": "https://example.com/artifact2"},
            ],
            "total_count": 2,
        }
        mock_get.return_value = mock_response

        # Call the function
        workflow_run_id = "12345"
        artifacts = get_artifacts_links(workflow_run_id)

        # Assert the result
        expected_artifacts = {
            "artifact1": "https://example.com/artifact1",
            "artifact2": "https://example.com/artifact2",
        }
        self.assertEqual(artifacts, expected_artifacts)

    @patch("utils.get_ci_error_statistics.requests.get")
    @patch("utils.get_ci_error_statistics.requests.head")
    @patch("utils.get_ci_error_statistics.open")
    def test_download_artifact(self, mock_open, mock_head, mock_get):
        # Mock the API response
        mock_head.return_value.headers = {"Location": "https://example.com/download"}
        mock_get.return_value.content = b"artifact content"

        # Call the function
        artifact_name = "artifact1"
        artifact_url = "https://example.com/artifact1"
        output_dir = "/path/to/output"
        token = "TOKEN"
        download_artifact(artifact_name, artifact_url, output_dir, token)

        # Assert the file is written with the correct content
        expected_file_path = os.path.join(output_dir, "artifact1.zip")
        mock_open.assert_called_once_with(expected_file_path, "wb")
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(b"artifact content")

    def test_get_errors_from_single_artifact(self):
        # Create a mock zipfile
        mock_zipfile = MagicMock()
        mock_zipfile.namelist.return_value = [
            "failures_line.txt",
            "summary_short.txt",
            "job_name.txt",
        ]
        mock_zipfile.open.side_effect = [
            StringIO("error_line: error message"),
            StringIO("FAILED test1\nFAILED test2"),
            StringIO("job1"),
        ]

        # Call the function
        artifact_zip_path = "/path/to/artifact.zip"
        job_links = {"job1": "https://example.com/job1"}
        errors = get_errors_from_single_artifact(artifact_zip_path, job_links)

        # Assert the result
        expected_errors = [
            ["error_line", "error message", "test1", "https://example.com/job1"],
            ["error_line", "error message", "test2", "https://example.com/job1"],
        ]
        self.assertEqual(errors, expected_errors)

    @patch("utils.get_ci_error_statistics.os.listdir")
    @patch("utils.get_ci_error_statistics.get_errors_from_single_artifact")
    def test_get_all_errors(self, mock_get_errors_from_single_artifact, mock_listdir):
        # Mock the listdir function to return artifact paths
        mock_listdir.return_value = ["artifact1.zip", "artifact2.zip"]

        # Mock the get_errors_from_single_artifact function
        mock_get_errors_from_single_artifact.side_effect = [
            [["error_line1", "error1", "test1", "https://example.com/job1"]],
            [["error_line2", "error2", "test2", "https://example.com/job2"]],
        ]

        # Call the function
        artifact_dir = "/path/to/artifacts"
        job_links = {"job1": "https://example.com/job1", "job2": "https://example.com/job2"}
        errors = get_all_errors(artifact_dir, job_links)

        # Assert the result
        expected_errors = [
            ["error_line1", "error1", "test1", "https://example.com/job1"],
            ["error_line2", "error2", "test2", "https://example.com/job2"],
        ]
        self.assertEqual(errors, expected_errors)

    def test_reduce_by_error(self):
        # Create a list of errors
        errors = [
            ["error1", "test1"],
            ["error2", "test2"],
            ["error1", "test3"],
        ]

        # Call the function
        reduced_errors = reduce_by_error(errors)

        # Assert the result
        expected_reduced_errors = {
            "error1": {"count": 2, "failed_tests": [("test1", "error1"), ("test3", "error1")]},
            "error2": {"count": 1, "failed_tests": [("test2", "error2")]},
        }
        self.assertEqual(reduced_errors, expected_reduced_errors)

    def test_get_model(self):
        # Test a test method with "tests/models/"
        test = "tests/models/test_model.py::test_method"
        model = get_model(test)
        self.assertEqual(model, "test_model")

        # Test a test method without "tests/models/"
        test = "test_model.py::test_method"
        model = get_model(test)
        self.assertIsNone(model)

    def test_reduce_by_model(self):
        # Create a list of errors with models
        errors = [
            ["error1", "test1", "model1"],
            ["error2", "test2", "model1"],
            ["error1", "test3", "model2"],
        ]

        # Call the function
        reduced_errors = reduce_by_model(errors)

        # Assert the result
        expected_reduced_errors = {
            "model1": {
                "count": 2,
                "errors": {"error1": 2, "error2": 1},
            },
            "model2": {
                "count": 1,
                "errors": {"error1": 1},
            },
        }
        self.assertEqual(reduced_errors, expected_reduced_errors)

    def test_make_github_table(self):
        # Create a reduced_by_error dictionary
        reduced_by_error = {
            "error1": {"count": 2, "failed_tests": [("test1", "error1"), ("test2", "error1")]},
            "error2": {"count": 1, "failed_tests": [("test3", "error2")]},
        }

        # Call the function
        table = make_github_table(reduced_by_error)

        # Assert the result
        expected_table = "| no. | error | status |\n|-:|:-|:-|\n| 2 | error1 |  |\n| 1 | error2 |  |\n"
        self.assertEqual(table, expected_table)

    def test_make_github_table_per_model(self):
        # Create a reduced_by_model dictionary
        reduced_by_model = {
            "model1": {
                "count": 2,
                "errors": {"error1": 2, "error2": 1},
            },
            "model2": {
                "count": 1,
                "errors": {"error1": 1},
            },
        }

        # Call the function
        table = make_github_table_per_model(reduced_by_model)

        # Assert the result
        expected_table = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n| model1 | 2 | error1 | 2 |\n| model2 | 1 | error1 | 1 |\n"
        self.assertEqual(table, expected_table)


if __name__ == "__main__":
    unittest.main()
