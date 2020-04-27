"""
Pytest for Product

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import Product
import Roi
import utilities
import numpy
import osgeo.gdal
from matplotlib import pylab as pl

TEST_DATA_PATH = "/home/colin/code/mtools/test_data/"

logger = utilities.get_logger('test_Product', verbose=True)

### TESTING Generic products

generic_product = Product.Product(TEST_DATA_PATH + "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

def test_product_name():
    logger.info("test_product_name")
    assert generic_product.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

def test_product_type():
    logger.info("test_product_type")
    assert generic_product.ptype == "ZIP"

### TESTING Venus product

venus_product = Product.Venus_product(TEST_DATA_PATH + "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

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

def test_get_venus_mask_asarray():
    logger.info("test_get_venus_mask_asarray")
    venus_mask_asarray = venus_product.get_band_asarray(venus_product.find_band("CLM_XS"))
    assert type(venus_mask_asarray) is numpy.ndarray

### TESTING Directory based product (actually acix maja)

dir_product = Product.Product(TEST_DATA_PATH + "acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0", logger)

def test_dir_product_type():
    logger.info("test_dir_product_type")
    assert dir_product.ptype == "DIR"

def test_dir_content_list():
    logger.info("test_dir_content_list")
    assert type(dir_product.content_list) is list

def test_get_band_filename_from_dir():
    logger.info("test_get_band_filename_from_dir")
    fname = dir_product.find_band("SRE_B4.")
    assert fname == TEST_DATA_PATH + "acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0_SRE_B4.tif"

def test_get_band_dir_asarray_type():
    logger.info("test_get_band_dir_asarray_type")
    dir_band_asarray = dir_product.get_band_asarray(dir_product.find_band("SRE_B4."))
    assert type(dir_band_asarray) is numpy.ndarray

def test_get_band_dir_asarray_value():
    dir_band_asarray = dir_product.get_band_asarray(dir_product.find_band("SRE_B4."))
    assert dir_band_asarray[0,0] == 850
    assert dir_band_asarray[6, 2] == 1249





# TEST REFACTORED PRODUCT FROM HERE

## TEST REFACTORED PRODUCT_ZIP_VENUS
def test_product_zip_venus():
    logger.info("test_product_zip_venus")
    p_zip_venus = Product.Product_zip_venus(TEST_DATA_PATH + "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)
    assert p_zip_venus.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"
    assert p_zip_venus.band_names[0] == "SRE_B1."
    assert p_zip_venus.clm_name == "CLM_XS"
    assert p_zip_venus.edg_name == "EDG_XS"

    logger.info("test_product_zip_venus_get_content_list")
    b4_filename = p_zip_venus.find_band("SRE_B4.")
    assert b4_filename == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_C_V2-2/VENUS-XS_20200402-191352-000_L2A_GALLOP30_C_V2-2_SRE_B4.tif"

    logger.info("test_product_zip_venus_get_band")
    b4 = p_zip_venus.get_band(b4_filename)
    assert type(b4) is numpy.ndarray

    logger.info("test_product_zip_venus_get_band_subset")
    b4_subset = p_zip_venus.get_band_subset(b4_filename, ulx=649455, uly=4238445, lrx=649465, lry=4238435)
    assert type(b4_subset) is numpy.ndarray
    assert b4_subset[0, 0] == 93
    assert b4_subset[1, 0] == 86
    assert b4_subset[0, 1] == 113
    assert b4_subset[1, 1] == 94
    assert p_zip_venus.sre_scalef == 1000
    b4_subset_SRE = p_zip_venus.get_band_subset(b4_filename, ulx=649455, uly=4238445, lrx=649465, lry=4238435, scalef=p_zip_venus.sre_scalef)
    assert b4_subset_SRE[0, 0] == 0.093
    assert b4_subset_SRE[1, 0] == 0.086
    assert b4_subset_SRE[0, 1] == 0.113
    assert b4_subset_SRE[1, 1] == 0.094

    logger.info("test_product_zip_venus_get_band_subset_withROI")
    roi = Roi.Roi([99, 649460, 4238440], 10, logger)
    b4_subset_SRE = p_zip_venus.get_band_subset(b4_filename, roi=roi, scalef=p_zip_venus.sre_scalef)
    assert b4_subset_SRE[0, 0] == 0.093
    assert b4_subset_SRE[1, 0] == 0.086
    assert b4_subset_SRE[0, 1] == 0.113
    assert b4_subset_SRE[1, 1] == 0.094

## TEST REFARCTORED PRODUCT_HDF

### TESTING HDF Vermote product

def test_product_hdf():
    p_hdf_vermote = Product.Product_hdf(TEST_DATA_PATH + "vermote_carpentras/refsrs2-L1C_T31TFJ_A003037_20171005T104550-Carpentras.hdf", logger)

    assert p_hdf_vermote.ptype == "HDF"

    logger.info("test_product_hdf_content_list")
    logger.debug(type(p_hdf_vermote.content_list))
    logger.debug(p_hdf_vermote.content_list)
    assert type(p_hdf_vermote.content_list) is list

    logger.info("test_product_hdf_find_band")
    subdsid = p_hdf_vermote.find_band("band04-red")
    assert type(subdsid) is int
    assert subdsid == 3

    logger.info("test_product_hdf_get_band")
    assert type(p_hdf_vermote.get_band(p_hdf_vermote.find_band("band04-red"))) is numpy.ndarray
    assert p_hdf_vermote.get_band(p_hdf_vermote.find_band("band04-red"))[0][0] == 596
    assert p_hdf_vermote.get_band(p_hdf_vermote.find_band("band04-red"))[6][2] == 1096