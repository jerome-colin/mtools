"""
ROI collection and object definitions

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import numpy as np
from scipy import stats
import sys

class Roi_collection:
    def __init__(self, fname, extent, logger, delimiter=','):

        self.fname = fname
        self.extent = extent
        self.logger = logger
        self.delimiter = delimiter

        self.logger.info("Checking coordinates consistency...")
        try:
            self.coord_arr = np.loadtxt(self.fname, delimiter=self.delimiter)
            self.logger.info("Found %i coordinates pairs" % (len(self.coord_arr)))
            for c in range(len(self.coord_arr)):
                self.logger.debug(self.coord_arr[c])

        except ValueError as err:
            self.logger.error(err)
            self.logger.error("Wrong value in coordinates file (or un-managed header line)")
            sys.exit(2)

        except FileNotFoundError as err:
            self.logger.error(err)
            sys.exit(1)

        # Extent value consistency check
        self.logger.info("Checking extent value consistency...")
        if self.extent <= 0:
            self.logger.error("Wrong extent given : %i" % self.extent)
            sys.exit(2)

    def compute_stats_all_bands(self, product, logger, quicklook=False):
        # Get the list of bands to compute stats for
        bands = product.get_bands()

        # For each Roi in Roi_collection:
        for i in range(len(self.coord_arr)):
            # Get an ROI object
            roi_n = Roi(self.coord_arr[i], self.extent, logger)

            # For each band in product, extract a subset according to ROI and return stats
            for band in bands:
                subset = product.get_zipped_band_subset_asarray(
                    product.get_zipped_band_filename(band), logger, ulx=roi_n.ulx,
                    uly=roi_n.uly, lrx=roi_n.lrx, lry=roi_n.lry)
                samples, minmax, avg, variance, skewness, kurtosis = stats.describe(subset, axis=None)
                print("ROI id %s, band %s, samples=%i, min=%6.2f, max=%6.2f, avg=%6.2f, variance=%6.2f, skewness=%6.2f, kurtosis=%6.2f" %
                      (roi_n.id, band, samples, minmax[0], minmax[1], avg, variance, skewness, kurtosis))


class Roi:
    def __init__(self, id_utmx_utmy, extent, logger):
        self.id = str(int(id_utmx_utmy[0]))
        self.utmx = id_utmx_utmy[1]
        self.utmy = id_utmx_utmy[2]
        self.extent = extent

        # Compute ulx, uly, lrx, lry assuming UTM coordinates
        self.ulx = self.utmx - self.extent / 2
        self.uly = self.utmy + self.extent / 2
        self.lrx = self.utmx + self.extent / 2
        self.lry = self.utmy - self.extent / 2

        logger.info('ROI id %s: ulx=%i, uly=%i, lrx=%i, lry=%i' % (self.id, self.ulx, self.uly, self.lrx, self.lry))