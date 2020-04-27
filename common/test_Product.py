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

# TEST REFACTORED PRODUCT FROM HERE

## TESTING PRODUCT_DIR (DEFAULT)
def test_product_dir():
    logger.info("TESTING PRODUCT_DIR (DEFAULT)")
    p_dir = Product.Product(TEST_DATA_PATH + "acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0",
                                  logger)
    assert type(p_dir.content_list) is list

    p_dir_filename = p_dir.find_band("SRE_B4.")
    assert p_dir_filename == TEST_DATA_PATH + "acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0_SRE_B4.tif"

    p_dir_band = p_dir.get_band(p_dir.find_band("SRE_B4."))
    assert type(p_dir_band) is numpy.ndarray
    assert p_dir_band[0,0] == 850
    assert p_dir_band[6, 2] == 1249

    b4_subset = p_dir.get_band_subset(p_dir.find_band("SRE_B4."), ulx=649455, uly=4238445, lrx=649465, lry=4238435)
    assert type(b4_subset) is numpy.ndarray

## TEST PRODUCT_ZIP_VENUS
def test_product_zip_venus():
    logger.info("TEST PRODUCT_ZIP_VENUS")
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

## TEST PRODUCT_HDF
def test_product_hdf():
    logger.info("TEST PRODUCT_HDF")
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

## TESTING PRODUCT_DIR_MAJA
def test_product_dir_maja():
    logger.info("TESTING PRODUCT_DIR_MAJA")
    p_dir_maja = Product.Product_dir_maja(TEST_DATA_PATH + "acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0",
                                  logger)
    assert type(p_dir_maja.content_list) is list

    p_dir_b4_filename = p_dir_maja.find_band("SRE_B4.")
    assert p_dir_b4_filename == TEST_DATA_PATH + "acix_carpentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0_SRE_B4.tif"

    p_dir_band = p_dir_maja.get_band(p_dir_b4_filename, scalef=p_dir_maja.sre_scalef)
    assert type(p_dir_band) is numpy.ndarray
    assert p_dir_band[0,0] == 0.0850
    assert p_dir_band[6, 2] == 0.1249

    roi = Roi.Roi([88, 660260, 4887620], 20, logger)
    b4_subset = p_dir_maja.get_band_subset(p_dir_maja.find_band("SRE_B4."), roi=roi, scalef=p_dir_maja.sre_scalef)
    assert type(b4_subset) is numpy.ndarray
    assert b4_subset[0, 0] == 0.1362
    assert b4_subset[1, 0] == 0.1451
    assert b4_subset[0, 1] == 0.1173
    assert b4_subset[1, 1] == 0.1306