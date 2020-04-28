"""
Tests Utilities for mtools

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import utilities
import Roi
import Product
import numpy
from sklearn.metrics import mean_squared_error

TEST_DATA_PATH = "/home/colin/code/mtools/test_data/"


logger = utilities.get_logger('test_utilities', verbose=True)


def test_rmse_single_vector():
    logger.debug("test_rmse_single_vector")
    v1 = numpy.random.rand(100)
    rmse_0 = utilities.rmse(v1,v1)
    assert rmse_0 == 0

def test_mse_along_random_vector():
    logger.debug("test_mse_along_random_vector")
    v1 = numpy.random.rand(100)
    v2 = numpy.random.rand(100)
    mse_utilities = utilities.mse(v1,v2)
    mse_sklearn = mean_squared_error(v1,v2)
    logger.debug("MSE(utilities) = %12.8f, MSE(sklearn) = %12.8f" % (mse_utilities, mse_sklearn))
    assert mse_utilities == mse_sklearn

def test_rmse_along_random_vector():
    logger.debug("test_rmse_along_random_vector")
    v1 = numpy.random.rand(100)
    v2 = numpy.random.rand(100)
    rmse_utilities = utilities.rmse(v1,v2)
    rmse_sklearn = numpy.sqrt(mean_squared_error(v1,v2))
    logger.debug("RMSE(utilities) = %12.8f, RMSE(sklearn) = %12.8f" % (rmse_utilities, rmse_sklearn))
    assert rmse_utilities == rmse_sklearn

def test_count_nan():
    logger.debug("test_count_nan")
    fullnan = numpy.array([numpy.nan, numpy.nan, numpy.nan])
    assert utilities.count_nan(fullnan) == 3
    assert utilities.count_not_nan(fullnan) == 0
    nonan = numpy.zeros_like(fullnan)
    assert utilities.count_nan(nonan) == 0
    assert utilities.count_not_nan(nonan) == 3
    nonan[1] = numpy.nan
    assert utilities.count_nan(nonan) == 1
    assert utilities.count_not_nan(nonan) == 2

def test_roi_quicklook_clear():
    logger.info("test_roi_quicklook_clear")
    p_venus = Product.Product_zip_venus(TEST_DATA_PATH + "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)
    r_clear = Roi.Roi([22, 649460, 4238440], 500, logger)
    b = p_venus.get_band_subset(p_venus.find_band("SRE_B3."), roi=r_clear, scalef=p_venus.sre_scalef)
    g = p_venus.get_band_subset(p_venus.find_band("SRE_B4."), roi=r_clear, scalef=p_venus.sre_scalef)
    r = p_venus.get_band_subset(p_venus.find_band("SRE_B7."), roi=r_clear, scalef=p_venus.sre_scalef)
    assert type(b) is numpy.ndarray
    assert type(g) is numpy.ndarray
    assert type(r) is numpy.ndarray
    is_quicklook = utilities.make_quicklook_rgb(r, g, b, logger, outfile="clear.png")
    assert is_quicklook == 0

def test_roi_quicklook_partly():
    logger.info("test_roi_quicklook_partly")
    p_venus = Product.Product_zip_venus(TEST_DATA_PATH + "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)
    r_partly_cloudy = Roi.Roi([33, 678644, 4246106], 500, logger)
    b = p_venus.get_band_subset(p_venus.find_band("SRE_B3."), roi=r_partly_cloudy, scalef=p_venus.sre_scalef)
    g = p_venus.get_band_subset(p_venus.find_band("SRE_B4."), roi=r_partly_cloudy, scalef=p_venus.sre_scalef)
    r = p_venus.get_band_subset(p_venus.find_band("SRE_B7."), roi=r_partly_cloudy, scalef=p_venus.sre_scalef)
    assert type(b) is numpy.ndarray
    assert type(g) is numpy.ndarray
    assert type(r) is numpy.ndarray
    is_quicklook = utilities.make_quicklook_rgb(r, g, b, logger, outfile="partly.png", vmax=None)
    assert is_quicklook == 0

    is_quicklook = utilities.make_quicklook_rgb(r, g, b, logger, outfile="partly.jpg", vmax=None)
    assert is_quicklook == 0

def test_quicklook_bad_cases():
    bad = None
    is_not_quicklook = utilities.make_quicklook_rgb(bad, bad, bad, logger, outfile="bad.png", vmax=None)
    assert is_not_quicklook == 1

    zeros = numpy.zeros([9,9])
    is_quicklook = utilities.make_quicklook_rgb(zeros, zeros, zeros, logger, outfile="zeros.png", vmax=None)
    assert is_quicklook == 0