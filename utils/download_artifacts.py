import os

import requests


def download_artifacts(artifact_urls, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for url in artifact_urls:
        response = requests.get(url)
        artifact_name = url.split("/")[-1]
        output_path = os.path.join(output_dir, artifact_name)

        with open(output_path, "wb") as f:
            f.write(response.content)

    return "Artifacts downloaded successfully."
