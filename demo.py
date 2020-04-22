# mtools common tests
# require : test_data/ directory


__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import sys
import argparse
import zipfile
import numpy as np
from scipy import stats

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

    logger.info("Test common.Product.get_zip_content_list...")
    vns_product._get_zip_content_list()

    logger.info("Test common.Product.get_zip_content_list...")
    b3_name = vns_product._get_zipped_band_filename("SRE_B3")

    logger.info("Test common.Product.get_zipped_band_asarray...")
    b3_img = vns_product._get_zipped_band_asarray(vns_product._get_zipped_band_filename("SRE_B3"))
    clm_img = vns_product._get_zipped_band_asarray(vns_product._get_zipped_band_filename(vns_product.clm_name))
    edg_img = vns_product._get_zipped_band_asarray(vns_product._get_zipped_band_filename(vns_product.edg_name))

    logger.info("Test common.Product.get_zipped_band_subset_asarray...")
    b7_subset_from_zip = vns_product._get_zipped_band_subset_asarray(vns_product._get_zipped_band_filename("SRE_B7"), logger, ulx=658528,
                                                                     uly=4244035, lrx=664529, lry=4238421)
    b4_subset_from_zip = vns_product._get_zipped_band_subset_asarray(vns_product._get_zipped_band_filename("SRE_B4"), logger, ulx=658528,
                                                                     uly=4244035, lrx=664529, lry=4238421)
    b2_subset_from_zip = vns_product._get_zipped_band_subset_asarray(vns_product._get_zipped_band_filename("SRE_B2"), logger, ulx=658528,
                                                                     uly=4244035, lrx=664529, lry=4238421)

    logger.info("Test common.Product.get_quicklook...")
    utl.make_quicklook_rgb(b7_subset_from_zip, b4_subset_from_zip, b2_subset_from_zip, logger, outfile='test_data/test.png')


    logger.info("Test common.Roi.Roi_collection.__init__...")
    roi_collection = common.Roi.Roi_collection(args.coordinates, args.extent, logger)

    logger.info("Test common.Roi.Roi.__init__...")
    for i in range(len(roi_collection.coord_arr)):
        roi_n = common.Roi.Roi(roi_collection.coord_arr[i],roi_collection.extent, logger)

    logger.info("Test common.Roi.Roi.cut_band...")
    sample_B2 = roi_n.cut_band(vns_product,"SRE_B2", logger)
    sample_B4 = roi_n.cut_band(vns_product, "SRE_B4", logger)
    sample_B7 = roi_n.cut_band(vns_product, "SRE_B7", logger)
    utl.make_quicklook_rgb(sample_B7, sample_B4, sample_B2, logger, outfile='test_data/roi_sample_test.png')

    roi_collection.compute_stats_all_bands(vns_product, logger)

    sys.exit(0)


if __name__ == "__main__":
    main()
