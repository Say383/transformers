import argparse
import math
import traceback

import dateutil.parser as date_parser
import requests


def extract_time_from_single_job(job):
    """Extract time info from a single job in a GitHub Actions workflow run"""
    # Existing code

def extract_job_time(workflow_run_id, token=None):
    """Extract time info for all jobs in a GitHub Actions workflow run"""
    # Existing code


def get_job_time(workflow_run_id, token=None):
    """Extract time info for all jobs in a GitHub Actions workflow run"""

    headers = None
    if token is not None:
        headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}

    url = f"https://api.github.com/repos/huggingface/transformers/actions/runs/{workflow_run_id}/jobs?per_page=100"
    result = requests.get(url, headers=headers).json()
    job_time = {}

    job_time = extract_job_time(args.workflow_run_id)
    job_time = dict(sorted(job_time.items(), key=lambda item: item[1]["duration"], reverse=True))

    for k, v in job_time.items():
        print(f'{k}: {v["duration"]}')


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
