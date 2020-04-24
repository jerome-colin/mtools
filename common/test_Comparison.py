import Collection
import Comparison
import utilities

logger = utilities.get_logger('test_Comparison', verbose=True)


acix_maja_collection = Collection.Collection("test_data/acix_carpentras/", logger)
acix_vermote_collection = Collection.Collection("test_data/vermote_carpentras/", logger)

compare = Comparison.Comparison(acix_vermote_collection, acix_maja_collection, logger)

def test_Comparison_basic():
    pass