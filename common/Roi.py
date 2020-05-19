"""
ROI collection and object definitions

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "1.0.1"

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

    def compute_stats_all_bands(self, product, logger, stdout=False, withAOT=False, withVAP=False):
        """
        Print statistiques for all bands of a product for all ROIs in collectoin
        :param product: a Product instance
        :param logger:
        :param quicklook: not yet implemented
        :return:
        """
        # Get the list of bands to compute stats for
        bands = product.band_names

        if withAOT:
            bands.append("AOT.")
        if withVAP:
            bands.append("VAP.")

        list_stats = []

        # For each Roi in Roi_collection:
        for i in range(len(self.coord_arr)):
            # Get an ROI object
            roi_n = Roi(self.coord_arr[i], self.extent, logger)
            # Get the corresponding mask
            clm = product.get_band_subset(product.find_band(product.clm_name), roi=roi_n)
            edg = product.get_band_subset(product.find_band(product.edg_name), roi=roi_n)
            mask = product.get_mask(clm, edg)

            # For each SRE band in product, extract a subset according to ROI and return stats
            for band in bands:
                # samples, minmax, avg, variance, skewness, kurtosis
                band_size = mask.size
                stats = self.compute_stats_oneband(roi_n, product, band, mask=mask)
                list_stats.append(stats)
                if stdout:
                    if stats is not None:
                        print("%s, %s, %s, %i, %i, %6.1f%%, %10.8f, %10.8f, %10.8f, %10.8f" %
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

        if band == "AOT.":
            subset = product.get_band_subset(product.find_band(product.aot_name), roi=roi, scalef=product.aot_scalef, layer=product.aot_layer)
        elif band == "VAP.":
            subset = product.get_band_subset(product.find_band(product.vap_name), roi=roi, scalef=product.vap_scalef, layer=product.vap_layer)
        else:
            subset = product.get_band_subset(product.find_band(band), roi=roi, scalef=product.sre_scalef)

        if mask is not None:
            search = np.where(mask == 1)
            valid_pixels = subset[search]
        else:
            valid_pixels = subset

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
