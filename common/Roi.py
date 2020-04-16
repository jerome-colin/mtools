import numpy as np
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

    def compute_stats_all_bands(self, product, logger):
        pass

class Roi:
    def __init__(self, id_utmx_utmy, extent, logger):
        self.id = str(id_utmx_utmy[0])
        self.utmx = id_utmx_utmy[1]
        self.utmy = id_utmx_utmy[2]
        self.extent = extent

        # Compute ulx, uly, lrx, lry assuming UTM coordinates
        self.ulx = self.utmx - self.extent
        self.uly = self.utmy + self.extent
        self.lrx = self.utmx + self.extent
        self.lry = self.utmy - self.extent

        logger.info('ROI id %s: ulx=%i, uly=%i, lrx=%i, lry=%i' % (self.id, self.ulx, self.uly, self.lrx, self.lry))