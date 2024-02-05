import unittest
from unittest.mock import MagicMock

from utils.get_ci_error_statistics import (download_artifact, get_all_errors,
                                           get_artifacts_links,
                                           get_errors_from_single_artifact,
                                           get_job_links, get_model,
                                           make_github_table,
                                           make_github_table_per_model,
                                           reduce_by_error, reduce_by_model)


class TestGetCIErrorStatistics(unittest.TestCase):
    def test_get_job_links(self):
        # Test case 1: Provide a valid workflow run ID and check if the returned job links match the expected values
        workflow_run_id = "12345"
        expected_job_links = {"job1": "https://github.com/job1", "job2": "https://github.com/job2"}
        get_job_links_result = get_job_links(workflow_run_id)
        self.assertEqual(get_job_links_result, expected_job_links)

        # Test case 2: Provide an invalid workflow run ID and check if an empty dictionary is returned
        workflow_run_id = "invalid"
        expected_job_links = {}
        get_job_links_result = get_job_links(workflow_run_id)
        self.assertEqual(get_job_links_result, expected_job_links)

    def test_get_artifacts_links(self):
        # Test case 1: Provide a valid workflow run ID and check if the returned artifact links match the expected values
        workflow_run_id = "12345"
        expected_artifact_links = {"artifact1": "https://github.com/artifact1", "artifact2": "https://github.com/artifact2"}
        get_artifacts_links_result = get_artifacts_links(workflow_run_id)
        self.assertEqual(get_artifacts_links_result, expected_artifact_links)

        # Test case 2: Provide an invalid workflow run ID and check if an empty dictionary is returned
        workflow_run_id = "invalid"
        expected_artifact_links = {}
        get_artifacts_links_result = get_artifacts_links(workflow_run_id)
        self.assertEqual(get_artifacts_links_result, expected_artifact_links)

    def test_download_artifact(self):
        # Test case 1: Provide a valid artifact URL and check if the artifact is downloaded correctly
        artifact_name = "artifact1"
        artifact_url = "https://github.com/artifact1"
        output_dir = "/path/to/output"
        token = "token"
        download_artifact(artifact_name, artifact_url, output_dir, token)
        # Add assertions to check if the artifact is downloaded correctly

        # Test case 2: Provide an invalid artifact URL and check if an exception is raised
        artifact_name = "artifact2"
        artifact_url = "invalid"
        output_dir = "/path/to/output"
        token = "token"
        with self.assertRaises(Exception):
            download_artifact(artifact_name, artifact_url, output_dir, token)

    def test_get_errors_from_single_artifact(self):
        # Test case 1: Provide a valid artifact zip path and check if the extracted errors match the expected values
        artifact_zip_path = "/path/to/artifact.zip"
        expected_errors = [["error1_line", "error1"], ["error2_line", "error2"]]
        get_errors_from_single_artifact_result = get_errors_from_single_artifact(artifact_zip_path)
        self.assertEqual(get_errors_from_single_artifact_result, expected_errors)

        # Test case 2: Provide an invalid artifact zip path and check if an exception is raised
        artifact_zip_path = "/path/to/invalid.zip"
        with self.assertRaises(Exception):
            get_errors_from_single_artifact(artifact_zip_path)

    def test_get_all_errors(self):
        # Test case 1: Provide a directory containing valid artifact zip files and check if all errors are correctly extracted
        artifact_dir = "/path/to/artifacts"
        expected_errors = [["error1_line", "error1"], ["error2_line", "error2"], ["error3_line", "error3"]]
        get_all_errors_result = get_all_errors(artifact_dir)
        self.assertEqual(get_all_errors_result, expected_errors)

        # Test case 2: Provide a directory containing invalid artifact zip files and check if an empty list is returned
        artifact_dir = "/path/to/invalid"
        expected_errors = []
        get_all_errors_result = get_all_errors(artifact_dir)
        self.assertEqual(get_all_errors_result, expected_errors)

    def test_reduce_by_error(self):
        # Test case 1: Provide a list of errors and check if the returned counts match the expected values
        errors = [["error1_line", "error1"], ["error2_line", "error2"], ["error1_line", "error1"]]
        expected_reduced_errors = {
            "error1": {"count": 2, "failed_tests": [("test1", "error1_line"), ("test3", "error1_line")]},
            "error2": {"count": 1, "failed_tests": [("test2", "error2_line")]},
        }
        reduce_by_error_result = reduce_by_error(errors)
        self.assertEqual(reduce_by_error_result, expected_reduced_errors)

        # Test case 2: Provide an empty list of errors and check if an empty dictionary is returned
        errors = []
        expected_reduced_errors = {}
        reduce_by_error_result = reduce_by_error(errors)
        self.assertEqual(reduce_by_error_result, expected_reduced_errors)

    def test_get_model(self):
        # Test case 1: Provide a test method and check if the returned model name matches the expected value
        test_method = "tests/models/test_model.py::test_model1"
        expected_model_name = "model1"
        get_model_result = get_model(test_method)
        self.assertEqual(get_model_result, expected_model_name)

        # Test case 2: Provide a test method without a model name and check if None is returned
        test_method = "tests/test_utils.py::test_utils1"
        expected_model_name = None
        get_model_result = get_model(test_method)
        self.assertEqual(get_model_result, expected_model_name)

    def test_reduce_by_model(self):
        # Test case 1: Provide a list of errors and check if the returned counts per model match the expected values
        errors = [
            ["error1_line", "error1", "tests/models/test_model1.py::test_model1"],
            ["error2_line", "error2", "tests/models/test_model1.py::test_model1"],
            ["error1_line", "error1", "tests/models/test_model2.py::test_model2"],
        ]
        expected_reduced_errors = {
            "model1": {
                "count": 2,
                "errors": {"error1": 2},
            },
            "model2": {
                "count": 1,
                "errors": {"error1": 1},
            },
        }
        reduce_by_model_result = reduce_by_model(errors)
        self.assertEqual(reduce_by_model_result, expected_reduced_errors)

        # Test case 2: Provide a list of errors without model names and check if an empty dictionary is returned
        errors = [["error1_line", "error1", None], ["error2_line", "error2", None]]
        expected_reduced_errors = {}
        reduce_by_model_result = reduce_by_model(errors)
        self.assertEqual(reduce_by_model_result, expected_reduced_errors)

    def test_make_github_table(self):
        # Test case 1: Provide a dictionary of reduced errors and check if the generated table matches the expected format
        reduced_errors = {
            "error1": {"count": 2, "failed_tests": [("test1", "error1_line"), ("test3", "error1_line")]},
            "error2": {"count": 1, "failed_tests": [("test2", "error2_line")]},
        }
        expected_table = "| no. | error | status |\n|-:|:-|:-|\n| 2 | error1 |  |\n| 1 | error2 |  |\n"
        make_github_table_result = make_github_table(reduced_errors)
        self.assertEqual(make_github_table_result, expected_table)

        # Test case 2: Provide an empty dictionary of reduced errors and check if an empty table is returned
        reduced_errors = {}
        expected_table = "| no. | error | status |\n|-:|:-|:-|\n"
        make_github_table_result = make_github_table(reduced_errors)
        self.assertEqual(make_github_table_result, expected_table)

    def test_make_github_table_per_model(self):
        # Test case 1: Provide a dictionary of reduced errors per model and check if the generated table matches the expected format
        reduced_errors = {
            "model1": {"count": 2, "errors": {"error1": 2}},
            "model2": {"count": 1, "errors": {"error1": 1}},
        }
        expected_table = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n| model1 | 2 | error1 | 2 |\n| model2 | 1 | error1 | 1 |\n"
        make_github_table_per_model_result = make_github_table_per_model(reduced_errors)
        self.assertEqual(make_github_table_per_model_result, expected_table)

        # Test case 2: Provide an empty dictionary of reduced errors per model and check if an empty table is returned
        reduced_errors = {}
        expected_table = "| model | no. of errors | major error | count |\n|-:|-:|-:|-:|\n"
        make_github_table_per_model_result = make_github_table_per_model(reduced_errors)
        self.assertEqual(make_github_table_per_model_result, expected_table)


if __name__ == "__main__":
    unittest.main()
