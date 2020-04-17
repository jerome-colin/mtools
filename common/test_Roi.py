import Roi
import Product
import utilities
import numpy

logger = utilities.get_logger('test_Roi', verbose=True)

### TESTING Roi_collection and Roi instances
c = Roi.Roi_collection("test_data/demo.csv", 100, logger)
r = Roi.Roi(c.coord_arr[1], 100, logger)

def test_Roi_collection_coord_arr():
    assert c.coord_arr[1,2] == 4238440

def test_Roi_xy():
    assert r.ulx == 649410
    assert r.lrx == 649510
    assert r.uly == 4238490
    assert r.lry == 4238390

def test_Roi_id_type():
    assert type(r.id) is str

def test_Roi_xy_type():
    assert type(r.ulx) is numpy.float64
    assert type(r.uly) is numpy.float64
    assert type(r.lrx) is numpy.float64
    assert type(r.lry) is numpy.float64


### TESTING Control pixel values for a subset of 2x2 pixels in band 4
p_venus_b4 = Product.Venus_product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger, ptype="ZIP")
r_2x2 = Roi.Roi([22,649460,4238440], 10, logger)

p_venus_b4_subset = r_2x2.cut_band(p_venus_b4, "SRE_B4.", logger)

def test_product_roi_cut_px_values():
    assert p_venus_b4_subset[0,0] == 0.093
    assert p_venus_b4_subset[1,0] == 0.086
    assert p_venus_b4_subset[0,1] == 0.113
    assert p_venus_b4_subset[1,1] == 0.094
