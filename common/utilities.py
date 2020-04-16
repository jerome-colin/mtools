import logging
import os
import numpy as np
from PIL import Image as pillow


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


def make_quicklook_rgb(r, g, b, logger, outfile="quicklook.png"):
    """
    Generate a quicklook as PNG
    :param r: band name (should match string name in filename)
    :param g: band name (should match string name in filename)
    :param b: band name (should match string name in filename)
    :param logger:
    :param outfile:
    :return: void
    """
    logger.info("Generating quicklook...")
    red_band = _convert_band_uint8(r, vmax=300)
    green_band = _convert_band_uint8(g, vmax=300)
    blue_band = _convert_band_uint8(b, vmax=300)

    array_stack = np.dstack((red_band, green_band, blue_band))
    img = pillow.fromarray(array_stack)
    if outfile[-4:] != ".png":
        outfile += ".png"

    img.save(outfile)


def _convert_band_uint8(band, vmax=None):
    """Convert a band array to unint8
    :return: an unint8 numpy array
    """
    if vmax == None:
        b_max = np.nanmax(band)
    else:
        b_max = vmax

    if b_max > 0:
        img = band / b_max * 256
    else:
        img = band * 0

    return img.astype(np.uint8)
