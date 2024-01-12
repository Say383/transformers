import os
import time

import requests


def download_artifact(artifact_name, artifact_url, output_dir, token):
    """Download an artifact from the GitHub Actions workflow run."""
    headers = None
    if token is not None:
        headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}

    try:
        result = requests.get(artifact_url, headers=headers, allow_redirects=False)
        download_url = result.headers["Location"]
        response = requests.get(download_url, allow_redirects=True)
        file_path = os.path.join(output_dir, f"{artifact_name}.zip")
        with open(file_path, "wb") as fp:
            fp.write(response.content)
    except Exception as e:
        print(f"Error downloading artifact: {e}")
        # Handle the error or log it as needed


# Example usage
artifact_name = "my_artifact"
artifact_url = "https://api.github.com/repos/huggingface/transformers/actions/artifacts/123/zip"
output_dir = "/path/to/output"
token = "my_github_token"

download_artifact(artifact_name, artifact_url, output_dir, token)
