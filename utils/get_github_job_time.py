import argparse
import math
import traceback

import dateutil.parser as date_parser
import requests


def get_job_times(workflow_run_id, token=None):
    job_links = get_job_links(workflow_run_id, token=token)
    artifacts = get_artifacts_links(workflow_run_id, token=token)
    job_time = get_job_time(workflow_run_id, token=token)
    selected_warnings = extract_warnings(workflow_run_id, targets=["DeprecationWarning", "UserWarning", "FutureWarning"])

    # Perform analysis on the retrieved data
    # ...

    # Return the analyzed data
    return job_time


if __name__ == "__main__":
    r"""
    Example:

        python get_github_job_time.py --workflow_run_id 2945609517
    """

    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument("--workflow_run_id", type=str, required=True, help="A GitHub Actions workflow run id.")
    args = parser.parse_args()

    job_time = get_job_time(args.workflow_run_id)
    job_time = dict(sorted(job_time.items(), key=lambda item: item[1]["duration"], reverse=True))

    for k, v in job_time.items():
        print(f'{k}: {v["duration"]}')
