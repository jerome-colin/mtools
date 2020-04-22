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
    """
    A collection of ROIs defined according to the coordinate file given to roistats
    """

    def __init__(self, fname, extent, logger, delimiter=','):
        """

        :param fname: the coordinate file
        :param extent: in mters
        :param logger:
        :param delimiter:
        """

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

    def compute_stats_all_bands(self, product, logger, stdout=False):
        """
        Print statistiques for all bands of a product for all ROIs in collectoin
        :param product: a Product instance
        :param logger:
        :param quicklook: not yet implemented
        :return:
        """
        # Get the list of bands to compute stats for
        bands = product.band_names

        list_stats = []

        # For each Roi in Roi_collection:
        for i in range(len(self.coord_arr)):
            # Get an ROI object
            roi_n = Roi(self.coord_arr[i], self.extent, logger)

            # For each band in product, extract a subset according to ROI and return stats
            for band in bands:
                # samples, minmax, avg, variance, skewness, kurtosis
                stats = self.compute_stats_oneband(roi_n, product, band)
                list_stats.append(stats)
                if stdout:
                    print("%s, %s, %s, %i, %6.4f, %6.4f, %6.4f, %6.4f, %6.4f, %6.4f" %
                          (product.name, roi_n.id, band[:-1], stats[0], stats[1][0], stats[1][1], stats[2], stats[3],
                           stats[4],
                           stats[5]))

        return list_stats

    def compute_stats_oneband(self, roi, product, band):
        subset = roi.cut_band(product, band, self.logger)
        return stats.describe(subset, axis=None)


class Roi:
    def __init__(self, id_utmx_utmy, extent, logger):
        """
        Returns an ROI instance
        :param id_utmx_utmy: a vector containing an id(int), utmx(float) and utmy(float).
        :param extent: in meters
        :param logger:
        """
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

    def cut_band(self, product, band, logger):
        """
        Returns a numpy array of a given band of a given product cut to fit the ROI
        :param product: a Product instance
        :param band: a string that helps identify a file in the zipped Product
        :param logger:
        :return: a numpy array
        """
        return product._get_zipped_band_subset_asarray(
            product.find_band(band), logger, ulx=self.ulx,
            uly=self.uly, lrx=self.lrx, lry=self.lry)

    def get_stacked_asarray(self, product, logger):
        pass
        # TODO: this

        # bands = product.band_names
        #
        # for band in bands:
        #     subset = self.cut_band(product, band, logger)
        #     samples, minmax, avg, variance, skewness, kurtosis = stats.describe(subset, axis=None)
        #     print(
        #         "ROI id %s, band %s, samples=%i, min=%6.4f, max=%6.4f, avg=%6.4f, variance=%6.4f, skewness=%6.4f, kurtosis=%6.4f" %
        #         (self.id, band, samples, minmax[0], minmax[1], avg, variance, skewness, kurtosis))
