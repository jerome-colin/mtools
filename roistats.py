#!/usr/bin/env python3
"""
Compute statistics over a square ROI

Require: see mtools.yml for conda environment configuration

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
import argparse
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
    vns_product = common.Product.Product_zip_venus(args.product, logger)

    # Create an roi collection
    roi_collection = common.Roi.Roi_collection(args.coordinates, args.extent, logger)

    # Compute statistics for a given product
    list_stats = roi_collection.compute_stats_all_bands(vns_product, logger, stdout=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
