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
            if len(self.coord_arr) == 0:
                self.logger.error("Coordinates file empty ?")
                sys.exit(2)

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
            mask = roi_n.get_mask(product, logger)

            # For each band in product, extract a subset according to ROI and return stats
            for band in bands:
                # samples, minmax, avg, variance, skewness, kurtosis

                band_size = mask.size

                stats = self.compute_stats_oneband(roi_n, product, band, mask=mask)
                list_stats.append(stats)
                if stdout:
                    if stats is not None:
                        print("%s, %s, %s, %i, %i, %6.1f%%, %6.4f, %6.4f, %6.4f, %6.4f" %
                              (product.name, roi_n.id, band[:-1], band_size, stats[0], stats[0]/band_size*100, stats[1][0], stats[1][1], stats[2], stats[3]))
                    else:
                        print("%s, %s, %s, no valid pixel in ROI (fully cloudy or out of edge)" % (product.name, roi_n.id, band[:-1]))

        return list_stats

    def compute_stats_oneband(self, roi, product, band, mask=None):
        """

        :param roi: Roi object
        :param product: Product object
        :param band: a string that helps identify a file
        :return:
        """
        subset = roi.cut_band(product, band, self.logger)
        if mask is not None:
            search = np.where(mask == 1)
            valid_pixels = subset[search]

        try:
            return stats.describe(valid_pixels, axis=None)
        except ValueError:
            return None


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
        :param band: a string that helps identify a file
        :param logger:
        :return: a numpy array
        """
        return product._get_zipped_band_subset_asarray(
            product.find_band(band), logger, ulx=self.ulx,
            uly=self.uly, lrx=self.lrx, lry=self.lry) / product.sre_scalef

    def cut_mask(self, product, band, logger):
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

    def get_mask(self, product, logger):
        # Get once the clm if any
        clm = self.cut_mask(product, product.clm_name, logger)
        edg = self.cut_mask(product, product.edg_name, logger)
        mask = clm + edg

        dummy = np.zeros_like(clm) + 1
        search = np.where(mask != 0)
        dummy[search] = 0

        logger.debug("mask_NaNsum=%i, dummy_NaNsum=%i" % (np.nansum(mask), np.nansum(dummy)))

        return dummy