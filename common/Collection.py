"""
Collection of product objects definitions

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import os, sys
import numpy as np
import re

class Collection:

    def __init__(self, path, logger):
        self.path = path
        self.logger = logger
        self.content_list = self._discover()
        self.products_timestamps = self._get_products_timestamps()

    def _discover(self):
        """
        Create a product content_list
        :return: a list
        """
        items = os.listdir(self.path)

        self.type_count = self._get_items_count_by_type(items)
        self.logger.debug("Found %i ZIP, %i HDF, %i DIR, %i UNKNOWN" %
                          (self.type_count[0], self.type_count[1], self.type_count[2], self.type_count[3]))

        self.type_max = np.argmax(self.type_count)
        self.logger.debug("Maximum items of type %i" % self.type_max)

        product_list = self._get_product_list(items, self.type_max)
        self.logger.info(product_list)

        return product_list

    def _get_items_count_by_type(self, items):
        """
        Identify the most likely product type in between zip, hdf and dir
        :param items:
        :return: type_count, 4 elements vector counting occurences of [zip, hdf, dir, unknown]
        """
        type_count = [0, 0, 0, 0] # ZIP, HDF, DIR, UKW
        for item in items:
            self.logger.debug("Checking item %s" % item)
            if os.path.isfile(self.path + item):
                self.logger.debug("%s is a file with extension %s" % (item, item[-3:]))
                if item[-3:] == "zip" or item[-3:] == "ZIP":
                    type_count[0] += 1
                elif item[-3:] == "hdf" or item[-3:] == "HDF":
                    type_count[1] += 1
                else:
                    type_count[3] += 1
            elif os.path.isdir(self.path + item):
                type_count[2] += 1
                self.logger.debug("%s is a directory" % item)

        return type_count

    def _get_product_list(self, items, type_max):
        """
        Return a list of products of a given type
        :param items:
        :param type_max:
        :return: a list
        """
        product_list = []
        if type_max == 0:
            for item in items:
                if os.path.isfile(self.path + item) and (item[-3:] == "zip" or item[-3:] == "ZIP"):
                    product_list.append(item)

        elif type_max == 1:
            for item in items:
                if os.path.isfile(self.path + item) and (item[-3:] == "hdf" or item[-3:] == "HDF"):
                    product_list.append(item)

        elif type_max == 2:
            for item in items:
                if os.path.isdir(self.path + item):
                    product_list.append(item)

        else:
            self.logger.error("No any recognized product in collection path %s" % self.path)
            sys.exit(2)

        return product_list

    def _get_products_timestamps(self):
        """
        Identify a YYYYMMDD pattern in product names of Collection
        :return: a list of [product name, YYYYMMDD]
        """
        products_date = []
        for item in self.content_list:
            self.logger.debug("Looking for timestamp in %s" % item)
            numbers = re.findall(r'[0-9]{8}', item)
            if len(numbers) != 1:
                self.logger.warning("Found many date patterns for item %s: %s" % (item, numbers))
            else:
                products_date.append([item, numbers[0]])

        self.logger.debug(products_date)
        return  products_date
