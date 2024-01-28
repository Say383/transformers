# utils/logging.py

import logging

logging.basicConfig(level=logging.INFO)

def info(message: str):
    logging.info(message)

def warning(message: str):
    logging.warning(message)

def error(message: str):
    logging.error(message)
