import json
import os
import unittest
from unittest import mock

from utils.get_ci_error_statistics import (download_artifact, get_all_errors,
                                           get_artifacts_links,
                                           get_errors_from_single_artifact,
                                           get_job_links, get_model,
                                           make_github_table,
                                           make_github_table_per_model,
                                           reduce_by_error, reduce_by_model)


class TestGetCIErrorStatistics(unittest.TestCase):
    @mock.patch("utils.get_ci_error_statistics.requests")
    def test_get_job_links(self, mock_requests):
        # Mock the response from the API
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "jobs": [
                {"name": "job1", "html_url": "https://example.com/job1"},
                {"name": "job2", "html_url": "https://example.com/job2"},
            ],
            "total_count": 2,
        }
        mock_requests.get.return_value = mock_response

        # Call the function
        job_links = get_job_links("workflow_run_id")

        # Assertions
        self.assertEqual(job_links, {"job1": "https://example.com/job1", "job2": "https://example.com/job2"})
        mock_requests.get.assert_called_once_with(
            "https://api.github.com/repos/huggingface/transformers/actions/runs/workflow_run_id/jobs?per_page=100",
            headers=None,
        )

    @mock.patch("utils.get_ci_error_statistics.requests")
    def test_get_artifacts_links(self, mock_requests):
        # Mock the response from the API
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "artifacts": [
                {"name": "artifact1", "archive_download_url": "https://example.com/artifact1"},
                {"name": "artifact2", "archive_download_url": "https://example.com/artifact2"},
            ],
            "total_count": 2,
        }
        mock_requests.get.return_value = mock_response

        # Call the function
        artifacts = get_artifacts_links("workflow_run_id")

        # Assertions
        self.assertEqual(
            artifacts,
            {"artifact1": "https://example.com/artifact1", "artifact2": "https://example.com/artifact2"},
        )
        mock_requests.get.assert_called_once_with(
            "https://api.github.com/repos/huggingface/transformers/actions/runs/workflow_run_id/artifacts?per_page=100",
            headers=None,
        )

    @mock.patch("utils.get_ci_error_statistics.requests")
    def test_download_artifact(self, mock_requests):
        # Mock the response from the API
        mock_response = mock.Mock()
        mock_response.headers = {"Location": "https://example.com/download"}
        mock_requests.get.return_value = mock_response
        mock_response_content = mock.Mock()
        mock_response_content.content = b"artifact content"
        mock_response_content.__enter__.return_value = mock_response_content
        mock_requests.get.return_value = mock_response_content

        # Call the function
        download_artifact("artifact_name", "artifact_url", "output_dir", "token")

        # Assertions
        mock_requests.get.assert_called_with("artifact_url", headers=None, allow_redirects=False)
        mock_requests.get.assert_called_with("https://example.com/download", allow_redirects=True)
        mock_response_content.write.assert_called_once_with(b"artifact content")

    def test_get_errors_from_single_artifact(self):
        # Create a mock zipfile
        mock_zipfile = mock.Mock()
        mock_zipfile.namelist.return_value = ["failures_line.txt", "summary_short.txt", "job_name.txt"]
        mock_zipfile.open.side_effect = [
            mock.mock_open(read_data=b"error_line: error").return_value,
            mock.mock_open(read_data=b"FAILED test1").return_value,
            mock.mock_open(read_data=b"job1").return_value,
        ]

        # Call the function
        errors = get_errors_from_single_artifact("artifact_zip_path", job_links={"job1": "https://example.com/job1"})

        # Assertions
        self.assertEqual(errors, [["error_line", "error", "test1", "https://example.com/job1"]])
        mock_zipfile.namelist.assert_called_once()
        mock_zipfile.open.assert_has_calls(
            [
                mock.call("failures_line.txt"),
                mock.call("summary_short.txt"),
                mock.call("job_name.txt"),
            ]
        )

    @mock.patch("utils.get_ci_error_statistics.os")
    @mock.patch("utils.get_ci_error_statistics.zipfile")
    def test_get_all_errors(self, mock_zipfile, mock_os):
        # Mock the listdir function
        mock_os.listdir.return_value = ["artifact1.zip", "artifact2.zip"]

        # Mock the zipfile.ZipFile class
        mock_zipfile.ZipFile.return_value.__enter__.return_value = mock_zipfile.ZipFile.return_value
        mock_zipfile.ZipFile.return_value.namelist.return_value = ["file1.txt", "file2.txt"]

        # Mock the get_errors_from_single_artifact function
        mock_get_errors_from_single_artifact = mock.Mock()
        mock_get_errors_from_single_artifact.return_value = [["error1", "test1", "https://example.com/job1"]]

        with mock.patch(
            "utils.get_ci_error_statistics.get_errors_from_single_artifact",
            mock_get_errors_from_single_artifact,
        ):
            # Call the function
            errors = get_all_errors("artifact_dir", job_links={"job1": "https://example.com/job1"})

            # Assertions
            self.assertEqual(errors, [["error1", "test1", "https://example.com/job1"]])
            mock_os.listdir.assert_called_once_with("artifact_dir")
            mock_zipfile.ZipFile.assert_called_once_with("artifact_dir/artifact1.zip")
            mock_zipfile.ZipFile.return_value.__enter__.assert_called_once()
            mock_zipfile.ZipFile.return_value.namelist.assert_called_once()
            mock_get_errors_from_single_artifact.assert_called_once_with(
                mock_zipfile.ZipFile.return_value.__enter__.return_value,
                job_links={"job1": "https://example.com/job1"},
            )

    def test_reduce_by_error(self):
        # Create a mock Counter
        mock_counter = mock.Mock()
        mock_counter.most_common.return_value = [("error1", 2), ("error2", 1)]

        # Call the function
        reduced_by_error = reduce_by_error(
            [["error1", "test1"], ["error1", "test2"], ["error2", "test3"]],
            error_filter=["error1"],
        )

        # Assertions
        self.assertEqual(
            reduced_by_error,
            {
                "error2": {"count": 1, "failed_tests": [("test3", "https://example.com/job1")]},
            },
        )
        mock_counter.most_common.assert_called_once()
        mock_counter.update.assert_called_once_with(["error1", "error1", "error2"])

    def test_get_model(self):
        # Call the function
        model = get_model("tests/models/model1::test1")

        # Assertions
        self.assertEqual(model, "model1")

    def test_reduce_by_model(self):
        # Call the function
        reduced_by_model = reduce_by_model(
            [["error1", "test1", "model1"], ["error1", "test2", "model2"], ["error2", "test3", "model1"]],
            error_filter=["error1"],
        )

        # Assertions
        self.assertEqual(
            reduced_by_model,
            {
                "model2": {"count": 1, "errors": {"error1": 1}},
            },
        )

    def test_make_github_table(self):
        # Call the function
        table = make_github_table(
            {
                "error1": {"count": 2},
                "error2": {"count": 1},
            }
        )

        # Assertions
        expected_table = "| no. | error | status |\n|-:|:-|:-|\n| 2 | error1 |  |\n| 1 | error2 |  |\n"
        self.assertEqual(table, expected_table)

    def test_make_github_table_per_model(self):
        # Call the function
        table = make_github_table_per_model(
            {
                "model1": {"count": 2, "errors": {"error1": 2}},
                "model2": {"count": 1, "errors": {"error1": 1}},
            }
        )

        # Assertions
        expected_table = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n| model1 | 2 | error1 | 2 |\n| model2 | 1 | error1 | 1 |\n"
        self.assertEqual(table, expected_table)


if __name__ == "__main__":
    unittest.main()
