import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--token", required=True, help="GitHub token")
args = parser.parse_args()
