"""
Pytest for Collection

"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.2"

import Collection
import utilities
import os

TEST_DATA_PATH = os.environ['TEST_DATA_PATH']


logger = utilities.get_logger('test_Collection', verbose=True)

venus_collection = Collection.Collection(TEST_DATA_PATH + "venus_collection/", logger)
acix_maja_collection = Collection.Collection(TEST_DATA_PATH + "acix_carpentras/", logger)
acix_vermote_collection = Collection.Collection(TEST_DATA_PATH + "vermote_carpentras/", logger)


def test_discover():
    assert venus_collection.type_count == [2,0,0,0]
    assert acix_vermote_collection.type_count == [0, 6, 0, 0]
    assert acix_maja_collection.type_count == [0, 0, 6, 0]

def test_products_timestamps():
    assert sorted(venus_collection.products_timestamps, key = lambda x: x[1])[0][1] == "20200402"
    assert sorted(acix_maja_collection.products_timestamps, key = lambda x: x[1])[0][1] == "20171005"
    assert sorted(acix_maja_collection.products_timestamps, key=lambda x: x[1])[-1][1] == "20171030"
    assert sorted(acix_vermote_collection.products_timestamps, key = lambda x: x[1])[0][1] == "20171005"
    assert sorted(acix_vermote_collection.products_timestamps, key=lambda x: x[1])[-1][1] == "20171030"