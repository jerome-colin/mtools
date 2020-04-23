"""
Generic product and Venus specific objects definitions

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import zipfile
import sys
import os
import subprocess, shlex
from xml.dom import minidom
import osgeo.gdal as gdal
import glob
import numpy as np


class Product:
    def __init__(self, path, logger, sensor="venus"):
        """
        Create a product object
        :param path: product path or product file name if ptype is ZIP
        :param logger: logger instance
        :param ptype: defaults to "ZIP"
        """
        self.path = path
        self.logger = logger

        # fband_name = [b for b in self.zip_content_list if band in b]

        # Consistency check
        try:
            if zipfile.is_zipfile(self.path):
                logger.info("ZIP file found")
                self.ptype = "ZIP"

            elif os.path.isdir(path):
                logger.info("Directory based product found")
                self.ptype = "DIR"

            elif path[-3:] == "hdf" or path[-3:] == "HDF":
                logger.info("HDF file found")
                self.ptype = "HDF"

            else:
                if os.path.isfile(self.path) == False:
                    logger.error("Unknown product or file not found: %s" % self.path)
                    sys.exit(2)

        except FileNotFoundError as err:
            logger.error(err)
            sys.exit(1)

        self.get_content_list()

    def get_content_list(self):
        if self.ptype == "ZIP":
            self._get_zip_content_list()
            self.name = self.path.split('/')[-1]

        elif self.ptype == "DIR":
            self._get_dir_content_list()

        elif self.ptype == "HDF":
            self._get_hdf_content_list()

        else:
            self.logger.warning("Not yet implemented")

    def _get_dir_content_list(self):
        self.content_list = glob.glob(self.path + '/*')

    def _get_hdf_content_list(self):
        hdf_ds = gdal.Open(self.path, gdal.GA_ReadOnly)
        self.content_list = hdf_ds.GetSubDatasets()

    def _get_zip_content_list(self):
        """
        Creates a zip_content_list attribute with the list of files in a zip archive
        :return:
        """
        with zipfile.ZipFile(self.path, 'r') as zip:
            self.content_list = zip.namelist()
            self.logger.info("Looking into ZIP file content")
            for element in self.content_list:
                self.logger.debug(element)

    def find_band(self, band):
        fband_name = [b for b in self.content_list if band in b]
        if len(fband_name) == 1:
            self.logger.info("Found file %s for band name %s" % (fband_name[0], band))
            return fband_name[0]
        else:
            self.logger.error("No match found for band name %s" % band)
            sys.exit(2)

    def _get_zipped_band_subset_asarray(self, fband, logger, ulx, uly, lrx, lry, scale=True):
        """Extract a Gdal object from an image file, optionally a subset from coordinates
        :param fband: product image file
        :param logger: logging object
        :param ulx: upper left x
        :param uly: upper left y
        :param lrx: lower right x
        :param lry: lower right y
        :return: a numpy array
        """

        try:
            translate = 'gdal_translate -projwin %s %s %s %s /vsizip/%s/%s %s' % (
                ulx, uly, lrx, lry, self.path, fband, ".tmp.tif")
            logger.debug(translate)
            args = shlex.split(translate)
            prog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = prog.communicate()
            logger.debug('Gdal_translate stdout: %s' % out)
            logger.debug('Gdal_translate stderr: %s' % err)
            img = gdal.Open(".tmp.tif")
            os.remove(".tmp.tif")

        except RuntimeError as err:
            logger.error('ERROR: Unable to open ' + fband)
            logger.error(err)
            sys.exit(1)

        if scale:
            if "SRE" in fband:
                return img.ReadAsArray() / self.sre_scalef
        else:
            return img.ReadAsArray()

    def _get_band(self, fband):
        """
        Return a gdal object from an image in a zip archive
        :param fband:
        :return: gdal object
        """
        if self.ptype == "ZIP":
            self.logger.debug('Gdal.Open using /vsizip/%s/%s' % (self.path, fband))
            return gdal.Open('/vsizip/%s/%s' % (self.path, fband))

        elif self.ptype == "DIR":
            self.logger.debug('Gdal.Open using %s' % (fband))
            return gdal.Open('%s' % (fband))

    def get_band_asarray(self, fband):
        img = self._get_band(fband)
        return img.ReadAsArray()


class Acix_maja_product(Product):
    """
    Sub-class of Product for Venus specific methods
    """

    def __init__(self, path, logger):
        super().__init__(path, logger)
        self.band_names = ["SRE_B1.",
                           "SRE_B2.",
                           "SRE_B3.",
                           "SRE_B4.",
                           "SRE_B5.",
                           "SRE_B6.",
                           "SRE_B7.",
                           "SRE_B8.",
                           "SRE_B8A."
                           "SRE_B9.",
                           "SRE_B10.",
                           "SRE_B11.",
                           "SRE_B12.", ]

        self.sre_scalef = 10000
        self.clm_name = "CLM_R1"
        self.edg_name = "EDG_R1"


class Acix_vermote_product(Product):
    """
    Sub-class of Product for Venus specific methods
    """

    def __init__(self, path, logger):
        super().__init__(path, logger)

    def find_band(self, band):
        """
        Overriding mother class method
        :param band:
        :return:
        """
        is_unique = 0
        subds_id = -1
        for b in range(len(self.content_list)):
            subds_name = self.content_list[b][1]
            if subds_name.find(band) != -1:
                subds_id = b
                is_unique += 1
                self.logger.info("Found %s in subdataset %s" % (band, subds_name))

        if is_unique == 0:
            self.logger.error("No subdataset found for band name %s in %s" % (band, self.path))

        if is_unique > 1:
            self.logger.error("Many subdataset found for band name %s in %s" % (band, self.path))

        if is_unique == 1:
            return subds_id

    def get_band_asarray(self, fband):
        """
        Overriding mother class method
        :param fband:
        :return:
        """
        return gdal.Open(self.content_list[fband][0], gdal.GA_ReadOnly).ReadAsArray().astype(np.int16)


class Venus_product(Product):
    """
    Sub-class of Product for Venus specific methods
    """

    def __init__(self, path, logger):
        super().__init__(path, logger)
        self.band_names = ["SRE_B1.",
                           "SRE_B2.",
                           "SRE_B3.",
                           "SRE_B4.",
                           "SRE_B5.",
                           "SRE_B6.",
                           "SRE_B7.",
                           "SRE_B8.",
                           "SRE_B9.",
                           "SRE_B10.",
                           "SRE_B11.",
                           "SRE_B12.", ]

        self.sre_scalef = 1000
        self.clm_name = "CLM_XS"
        self.edg_name = "EDG_XS"

    def parse_metadata(self):
        """
        TODO: adapt to zip files
        :return:
        """
        fname = self.get_metadata_fname()
        self.xml_meta = minidom.parse(fname)

    def get_metadata_fname(self):
        fmeta = [f for f in self.content_list if "MTD_ALL.xml" in f]
        if len(fmeta) == 1:
            self.logger.info("Found metadata file %s" % (fmeta[0]))
            return fmeta[0]
        else:
            self.logger.error("No match found for metadata file")
            sys.exit(2)
