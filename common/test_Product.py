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

### TESTING Generic products

generic_product = Product.Product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

def test_product_name():
    logger.info("test_product_name")
    assert generic_product.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

def test_product_type():
    logger.info("test_product_type")
    assert generic_product.ptype == "ZIP"

### TESTING Venus product

venus_product = Product.Venus_product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

def test_venus_product_name():
    logger.info("test_venus_product_name")
    assert venus_product.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

def test_find_band_from_zip():
    logger.info("test_find_band_from_zip")
    fname = venus_product.find_band("SRE_B4.")
    assert fname == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_C_V2-2/VENUS-XS_20200402-191352-000_L2A_GALLOP30_C_V2-2_SRE_B4.tif"

def test_get_venus_band_asarray():
    logger.info("test_get_venus_band_asarray")
    venus_band_asarray = venus_product.get_band_asarray(venus_product.find_band("SRE_B4."))
    assert type(venus_band_asarray) is numpy.ndarray

### TESTING Directory based product (actually acix maja)

dir_product = Product.Product("test_data/acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0", logger)

def test_dir_product_type():
    logger.info("test_dir_product_type")
    assert dir_product.ptype == "DIR"

def test_dir_content_list():
    logger.info("test_dir_content_list")
    assert type(dir_product.content_list) is list

def test_get_band_filename_from_dir():
    logger.info("test_get_band_filename_from_dir")
    fname = dir_product.find_band("SRE_B4.")
    assert fname == "test_data/acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0_SRE_B4.tif"

def test_get_band_dir_asarray_type():
    logger.info("test_get_band_dir_asarray_type")
    dir_band_asarray = dir_product.get_band_asarray(dir_product.find_band("SRE_B4."))
    assert type(dir_band_asarray) is numpy.ndarray

def test_get_band_dir_asarray_value():
    dir_band_asarray = dir_product.get_band_asarray(dir_product.find_band("SRE_B4."))
    assert dir_band_asarray[0,0] == 850
    assert dir_band_asarray[6, 2] == 1249


### TESTING HDF Vermote product

hdf_product = Product.Acix_vermote_product("test_data/vermote_carpentras/refsrs2-L1C_T31TFJ_A003037_20171005T104550-Carpentras.hdf", logger)

def test_hdf_product_type():
    logger.info("test_hdf_product_type")
    assert hdf_product.ptype == "HDF"

def test_hdf_content_list():
    logger.info("test_hdf_content_list")
    logger.debug(type(hdf_product.content_list))
    logger.debug(hdf_product.content_list)
    assert type(hdf_product.content_list) is list

def test_find_band_hdf():
    logger.info("test_find_band_hdf")
    subdsid = hdf_product.find_band("band04-red")
    logger.debug("Tested and found %i" % subdsid)
    assert type(subdsid) is int
    assert subdsid == 3

def test_get_hdf_band_asarray_type():
    logger.info("test_get_hdf_band_asarray_type")
    assert type(hdf_product.get_band_asarray(hdf_product.find_band("band04-red"))) is numpy.ndarray

def test_get_hdf_band_asarray_values():
    logger.info("test_get_hdf_band_asarray_values")
    assert hdf_product.get_band_asarray(hdf_product.find_band("band04-red"))[0][0] == 596
    assert hdf_product.get_band_asarray(hdf_product.find_band("band04-red"))[6][2] == 1096