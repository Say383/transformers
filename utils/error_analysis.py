import argparse
import json
import math
import os
import time
import traceback
import zipfile
from collections import Counter

import requests


def get_job_links(workflow_run_id, token=None):
    # Function implementation


def get_artifacts_links(workflow_run_id, token=None):
    # Function implementation


def download_artifact(artifact_name, artifact_url, output_dir, token):
    # Function implementation


def get_errors_from_single_artifact(artifact_zip_path, job_links=None):
    # Function implementation


def get_all_errors(artifact_dir, job_links=None):
    # Function implementation


def reduce_by_error(logs, error_filter=None):
    # Function implementation


def reduce_by_model(logs, error_filter=None):
    # Function implementation


def make_github_table(reduced_by_error):
    # Function implementation


def make_github_table_per_model(reduced_by_model):
    # Function implementation


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument("--workflow_run_id", type=str, required=True, help="A GitHub Actions workflow run id.")
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Where to store the downloaded artifacts and other result files.",
    )
    parser.add_argument("--token", default=None, type=str, help="A token that has actions:read permission.")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    _job_links = get_job_links(args.workflow_run_id, token=args.token)
    job_links = {}
    # To deal with `workflow_call` event, where a job name is the combination of the job names in the caller and callee.
    # For example, `PyTorch 1.11 / Model tests (models/albert, single-gpu)`.
    if _job_links:
        for k, v in _job_links.items():
            # This is how GitHub actions combine job names.
            if " / " in k:
                index = k.find(" / ")
                k = k[index + len(" / ") :]
            job_links[k] = v
    with open(os.path.join(args.output_dir, "job_links.json"), "w", encoding="UTF-8") as fp:
        json.dump(job_links, fp, ensure_ascii=False, indent=4)

    artifacts = get_artifacts_links(args.workflow_run_id, token=args.token)
    with open(os.path.join(args.output_dir, "artifacts.json"), "w", encoding="UTF-8") as fp:
        json.dump(artifacts, fp, ensure_ascii=False, indent=4)

    for idx, (name, url) in enumerate(artifacts.items()):
        download_artifact(name, url, args.output_dir, args.token)
        # Be gentle to GitHub
        time.sleep(1)

    errors = get_all_errors(args.output_dir, job_links=job_links)

    counter = Counter()
    counter.update([e[1] for e in errors])

    most_common = counter.most_common(30)
    for item in most_common:
        print(item)

    with open(os.path.join(args.output_dir, "errors.json"), "w", encoding="UTF-8") as fp:
        json.dump(errors, fp, ensure_ascii=False, indent=4)

    reduced_by_error = reduce_by_error(errors)
    reduced_by_model = reduce_by_model(errors)

    s1 = make_github_table(reduced_by_error)
    s2 = make_github_table_per_model(reduced_by_model)

    with open(os.path.join(args.output_dir, "reduced_by_error.txt"), "w", encoding="UTF-8") as fp:
        fp.write(s1)
    with open(os.path.join(args.output_dir, "reduced_by_model.txt"), "w", encoding="UTF-8") as fp:
        fp.write(s2)
