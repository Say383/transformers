import unittest
from os import os
from unittest import mock
from unittest.mock import MagicMock

from utils import get_ci_error_statistics


class TestGetCIErrorStatistics(unittest.TestCase):
    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_job_links(self, mock_get):
        # Mock the requests.get function
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jobs": [
                {"name": "job1", "html_url": "https://example.com/job1"},
                {"name": "job2", "html_url": "https://example.com/job2"},
            ],
            "total_count": 2,
        }
        mock_get.return_value = mock_response

        # Test with valid workflow run ID
        job_links = get_ci_error_statistics.get_job_links("workflow_run_id")
        self.assertEqual(job_links, {"job1": "https://example.com/job1", "job2": "https://example.com/job2"})

        # Test with invalid workflow run ID
        job_links = get_ci_error_statistics.get_job_links("invalid_workflow_run_id")
        self.assertEqual(job_links, {})

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_artifacts_links(self, mock_get):
        # Mock the requests.get function
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifacts": [
                {"name": "artifact1", "archive_download_url": "https://example.com/artifact1.zip"},
                {"name": "artifact2", "archive_download_url": "https://example.com/artifact2.zip"},
            ],
            "total_count": 2,
        }
        mock_get.return_value = mock_response

        # Test with valid workflow run ID
        artifacts = get_ci_error_statistics.get_artifacts_links("workflow_run_id")
        self.assertEqual(
            artifacts,
            {"artifact1": "https://example.com/artifact1.zip", "artifact2": "https://example.com/artifact2.zip"},
        )

        # Test with invalid workflow run ID
        artifacts = get_ci_error_statistics.get_artifacts_links("invalid_workflow_run_id")
        self.assertEqual(artifacts, {})

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_download_artifact(self, mock_get):
        # Mock the requests.get function
        mock_response = MagicMock()
        mock_response.headers = {"Location": "https://example.com/download"}
        mock_get.return_value = mock_response

        # Test with valid artifact URL, output directory, and token
        get_ci_error_statistics.download_artifact(
            "artifact1", "https://example.com/artifact1.zip", "output_dir", "token"
        )
        # Assert that the artifact is downloaded correctly

    def test_get_errors_from_single_artifact(self):
        # Create a mock artifact zip file with predefined contents
        artifact_zip_path = "mock_artifact.zip"
        with open(artifact_zip_path, "wb") as f:
            f.write(b"failures_line.txt\nsummary_short.txt\njob_name.txt")

        job_links = {"job1": "https://example.com/job1"}

        # Test with the mock artifact zip file and job links
        errors = get_ci_error_statistics.get_errors_from_single_artifact(artifact_zip_path, job_links=job_links)
        self.assertEqual(errors, [["failures_line.txt", "error1", "test1", "https://example.com/job1"]])

    def test_get_all_errors(self):
        # Create mock artifact zip files with predefined contents
        artifact_dir = "mock_artifacts"
        os.makedirs(artifact_dir, exist_ok=True)
        artifact_zip_path1 = os.path.join(artifact_dir, "artifact1.zip")
        artifact_zip_path2 = os.path.join(artifact_dir, "artifact2.zip")

        with open(artifact_zip_path1, "wb") as f:
            f.write(b"failures_line.txt\nsummary_short.txt\njob_name.txt")
        with open(artifact_zip_path2, "wb") as f:
            f.write(b"failures_line.txt\nsummary_short.txt\njob_name.txt")

        job_links = {"job1": "https://example.com/job1"}

        # Test with the mock artifact directory and job links
        errors = get_ci_error_statistics.get_all_errors(artifact_dir, job_links=job_links)
        self.assertEqual(errors, [["failures_line.txt", "error1", "test1", "https://example.com/job1"]])

    def test_reduce_by_error(self):
        # Test with a predefined list of errors
        logs = [["failures_line.txt", "error1", "test1"], ["failures_line.txt", "error2", "test2"]]
        reduced_errors = get_ci_error_statistics.reduce_by_error(logs)
        self.assertEqual(
            reduced_errors,
            {
                "error1": {"count": 1, "failed_tests": [("test1", "failures_line.txt")]},
                "error2": {"count": 1, "failed_tests": [("test2", "failures_line.txt")]},
            },
        )

    def test_get_model(self):
        # Test with different test names
        test1 = "tests/models/test_model1.py::test_method1"
        test2 = "tests/models/test_model2.py::test_method2"

        model1 = get_ci_error_statistics.get_model(test1)
        model2 = get_ci_error_statistics.get_model(test2)

        self.assertEqual(model1, "model1")
        self.assertEqual(model2, "model2")

    def test_reduce_by_model(self):
        # Test with a predefined list of errors and models
        logs = [
            ["failures_line.txt", "error1", "test1", "model1"],
            ["failures_line.txt", "error2", "test2", "model2"],
        ]
        reduced_errors_per_model = get_ci_error_statistics.reduce_by_model(logs)
        self.assertEqual(
            reduced_errors_per_model,
            {
                "model1": {"count": 1, "errors": {"error1": 1}},
                "model2": {"count": 1, "errors": {"error2": 1}},
            },
        )

    def test_make_github_table(self):
        # Test with a predefined dictionary of reduced errors
        reduced_errors = {
            "error1": {"count": 1, "failed_tests": [("test1", "failures_line.txt")]},
            "error2": {"count": 1, "failed_tests": [("test2", "failures_line.txt")]},
        }
        github_table = get_ci_error_statistics.make_github_table(reduced_errors)
        expected_table = "| no. | error | status |\n|-:|:-|:-|\n| 1 | error1 |  |\n| 1 | error2 |  |\n"
        self.assertEqual(github_table, expected_table)

    def test_make_github_table_per_model(self):
        # Test with a predefined dictionary of reduced errors per model
        reduced_errors_per_model = {
            "model1": {"count": 1, "errors": {"error1": 1}},
            "model2": {"count": 1, "errors": {"error2": 1}},
        }
        github_table_per_model = get_ci_error_statistics.make_github_table_per_model(reduced_errors_per_model)
        expected_table_per_model = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n| model1 | 1 | error1 | 1 |\n| model2 | 1 | error2 | 1 |\n"
        self.assertEqual(github_table_per_model, expected_table_per_model)


if __name__ == "__main__":
    unittest.main()
