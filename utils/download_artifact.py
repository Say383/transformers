import os

import requests


def download_artifact(name, url, output_dir, token=None):
    """Download an artifact file from the provided URL"""
    os.makedirs(output_dir, exist_ok=True)

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_path = os.path.join(output_dir, name)
        with open(file_path, "wb") as file:
            file.write(response.content)
    else:
        raise Exception(f"Failed to download artifact: {response.status_code} - {response.text}")
