import argparse
import json
import os
import time
import zipfile

from get_ci_error_statistics import download_artifact, get_artifacts_links

from transformers import logging


logger = logging.get_logger(__name__)


def extract_warnings_from_single_artifact(artifact_path, targets):
    """Extract warnings from a downloaded artifact (in .zip format)"""
    selected_warnings = set()
    buffer = []

    def parse_line(fp):
        for line in fp:
            if isinstance(line, bytes):
                line = line.decode("UTF-8")
            if "warnings summary (final)" in line:
                continue
            # This means we are outside the body of a warning
            elif not line.startswith(" "):
                # process a single warning and move it to `selected_warnings`.
                if len(buffer) > 0:
                    warning = "\n".join(buffer)
                    # Only keep the warnings specified in `targets`
                    if any(f": {x}: " in warning for x in targets):
                        selected_warnings.add(warning)
                    buffer.clear()
                continue
            else:
                line = line.strip()
                buffer.append(line)
                            continue
                        with z.open(filename) as fp:
                            parse_line(fp)
        except Exception:
            logger.warning(
                f"{artifact_path} is either an invalid zip file or something else wrong. This file is skipped."
            )

    return selected_warnings


def extract_warnings(artifact_dir, targets):
    """Extract warnings from all artifact files"""
def extract_warnings(artifact_dir, targets, from_gh):
    """Extract warnings from all artifact files"""

    selected_warnings = set()

    paths = [os.path.join(artifact_dir, p) for p in os.listdir(artifact_dir) if (p.endswith(".zip") or from_gh)]
    for p in paths:
        selected_warnings.update(extract_warnings_from_single_artifact(p, targets, from_gh))

    return selected_warnings
def extract_warnings(artifact_dir, targets, from_gh):
    """Extract warnings from all artifact files"""

    selected_warnings = set()

    paths = [os.path.join(artifact_dir, p) for p in os.listdir(artifact_dir) if (p.endswith(".zip") or from_gh)]
    for p in paths:
        selected_warnings.update(extract_warnings_from_single_artifact(p, targets, from_gh))

    return selected_warnings
def extract_warnings(artifact_dir, targets, from_gh):
    """Extract warnings from all artifact files"""

    selected_warnings = set()

    paths = [os.path.join(artifact_dir, p) for p in os.listdir(artifact_dir) if (p.endswith(".zip") or from_gh)]
    for p in paths:
        selected_warnings.update(extract_warnings_from_single_artifact(p, targets, from_gh))

    return selected_warnings
    selected_warnings = set()

    paths = [os.path.join(artifact_dir, p) for p in os.listdir(artifact_dir) if (p.endswith(".zip") or from_gh)]
    for p in paths:
        selected_warnings.update(extract_warnings_from_single_artifact(p, targets))

    return selected_warnings


new line(s) to replace
    selected_warnings = extract_warnings(args.output_dir, args.targets)
    selected_warnings = sorted(selected_warnings)
    with open(os.path.join(args.output_dir, "selected_warnings.json"), "w", encoding="UTF-8") as fp:
        json.dump(selected_warnings, fp, ensure_ascii=False, indent=4)
