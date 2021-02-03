"""
Pytest for Collection

"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.3"

import Collection
import Comparison
import utilities
import os

TEST_DATA_PATH = os.environ['TEST_DATA_PATH']


logger = utilities.get_logger('test_Comparison', verbose=True)


def test_Comparison_basic():
    logger.info("test_Comparison")
    acix_maja_collection = Collection.Collection(TEST_DATA_PATH + "acix_carpentras/", logger)
    acix_vermote_collection = Collection.Collection(TEST_DATA_PATH + "vermote_carpentras/", logger)

    compare = Comparison.Comparison(acix_vermote_collection, acix_maja_collection, logger)
    assert sorted(compare.matching_products, key = lambda x: x[1])[0][0] == "20171005"
    assert sorted(compare.matching_products, key = lambda x: x[1])[0][1] == TEST_DATA_PATH + "vermote_carpentras/refsrs2-L1C_T31TFJ_A003037_20171005T104550-Carpentras.hdf"
    assert sorted(compare.matching_products, key = lambda x: x[1])[0][2] == TEST_DATA_PATH + "acix_carpentras/SENTINEL2B_20171005-104550-197_L2A_T31TFJ_C_V1-0"
