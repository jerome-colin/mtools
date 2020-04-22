"""
Pytest for Product

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import Product
import utilities
import numpy
from matplotlib import pylab as pl

logger = utilities.get_logger('test_Product', verbose=True)

generic_product = Product.Product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

def test_product_name():
    logger.info("test_product_name")
    assert generic_product.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

def test_product_type():
    logger.info("test_product_type")
    assert generic_product.ptype == "ZIP"

venus_product = Product.Venus_product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

def test_venus_product_name():
    logger.info("test_venus_product_name")
    assert venus_product.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

def test_get_band_filename_from_zip():
    logger.info("test_get_band_filename_from_zip")
    fname = venus_product.get_band_filename("SRE_B4.")
    assert fname == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_C_V2-2/VENUS-XS_20200402-191352-000_L2A_GALLOP30_C_V2-2_SRE_B4.tif"

def test_get_venus_band_asarray():
    logger.info("test_get_venus_band_asarray")
    venus_band_asarray = venus_product.get_band_asarray(venus_product.get_band_filename("SRE_B4."))
    assert type(venus_band_asarray) is numpy.ndarray

dir_product = Product.Product("test_data/acix_captentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0", logger)

def test_dir_product_type():
    logger.info("test_dir_product_type")
    assert dir_product.ptype == "DIR"

def test_dir_content_list():
    logger.info("test_dir_content_list")
    assert type(dir_product.content_list) is list

def test_get_band_filename_from_dir():
    logger.info("test_get_band_filename_from_dir")
    fname = dir_product.get_band_filename("SRE_B4.")
    assert fname == "test_data/acix_captentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0_SRE_B4.tif"

def test_get_venus_band_asarray():
    logger.info("test_get_venus_band_asarray")
    dir_band_asarray = dir_product.get_band_asarray(dir_product.get_band_filename("SRE_B4."))
    assert type(dir_band_asarray) is numpy.ndarray
