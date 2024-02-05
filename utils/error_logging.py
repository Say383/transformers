import logging
from typing import List


def log_errors_to_file(errors: List[str], file_path: str) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    file_handler = logging.FileHandler(file_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    for error in errors:
        logger.error(error)
