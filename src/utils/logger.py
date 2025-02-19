import logging
import os

from config import basic_config


BASE_DIR = os.getcwd()
LOG_FILE_PATH = os.path.join(BASE_DIR, "file.log")
STREAM_LOG = basic_config.stream_log

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")


def setup_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        if STREAM_LOG:
            logger.addHandler(console_handler)
    return logger
