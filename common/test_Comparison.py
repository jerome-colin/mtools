"""
Pytest for Collection

"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.1"

import Collection
import Comparison
import utilities
import numpy
import os

TEST_DATA_PATH = os.environ['TEST_DATA_PATH']


logger = utilities.get_logger('test_Comparison', verbose=True)


def test_Comparison_basic():
    logger.info("test_Comparison")
    acix_maja_collection = Collection.Collection(TEST_DATA_PATH + "acix_carpentras/", logger)
    acix_vermote_collection = Collection.Collection(TEST_DATA_PATH + "vermote_carpentras/", logger)

    compare = Comparison.Comparison(acix_vermote_collection, acix_maja_collection, logger)
    assert compare.matching_products[0][0] == "20171010"
    assert compare.matching_products[0][1] == "/home/colin/code/mtools/test_data/vermote_carpentras/refsrs2-L1C_T31TFJ_A012017_20171010T104021-Carpentras.hdf"
    assert compare.matching_products[0][2] == "/home/colin/code/mtools/test_data/acix_carpentras/SENTINEL2A_20171010-104021-460_L2A_T31TFJ_C_V1-0"
