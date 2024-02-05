import json
import os
import unittest
import zipfile
from io import BytesIO
from unittest import mock

from get_ci_error_statistics import (download_artifact, get_all_errors,
                                     get_artifacts_links,
                                     get_errors_from_single_artifact,
                                     get_job_links, make_github_table,
                                     make_github_table_per_model,
                                     reduce_by_error, reduce_by_model)


class TestGetCIErrorStatistics(unittest.TestCase):
    @mock.patch("get_ci_error_statistics.requests.get")
    def test_get_job_links(self, mock_get):
        # TODO: Implement test cases for get_job_links function
        pass

    @mock.patch("get_ci_error_statistics.requests.get")
    def test_get_artifacts_links(self, mock_get):
        # TODO: Implement test cases for get_artifacts_links function
        pass

    @mock.patch("get_ci_error_statistics.requests.get")
    @mock.patch("get_ci_error_statistics.requests.head")
    def test_download_artifact(self, mock_head, mock_get):
        # TODO: Implement test cases for download_artifact function
        pass

    def test_get_errors_from_single_artifact(self):
        # TODO: Implement test cases for get_errors_from_single_artifact function
        pass

    def test_get_all_errors(self):
        # TODO: Implement test cases for get_all_errors function
        pass

    def test_reduce_by_error(self):
        # TODO: Implement test cases for reduce_by_error function
        pass

    def test_reduce_by_model(self):
        # TODO: Implement test cases for reduce_by_model function
        pass

    def test_make_github_table(self):
        # TODO: Implement test cases for make_github_table function
        pass

    def test_make_github_table_per_model(self):
        # TODO: Implement test cases for make_github_table_per_model function
        pass


if __name__ == "__main__":
    unittest.main()
