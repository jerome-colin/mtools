#!/usr/bin/env python3
"""
Compute statistics over a square ROI

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
import argparse
import zipfile
import numpy as np
import gdal
from matplotlib import pylab as pl
import common.utilities as utl
import common.Product
import common.Roi


def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("product", help="Venus product (ZIP)")
    parser.add_argument("coordinates", help="coordinate file")
    parser.add_argument("-e", "--extent", type=int, \
                        help="extent of the square ROI (meters), defaults to 100", default=100)
    parser.add_argument("-v", "--verbose", help="Set verbosity to DEBUG level", action="store_true", default=False)
    args = parser.parse_args()

    # Create the logger
    logger = utl.get_logger('roistats', args.verbose)

    # Create a Venus product object
    logger.info("Checking arguments consistency...")
    vns_product = common.Product.Venus_product(args.product, logger)

    # Create an roi collection
    roi_collection = common.Roi.Roi_collection(args.coordinates, args.extent, logger)

    # Compute statistics for a given product
    roi_collection.compute_stats_all_bands(vns_product, logger)

    sys.exit(0)


if __name__ == "__main__":
    main()
