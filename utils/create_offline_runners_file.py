import os
import sys


def create_offline_runners_file():
    if not os.path.exists("utils/offline_runners.txt"):
        with open("utils/offline_runners.txt", "w") as file:
            pass

create_offline_runners_file()
