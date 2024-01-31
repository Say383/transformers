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
    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_job_links(self, mock_get):
        # TODO: Implement test case
        pass

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    def test_get_artifacts_links(self, mock_get):
        # TODO: Implement test case
        pass

    @mock.patch("utils.get_ci_error_statistics.requests.get")
    @mock.patch("utils.get_ci_error_statistics.open")
    def test_download_artifact(self, mock_open, mock_get):
        # TODO: Implement test case
        pass

    def test_get_errors_from_single_artifact(self):
        # TODO: Implement test case
        pass

    def test_get_all_errors(self):
        # TODO: Implement test case
        pass

    def test_reduce_by_error(self):
        # TODO: Implement test case
        pass

    def test_get_model(self):
        # TODO: Implement test case
        pass

    def test_reduce_by_model(self):
        # TODO: Implement test case
        pass

    def test_make_github_table(self):
        # TODO: Implement test case
        pass

    def test_make_github_table_per_model(self):
        # TODO: Implement test case
        pass


if __name__ == "__main__":
    unittest.main()
