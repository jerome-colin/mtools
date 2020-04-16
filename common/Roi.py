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

class Roi:
    def __init__(self, latlon, extent):
        pass