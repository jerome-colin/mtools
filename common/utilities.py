import logging
import os


def get_logger(name, verbose=False):
    """
    Simple logger
    :param name: eg. the app name
    :param verbose: sets DEBUG level if True
    :return: logger object
    """
    logger = logging.getLogger(name)
    logging_file = name + '.log'
    try:
        os.remove(logging_file)
    except FileNotFoundError:
        pass

    logging_handler = logging.FileHandler(logging_file)
    logging_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logging_handler.setFormatter(logging_formatter)
    logger.addHandler(logging_handler)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger

