"""
Pytest for Collection

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import Collection
import utilities

logger = utilities.get_logger('test_Collection', verbose=True)

venus_collection = Collection.Collection("test_data/venus_collection/", logger)
acix_maja_collection = Collection.Collection("test_data/acix_carpentras/", logger)
acix_vermote_collection = Collection.Collection("test_data/vermote_carpentras/", logger)


def test_discover():
    assert venus_collection.type_count == [2,0,0,0]
    assert acix_vermote_collection.type_count == [0, 6, 0, 0]
    assert acix_maja_collection.type_count == [0, 0, 6, 0]

def test_products_timestamps():
    assert venus_collection.products_timestamps[0][1] == "20200402"
    assert acix_maja_collection.products_timestamps[0][1] == "20171005"
    assert acix_vermote_collection.products_timestamps[0][1] == "20171010"