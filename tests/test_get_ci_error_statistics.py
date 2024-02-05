import unittest
from unittest import mock

from utils import get_ci_error_statistics


class TestGetCIErrorStatistics(unittest.TestCase):
    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_job_links_success(self, mock_get):
        # Mock the API call to requests.get and return a sample response
        mock_get.return_value.json.return_value = {
            "jobs": [
                {"name": "job1", "html_url": "https://example.com/job1"},
                {"name": "job2", "html_url": "https://example.com/job2"},
            ]
        }

        # Call the function to be tested
        job_links = get_ci_error_statistics.get_job_links("workflow_run_id")

        # Assert that the returned job links match the expected values
        expected_job_links = {
            "job1": "https://example.com/job1",
            "job2": "https://example.com/job2",
        }
        self.assertEqual(job_links, expected_job_links)

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_artifacts_links_success(self, mock_get):
        # Mock the API call to requests.get and return a sample response
        mock_get.return_value.json.return_value = {
            "artifacts": [
                {"name": "artifact1", "archive_download_url": "https://example.com/artifact1.zip"},
                {"name": "artifact2", "archive_download_url": "https://example.com/artifact2.zip"},
            ]
        }

        # Call the function to be tested
        artifacts = get_ci_error_statistics.get_artifacts_links("workflow_run_id")

        # Assert that the returned artifacts links match the expected values
        expected_artifacts = {
            "artifact1": "https://example.com/artifact1.zip",
            "artifact2": "https://example.com/artifact2.zip",
        }
        self.assertEqual(artifacts, expected_artifacts)

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_download_artifact_success(self, mock_get):
        # Mock the API call to requests.get and return a sample response
        mock_get.return_value.headers = {"Location": "https://example.com/download"}
        mock_get.return_value.content = b"Sample artifact content"

        # Call the function to be tested
        get_ci_error_statistics.download_artifact("artifact1", "https://example.com/artifact1.zip", "output_dir", "token")

        # Assert that the artifact is downloaded and saved correctly
        expected_file_path = "output_dir/artifact1.zip"
        with open(expected_file_path, "rb") as f:
            self.assertEqual(f.read(), b"Sample artifact content")

    def test_get_errors_from_single_artifact_success(self):
        # Create a sample artifact zip file
        artifact_zip_path = "sample_artifact.zip"
        with open(artifact_zip_path, "w") as f:
            f.write("Sample artifact content")

        # Call the function to be tested
        errors = get_ci_error_statistics.get_errors_from_single_artifact(artifact_zip_path)

        # Assert that the errors are extracted correctly from the artifact
        expected_errors = [["error_line", "error", "failed_test", None]]
        self.assertEqual(errors, expected_errors)

    @mock.patch("os.listdir")
    @mock.patch("utils.get_ci_error_statistics.get_errors_from_single_artifact")
    def test_get_all_errors_success(self, mock_get_errors_from_single_artifact, mock_listdir):
        # Mock the os.listdir function to return a list of sample artifact zip files
        mock_listdir.return_value = ["artifact1.zip", "artifact2.zip"]

        # Mock the get_errors_from_single_artifact function to return sample errors
        mock_get_errors_from_single_artifact.side_effect = [
            [["error_line1", "error1", "failed_test1", None]],
            [["error_line2", "error2", "failed_test2", None]],
        ]

        # Call the function to be tested
        errors = get_ci_error_statistics.get_all_errors("artifact_dir")

        # Assert that all errors are extracted correctly from the artifacts
        expected_errors = [
            ["error_line1", "error1", "failed_test1", None],
            ["error_line2", "error2", "failed_test2", None],
        ]
        self.assertEqual(errors, expected_errors)

    def test_reduce_by_error_success(self):
        # Create a sample list of errors
        logs = [
            ["error1_line1", "error1", "failed_test1"],
            ["error1_line2", "error1", "failed_test2"],
            ["error2_line1", "error2", "failed_test3"],
        ]

        # Call the function to be tested
        reduced_errors = get_ci_error_statistics.reduce_by_error(logs)

        # Assert that the errors are reduced correctly and the output matches the expected format
        expected_reduced_errors = {
            "error1": {"count": 2, "failed_tests": [("failed_test1", "error1_line1"), ("failed_test2", "error1_line2")]},
            "error2": {"count": 1, "failed_tests": [("failed_test3", "error2_line1")]},
        }
        self.assertEqual(reduced_errors, expected_reduced_errors)

    def test_get_model_success(self):
        # Create a sample test method
        test = "tests/models/test_model.py::TestModel::test_method"

        # Call the function to be tested
        model = get_ci_error_statistics.get_model(test)

        # Assert that the model name is extracted correctly
        expected_model = "model"
        self.assertEqual(model, expected_model)

    def test_reduce_by_model_success(self):
        # Create a sample list of errors with models
        logs = [
            ["error1_line1", "error1", "failed_test1", "model1"],
            ["error1_line2", "error1", "failed_test2", "model1"],
            ["error2_line1", "error2", "failed_test3", "model2"],
        ]

        # Call the function to be tested
        reduced_errors = get_ci_error_statistics.reduce_by_model(logs)

        # Assert that the errors are reduced by model correctly and the output matches the expected format
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

    @mock.patch("utils.get_ci_error_statistics.argparse.ArgumentParser")
    @mock.patch("utils.get_ci_error_statistics.get_job_links")
    @mock.patch("utils.get_ci_error_statistics.get_artifacts_links")
    @mock.patch("utils.get_ci_error_statistics.download_artifact")
    @mock.patch("utils.get_ci_error_statistics.get_all_errors")
    @mock.patch("utils.get_ci_error_statistics.reduce_by_error")
    @mock.patch("utils.get_ci_error_statistics.reduce_by_model")
    @mock.patch("utils.get_ci_error_statistics.open")
    @mock.patch("utils.get_ci_error_statistics.json.dump")
    def test_main_script_execution_success(
        self,
        mock_json_dump,
        mock_open,
        mock_reduce_by_model,
        mock_reduce_by_error,
        mock_get_all_errors,
        mock_download_artifact,
        mock_get_artifacts_links,
        mock_get_job_links,
        mock_argparse,
    ):
        # Mock the command-line arguments using argparse.Namespace
        args = mock.Mock()
        args.workflow_run_id = "workflow_run_id"
        args.output_dir = "output_dir"
        args.token = "token"
        mock_argparse.ArgumentParser.return_value.parse_args.return_value = args

        # Mock the necessary function calls and return sample values
        mock_get_job_links.return_value = {"job1": "https://example.com/job1"}
        mock_get_artifacts_links.return_value = {"artifact1": "https://example.com/artifact1.zip"}
        mock_get_all_errors.return_value = [["error_line", "error", "failed_test", None]]
        mock_reduce_by_error.return_value = {"error": {"count": 1, "failed_tests": [("failed_test", "error_line")]}}

        # Call the main script
        get_ci_error_statistics.main()

        # Assert that the expected output files are created and contain the correct data
        expected_job_links = {"job1": "https://example.com/job1"}
        mock_json_dump.assert_any_call(expected_job_links, mock_open.return_value.__enter__.return_value)
        expected_artifacts = {"artifact1": "https://example.com/artifact1.zip"}
        mock_json_dump.assert_any_call(expected_artifacts, mock_open.return_value.__enter__.return_value)
        mock_download_artifact.assert_called_with("artifact1", "https://example.com/artifact1.zip", "output_dir", "token")
        expected_errors = [["error_line", "error", "failed_test", None]]
        mock_json_dump.assert_any_call(expected_errors, mock_open.return_value.__enter__.return_value)
        expected_reduced_by_error = {"error": {"count": 1, "failed_tests": [("failed_test", "error_line")]}}

        expected_reduced_by_model = {
            "model": {
                "count": 1,
                "errors": {"error": 1},
            }
        }
        mock_reduce_by_error.assert_called_with(expected_errors)
        mock_reduce_by_model.assert_called_with(expected_errors)
        mock_open.assert_any_call("output_dir/reduced_by_error.txt", "w", encoding="UTF-8")
        mock_open.assert_any_call("output_dir/reduced_by_model.txt", "w", encoding="UTF-8")

    @mock.patch("utils.get_ci_error_statistics.argparse.ArgumentParser")
    @mock.patch("utils.get_ci_error_statistics.logging.error")
    def test_main_script_execution_error_handling(
        self,
        mock_logging_error,
        mock_argparse,
    ):
        # Mock the command-line arguments to trigger an error
        args = mock.Mock()
        args.workflow_run_id = "workflow_run_id"
        args.output_dir = "output_dir"
        args.token = "token"
        mock_argparse.ArgumentParser.return_value.parse_args.return_value = args

        # Mock the necessary function calls to raise an exception
        mock_get_job_links.side_effect = Exception("Error while fetching job links")

        # Call the main script
        get_ci_error_statistics.main()

        # Assert that the error is logged correctly
        expected_error_message = "Error while creating output directory: output_dir: Error while fetching job links"
        mock_logging_error.assert_called_with(expected_error_message)

if __name__ == "__main__":
    unittest.main()
