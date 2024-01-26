import os
import zipfile

import requests


def download_artifact(artifact_name, artifact_url, output_dir):
    headers = None
    if token is not None:
        headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}

    result = requests.get(artifact_url, headers=headers, allow_redirects=False)
    download_url = result.headers["Location"]
    response = requests.get(download_url, allow_redirects=True)
    file_path = os.path.join(output_dir, f"{artifact_name}.zip")
    with open(file_path, "wb") as fp:
        fp.write(response.content)
