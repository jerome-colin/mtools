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


def make_quicklook_rgb(r, g, b, logger, vmax=0.5, outfile="quicklook.png"):
    """
    Generate a quicklook as PNG
    :param r: band name (should match string name in filename)
    :param g: band name (should match string name in filename)
    :param b: band name (should match string name in filename)
    :param logger:
    :param outfile:
    :return: void
    """
    try:
        logger.info("Generating quicklook...")
        red_band = _convert_band_uint8(r, vmax=vmax)
        green_band = _convert_band_uint8(g, vmax=vmax)
        blue_band = _convert_band_uint8(b, vmax=vmax)

        array_stack = np.dstack((red_band, green_band, blue_band))
        img = pillow.fromarray(array_stack)
        if outfile[-4:] != ".png":
            outfile += ".png"

        img.save(outfile)
        return 0

    except:
        return 1


def _convert_band_uint8(band, vmin=0, vmax=None):
    """Convert a band array to unint8
    :return: an unint8 numpy array
    """
    if vmax == None:
        b_max = np.nanmax(band)
    else:
        b_max = vmax

    clipped_band = np.clip(band,vmin,b_max)

    if b_max > 0:
        img = clipped_band / b_max * 256
    else:
        img = clipped_band * 0

    return img.astype(np.uint8)
