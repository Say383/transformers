import unittest
from unittest.mock import MagicMock, patch

from utils.get_ci_error_statistics import (download_artifact, get_all_errors,
                                           get_artifacts_links,
                                           get_errors_from_single_artifact,
                                           get_job_links, get_model,
                                           make_github_table,
                                           make_github_table_per_model,
                                           reduce_by_error, reduce_by_model)


class TestGetCIErrorStatistics(unittest.TestCase):
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
        job_links = get_job_links("workflow_run_id")

        # Assert the returned job links
        expected_job_links = {"job1": "https://example.com/job1", "job2": "https://example.com/job2"}
        self.assertEqual(job_links, expected_job_links)

    @patch("utils.get_ci_error_statistics.requests.get")
    def test_get_artifacts_links(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifacts": [
                {"name": "artifact1", "archive_download_url": "https://example.com/artifact1.zip"},
                {"name": "artifact2", "archive_download_url": "https://example.com/artifact2.zip"},
            ],
            "total_count": 2,
        }
        mock_get.return_value = mock_response

        # Call the function
        artifacts = get_artifacts_links("workflow_run_id")

        # Assert the returned artifact links
        expected_artifacts = {
            "artifact1": "https://example.com/artifact1.zip",
            "artifact2": "https://example.com/artifact2.zip",
        }
        self.assertEqual(artifacts, expected_artifacts)

    @patch("utils.get_ci_error_statistics.requests.get")
    @patch("utils.get_ci_error_statistics.requests.get")
    def test_download_artifact(self, mock_get_redirect, mock_get_download):
        # Mock the API responses
        mock_redirect_response = MagicMock()
        mock_redirect_response.headers = {"Location": "https://example.com/download"}
        mock_get_redirect.return_value = mock_redirect_response

        mock_download_response = MagicMock()
        mock_download_response.content = b"Artifact content"
        mock_get_download.return_value = mock_download_response

        # Call the function
        download_artifact("artifact1", "https://example.com/artifact1.zip", "output_dir", "token")

        # Assert that the artifact is downloaded correctly
        expected_file_path = "output_dir/artifact1.zip"
        with open(expected_file_path, "rb") as f:
            self.assertEqual(f.read(), b"Artifact content")

    def test_get_errors_from_single_artifact(self):
        # Create a mock artifact zip file
        mock_zip_file = MagicMock()
        mock_zip_file.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zip_file.open.side_effect = [
            MagicMock(readline=MagicMock(return_value="error_line: error1\n")),
            MagicMock(readline=MagicMock(return_value="FAILED test1\n")),
            MagicMock(readline=MagicMock(return_value="job1\n")),
        ]

        with patch("utils.get_ci_error_statistics.zipfile.ZipFile", return_value=mock_zip_file):
            # Call the function
            errors = get_errors_from_single_artifact("artifact_zip_path")

            # Assert the extracted errors
            expected_errors = [["error_line", "error1", "test1", "https://example.com/job1"]]
            self.assertEqual(errors, expected_errors)

    def test_get_all_errors(self):
        # Create mock artifact zip files
        mock_zip_file1 = MagicMock()
        mock_zip_file1.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zip_file1.open.side_effect = [
            MagicMock(readline=MagicMock(return_value="error_line: error1\n")),
            MagicMock(readline=MagicMock(return_value="FAILED test1\n")),
            MagicMock(readline=MagicMock(return_value="job1\n")),
        ]

        mock_zip_file2 = MagicMock()
        mock_zip_file2.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zip_file2.open.side_effect = [
            MagicMock(readline=MagicMock(return_value="error_line: error2\n")),
            MagicMock(readline=MagicMock(return_value="FAILED test2\n")),
            MagicMock(readline=MagicMock(return_value="job2\n")),
        ]

        with patch("utils.get_ci_error_statistics.zipfile.ZipFile") as mock_zip:
            mock_zip.side_effect = [mock_zip_file1, mock_zip_file2]

            # Call the function
            errors = get_all_errors("artifact_dir")

            # Assert the extracted errors
            expected_errors = [
                ["error_line", "error1", "test1", "https://example.com/job1"],
                ["error_line", "error2", "test2", "https://example.com/job2"],
            ]
            self.assertEqual(errors, expected_errors)

    def test_reduce_by_error(self):
        # Create a mock list of errors
        mock_errors = [
            ["error1_line", "error1", "test1", "https://example.com/job1"],
            ["error2_line", "error2", "test2", "https://example.com/job2"],
            ["error1_line", "error1", "test3", "https://example.com/job3"],
        ]

        # Call the function
        reduced_errors = reduce_by_error(mock_errors)

        # Assert the reduced errors
        expected_reduced_errors = {
            "error1": {
                "count": 2,
                "failed_tests": [("test1", "https://example.com/job1"), ("test3", "https://example.com/job3")],
            },
            "error2": {"count": 1, "failed_tests": [("test2", "https://example.com/job2")]},
        }
        self.assertEqual(reduced_errors, expected_reduced_errors)

    def test_get_model(self):
        # Call the function with different test cases
        model1 = get_model("tests/models/model1/test1")
        model2 = get_model("tests/models/model2/test2")
        model3 = get_model("other/test3")

        # Assert the returned model names
        self.assertEqual(model1, "model1")
        self.assertEqual(model2, "model2")
        self.assertIsNone(model3)

    def test_reduce_by_model(self):
        # Create a mock list of errors
        mock_errors = [
            ["error1_line", "error1", "test1", "https://example.com/job1"],
            ["error2_line", "error2", "test2", "https://example.com/job2"],
            ["error1_line", "error1", "test3", "https://example.com/job3"],
        ]

        # Call the function
        reduced_errors = reduce_by_model(mock_errors)

        # Assert the reduced errors per model
        expected_reduced_errors = {
            "model1": {
                "count": 2,
                "errors": {"error1": 2},
            },
            "model2": {
                "count": 1,
                "errors": {"error2": 1},
            },
        }
        self.assertEqual(reduced_errors, expected_reduced_errors)

    def test_make_github_table(self):
        # Create a mock reduced_by_error dictionary
        reduced_by_error = {
            "error1": {"count": 2},
            "error2": {"count": 1},
        }

        # Call the function
        github_table = make_github_table(reduced_by_error)

        # Assert the generated GitHub table
        expected_github_table = "| no. | error | status |\n|-:|:-|:-|\n| 2 | error1 |  |\n| 1 | error2 |  |\n"
        self.assertEqual(github_table, expected_github_table)

    def test_make_github_table_per_model(self):
        # Create a mock reduced_by_model dictionary
        reduced_by_model = {
            "model1": {"count": 2, "errors": {"error1": 2}},
            "model2": {"count": 1, "errors": {"error2": 1}},
        }

        # Call the function
        github_table = make_github_table_per_model(reduced_by_model)

        # Assert the generated GitHub table per model
        expected_github_table = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n| model1 | 2 | error1 | 2 |\n| model2 | 1 | error2 | 1 |\n"
        self.assertEqual(github_table, expected_github_table)


if __name__ == "__main__":
    unittest.main()
