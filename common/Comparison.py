"""
Generic comparison class, scenarii can be subclasses

"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "1.0.2"

import os, sys
import numpy as np

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


