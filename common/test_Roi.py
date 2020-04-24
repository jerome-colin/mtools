"""
Pytest for Roi

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import Roi
import Product
import utilities
import numpy
import pytest

TEST_DATA_PATH = "/home/colin/code/mtools/test_data/"

logger = utilities.get_logger('test_Roi', verbose=True)

logger.info("TESTING Roi_collection and Roi instances")
c = Roi.Roi_collection(TEST_DATA_PATH + "demo.csv", 100, logger)
r = Roi.Roi(c.coord_arr[1], 100, logger)

def test_Roi_collection_coord_arr():
    logger.info("test_Roi_collection_coord_arr")
    assert c.coord_arr[1,2] == 4238440

def test_Roi_xy():
    logger.info("test_Roi_xy")
    assert r.ulx == 649410
    assert r.lrx == 649510
    assert r.uly == 4238490
    assert r.lry == 4238390

def test_Roi_id_type():
    logger.info("test_Roi_id_type")
    assert type(r.id) is str

def test_Roi_xy_type():
    logger.info("test_Roi_xy_type")
    assert type(r.ulx) is numpy.float64
    assert type(r.uly) is numpy.float64
    assert type(r.lrx) is numpy.float64
    assert type(r.lry) is numpy.float64


logger.info("TESTING Control pixel values for a subset of 2x2 pixels in band 4")
p_venus = Product.Venus_product(TEST_DATA_PATH + "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)
r_2x2 = Roi.Roi([22,649460,4238440], 10, logger)

p_venus_b4_subset = r_2x2.cut_band(p_venus, "SRE_B4.", logger)

def test_venus_subset_nocloud_type():
    logger.info("test_venus_subset_nocloud_type")
    assert type(p_venus_b4_subset) is numpy.ndarray

def test_product_roi_cut_px_values():
    logger.info("test_product_roi_cut_px_values")
    assert p_venus_b4_subset[0,0] == 0.093
    assert p_venus_b4_subset[1,0] == 0.086
    assert p_venus_b4_subset[0,1] == 0.113
    assert p_venus_b4_subset[1,1] == 0.094

logger.info("TESTING Partly cloudy ROI")
r_partly_cloudy = Roi.Roi([33,678644,4246106], 150, logger)
def test_clm_partly_cloudy_values():
    logger.info("test_clm_partly_cloudy_values")
    clm = r_partly_cloudy.get_mask(p_venus, logger)
    assert type(clm) is numpy.ndarray
    assert numpy.min(clm) == 0
    assert numpy.max(clm) == 1
    assert numpy.sum(clm) == 518

logger.info("TESTING Fully cloudy ROI")
r_fully_cloudy = Roi.Roi([44,679016,4245740], 100, logger)
p_venus_b4_fully_cloudy_subset = r_fully_cloudy.cut_band(p_venus, "SRE_B4.", logger)
p_venus_cml_fully_cloudy_subset = r_fully_cloudy.cut_mask(p_venus, "CLM_XS", logger)

def test_clm_fully_cloudy_type():
    logger.info("test_clm_fully_cloudy_type")
    assert type(p_venus_cml_fully_cloudy_subset) is numpy.ndarray

def test_clm_fully_cloudy_values():
    logger.info("test_clm_fully_cloudy_values")
    clm = r_fully_cloudy.get_mask(p_venus, logger)
    assert type(clm) is numpy.ndarray
    assert numpy.min(clm) == 0
    assert numpy.max(clm) == 0


logger.info("TESTING Statistics for Roi_collection.compute_stats_all_bands")
collection_10m = Roi.Roi_collection(TEST_DATA_PATH + "demo.csv", 10, logger)
list_stats = collection_10m.compute_stats_all_bands(p_venus, logger)

def test_Roi_collection_compute_stats_all_bands():
    logger.info("test_Roi_collection_compute_stats_all_bands")
    assert list_stats[15][0] == 4
    assert list_stats[15][1][0] == 0.086
    assert list_stats[15][1][1] == 0.113
    assert list_stats[15][2] == 0.0965