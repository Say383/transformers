import logging
import traceback

import requests
from github import Github


def get_job_links(workflow_run_id, token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"https://api.github.com/repos/huggingface/transformers/actions/runs/{workflow_run_id}/jobs?per_page=100"
    try:
        result = requests.get(url, headers=headers).json() or {}
        job_links = {}
        for job in result.get("jobs", []):
            job_links[job["name"]] = job["html_url"]
        return job_links
    except Exception:
        logging.error(f"Unknown error, could not fetch links:\n{traceback.format_exc()}")
        return {}

def download_artifacts(artifacts, output_dir, token=None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    for name, url in artifacts.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            with open(f"{output_dir}/{name}", "wb") as f:
                f.write(response.content)
        except Exception:
            logging.error(f"Failed to download artifact {name}:\n{traceback.format_exc()}")

def authenticate(token=None):
    if token:
        return Github(token)
    else:
        return Github()
