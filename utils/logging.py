"""
Helper functions for logging
"""
import logging
import os


def get_logger(filename: str,
               path: str = 'log',
               encoding: str = 'utf-8',
               debug: bool = False) -> logging.Logger:
    """
    Configuring and return logger with file as sream for logging.

    Args:
        filename: Filename of created .log file.
        path: Directory where the log file will be created.
        encoding: The encoding used for the log file.
        debug: If True setting log level to DEBUG, INFO otherwise.

    Returns:
        A logger that uses a file as a stream for logging.
    """
    if not os.path.exists(path):
        os.makedirs(path)

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%m-%d-%Y %H:%M:%S')
    logging_level = logging.DEBUG if debug else logging.INFO

    file_handler = logging.FileHandler(filename=f'{path}/{filename}.log',
                                       mode='w+',
                                       encoding=encoding)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging_level)
    logger.addHandler(file_handler)

    return logger
