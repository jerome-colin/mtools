"""
Tests Utilities for mtools

"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.3"

import os
import utilities
import Roi
import Product
import numpy
import pytest
from sklearn.metrics import mean_squared_error

TEST_DATA_PATH = os.environ['TEST_DATA_PATH']

logger = utilities.get_logger('test_utilities', verbose=True)


def test_rmse_single_vector():
    logger.debug("test_rmse_single_vector")
    v1 = numpy.random.rand(100)
    rmse_0 = utilities.rmse(v1, v1)
    assert rmse_0 == 0


def test_mse_along_random_vector():
    logger.debug("test_mse_along_random_vector")
    v1 = numpy.random.rand(100)
    v2 = numpy.random.rand(100)
    mse_utilities = utilities.mse(v1, v2)
    mse_sklearn = mean_squared_error(v1, v2)
    logger.debug("MSE(utilities) = %12.8f, MSE(sklearn) = %12.8f" % (mse_utilities, mse_sklearn))
    assert mse_utilities == mse_sklearn


def test_rmse_along_random_vector():
    logger.debug("test_rmse_along_random_vector")
    v1 = numpy.random.rand(100)
    v2 = numpy.random.rand(100)
    rmse_utilities = utilities.rmse(v1, v2)
    rmse_sklearn = numpy.sqrt(mean_squared_error(v1, v2))
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

    zeros = numpy.zeros([9, 9])
    is_quicklook = utilities.make_quicklook_rgb(zeros, zeros, zeros, logger, outfile="zeros.png", vmax=None)
    assert is_quicklook == 0


def test_APU():
    v1 = numpy.array([0.865067,
                      0.467834,
                      0.006436,
                      0.822698,
                      0.500021,
                      0.625819,
                      0.685094,
                      0.684385,
                      0.730635,
                      0.620578,
                      0.382865,
                      0.642284,
                      0.144894,
                      0.505433,
                      0.421729,
                      0.986743,
                      0.961358,
                      0.841948,
                      0.801575,
                      0.937703,
                      0.255979,
                      0.686074,
                      0.796511,
                      0.696359])

    v2 = numpy.array([0.892189,
                      0.479804,
                      0.006296,
                      0.800723,
                      0.519695,
                      0.615373,
                      0.685457,
                      0.711348,
                      0.721573,
                      0.616186,
                      0.372007,
                      0.615052,
                      0.151552,
                      0.499962,
                      0.418653,
                      0.945880,
                      0.915512,
                      0.848146,
                      0.780696,
                      0.906468,
                      0.248680,
                      0.696450,
                      0.834688,
                      0.687994])

    delta = utilities.delta_sr(v1, v2)
    assert utilities.accuracy(delta)    == pytest.approx(0.00415158)
    assert utilities.precision(delta)   == pytest.approx(0.02098248)
    assert utilities.uncertainty(delta) == pytest.approx(0.02095605)