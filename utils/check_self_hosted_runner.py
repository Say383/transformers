import json

def handle_offline_runners():
    try:
        with open("offline_runners.txt", "r") as fp:
            offline_runners = json.load(fp)
    except FileNotFoundError:
        offline_runners = []

    return offline_runners


offline_runners = handle_offline_runners()
# Add a check to handle the case when the offline_runners.txt file is not found
def handle_offline_runners():
    try:
        with open("offline_runners.txt", "r") as fp:
            offline_runners = json.load(fp)
    except FileNotFoundError:
        offline_runners = []

    return offline_runners


offline_runners = handle_offline_runners()
