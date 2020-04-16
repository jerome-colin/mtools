# mtools common tests
# require : test_data/ directory


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
    logger = utl.get_logger('tests', args.verbose)

    logger.info("Test common.Product.__init__...")
    vns_product = common.Product.Venus_product(args.product, logger)

    logger.info("Test common.Roi.Roi_collection.__init__...")
    roi_collection = common.Roi.Roi_collection(args.coordinates, args.extent, logger)

    logger.info("Test common.Product.get_zip_content_list...")
    vns_product.get_zip_content_list()

    logger.info("Test common.Product.get_zip_content_list...")
    b3_name = vns_product.get_zipped_band_filename("SRE_B3")

    logger.info("Test common.Product.get_zipped_band_asarray...")
    b3_img = vns_product.get_zipped_band_asarray(vns_product.get_zipped_band_filename("SRE_B3"))
    clm_img = vns_product.get_zipped_band_asarray(vns_product.get_zipped_band_filename("CLM_XS"))
    edg_img = vns_product.get_zipped_band_asarray(vns_product.get_zipped_band_filename("EDG_XS"))

    logger.info("Test common.Product.get_zipped_band_subset_asarray...")
    b7_subset_from_zip = vns_product.get_zipped_band_subset_asarray(vns_product.get_zipped_band_filename("SRE_B7"), logger, ulx=658528,
                                                          uly=4244035, lrx=664529, lry=4238421)
    b4_subset_from_zip = vns_product.get_zipped_band_subset_asarray(vns_product.get_zipped_band_filename("SRE_B4"), logger, ulx=658528,
                                                          uly=4244035, lrx=664529, lry=4238421)
    b2_subset_from_zip = vns_product.get_zipped_band_subset_asarray(vns_product.get_zipped_band_filename("SRE_B2"), logger, ulx=658528,
                                                          uly=4244035, lrx=664529, lry=4238421)

    logger.info("Test common.Product.get_quicklook...")
    vns_product.make_quicklook(b7_subset_from_zip, b4_subset_from_zip, b2_subset_from_zip, logger, outfile='test_data/test.png')


    sys.exit(0)


if __name__ == "__main__":
    main()
