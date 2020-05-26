"""
Utilities for mtools

"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.3"


import logging
import os
import uuid
import numpy as np
from PIL import Image as pillow


def accuracy(delta_sr):
    """
    Accuracy as defined in ACIX I APU criterion paper
    :param delta_sr: see delta_sr
    :return: Accuracy
    """
    return np.sum(delta_sr) / len(delta_sr)


def count_nan(arr):
    """
    Count the number of NaN in arr
    :param arr:
    :return: integer
    """
    return np.count_nonzero(np.isnan(arr))


def count_not_nan(arr):
    """
    Count the number of NaN in arr
    :param arr:
    :return: integer
    """
    return np.count_nonzero(~np.isnan(arr))


def delta_sr(processor_sr, aeronet_sr):
    """
    Convention in ACIX I paper
    :param processor_sr: surface reflectance of the processor
    :param aeronet_sr: surface reflectance of the reference (aeronet based)
    :return:
    """
    return processor_sr - aeronet_sr


def get_logger(name, verbose=False):
    """
    Simple logger
    :param name: eg. the app name
    :param verbose: sets DEBUG level if True
    :return: logger object
    """
    logger = logging.getLogger(name)
    logging_file = name + '_' + str(uuid.uuid4()) + '.log'
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

    logger.info("Generated with MTOOLS version : " + __version__ + ". For help, please contact " + __author__)

    return logger


def is_valid(band, mask):
    """
    Return a vector of pixels from the array 'band' that match 'mask'=1
    :param band:
    :param mask:
    :return: a numpy vector
    """
    search = np.where(mask == 1)
    valid_pixels = band[search]
    return valid_pixels


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


def mse(v1, v2):
    """
    Return RMSE between two vectors of same length
    :param v1: numpy vector
    :param v2: numpy vector
    :return: float rmse
    """
    return np.nanmean((v1 - v2) ** 2)


def precision(delta_sr):
    """
    Precision as defined in ACIX I APU criterion paper
    :param delta_sr: see delta_sr
    :return: Precision
    """
    acc = accuracy(delta_sr)
    return np.sqrt((np.sum((delta_sr - acc) ** 2)) / (len(delta_sr) - 1))


def rmse(v1, v2):
    """
    Return RMSE between two vectors of same length
    :param v1: numpy vector
    :param v2: numpy vector
    :return: float rmse
    """
    return np.sqrt(np.nanmean((v1 - v2) ** 2))

def rmse_d(diff):
    """
    Return RMSE from input diff between two vectors of same length
    :param v1: numpy vector
    :param v2: numpy vector
    :return: float rmse
    """
    return np.sqrt(np.nanmean((diff) ** 2))


def uncertainty(delta_sr):
    """
    Uncertainty as defined in ACIX I APU criterion paper
    :return: Uncertainty
    """
    return np.sqrt(np.sum(delta_sr**2) / len(delta_sr))


def write_list_to_file(guest_list, filename):
    """Write the list to csv file."""

    with open(filename, "w") as outfile:
        for entries in guest_list:
            outfile.write(str(entries))
            outfile.write("\n")


def _convert_band_uint8(band, vmin=0, vmax=None):
    """Convert a band array to unint8
    :return: an unint8 numpy array
    """
    if vmax == None:
        b_max = np.nanmax(band)
    else:
        b_max = vmax

    clipped_band = np.clip(band, vmin, b_max)

    if b_max > 0:
        img = clipped_band / b_max * 256
    else:
        img = clipped_band * 0

    return img.astype(np.uint8)