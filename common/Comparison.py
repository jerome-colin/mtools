"""
Generic comparison class, scenarii can be subclasses

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import os, sys
import numpy
try:
    import Product
    import utilities
except ModuleNotFoundError:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(this_dir)
    import Product
    import utilities

class Comparison:
    def __init__(self, collection1, collection2, logger):
        self.collection1 = collection1
        self.collection2 = collection2
        self.logger = logger

        self._check_products_dims()
        self.matching_products = self.find_matching()

    def _check_products_dims(self):
        pass

    def find_matching(self):
        matching_products = []
        self.logger.debug("Init find_matching...")
        timestamps1 = [item[1] for item in self.collection1.products_timestamps]
        timestamps2 = [item[1] for item in self.collection2.products_timestamps]
        self.logger.debug(timestamps1)
        self.logger.debug(timestamps2)

        for i in range(len(self.collection1.products_timestamps)):
            pid = timestamps2.index((timestamps1[i]))
            matching_products.append([timestamps1[i], self.collection1.products_timestamps[i][0],
                                      self.collection2.products_timestamps[pid][0]])
            self.logger.info("Found matching for %s between %s and %s" %
                             (timestamps1[i], self.collection1.products_timestamps[i][0],
                              self.collection2.products_timestamps[pid][0]))

        self.logger.info("Collections have %i products matching in dates" % len(matching_products))

        return matching_products


class Comparison_acix(Comparison):

    def __init__(self, collection1, collection2, logger):
        super().__init__(collection1, collection2, logger)

        # MAJA: ni B1, ni B9
        # VERMOTE: pas B10
        self.bands_definition_acix = (
            ["SRE_B2.", "band02", "R1"],
            ["SRE_B3.", "band03", "R1"],
            ["SRE_B4.", "band04", "R1"],
            ["SRE_B5.", "band05", "R2"],
            ["SRE_B6.", "band06", "R2"],
            ["SRE_B7.", "band07", "R2"],
            ["SRE_B8.", "band08", "R1"],
            ["SRE_B8A.", "band8a", "R2"],
            ["SRE_B11.", "band11", "R2"],
            ["SRE_B12.", "band12", "R2"])

    def one_by_one(self, save_csv=None):
        # For each matching_product pair (p1, p2)
        #   For each band b
        #       get valid_pixels as a vector (v1, v2) for both
        #       return date, band, rmse

        result = []

        for match in self.matching_products:
            self.logger.info("One-by-one for %s between %s and %s" % (match[0], match[1], match[2]))
            p_ref = Product.Product_hdf_acix(match[1], self.logger)
            p_maja = Product.Product_dir_maja(match[2], self.logger)

            for band in self.bands_definition_acix:
                self.logger.info("Comparing %s with %s" % (band[1], band[0]))
                b_ref = p_ref.get_band(p_ref.find_band(band[1]), scalef=p_ref.sre_scalef)
                b_maja = p_maja.get_band(p_maja.find_band(band[0]), scalef=p_maja.sre_scalef)

                clm = p_maja.get_band(p_maja.find_band("CLM_" + band[2]))
                edg = p_maja.get_band(p_maja.find_band("EDG_" + band[2]))
                mask, ratio = p_maja.get_mask(clm, edg, stats=True)

                b_ref_valid = utilities.is_valid(b_ref, mask)
                b_maja_valid = utilities.is_valid(b_maja, mask)
                self.logger.debug("b_ref_valid shape is %s" % str(numpy.shape(b_ref_valid)))
                self.logger.debug("b_ref_valid shape is %s" % str(numpy.shape(b_maja_valid)))
                rmse = utilities.rmse(b_ref_valid, b_maja_valid)
                self.logger.info("One-by-one comparison RMSE, %s, %s, %s, %8.4f, %4.2f%%" % (match[0], band[1], band[0], rmse, ratio))
                result.append([match[0], band[1], band[0], rmse, ratio, match[1], match[2]])

        if save_csv is not None:
            utilities.write_list_to_file(result, save_csv)

        return result
