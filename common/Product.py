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

        #fband_name = [b for b in self.zip_content_list if band in b]

        # Consistency check
        try:
            if zipfile.is_zipfile(self.path):
                logger.info("Valid ZIP file found")
                self.ptype = "ZIP"


            elif os.path.isdir(path):
                logger.info("Valid directory found")
                self.ptype = "DIR"

            else:
                logger.error("Unknown product")

            self.get_content_list()

        except FileNotFoundError as err:
            logger.error(err)
            sys.exit(1)

    def get_content_list(self):
        if self.ptype == "ZIP":
            self._get_zip_content_list()
            self.name = self.path.split('/')[-1]

        elif self.ptype == "DIR":
            self._get_dir_content_list()

        else:
            self.logger.warning("Not yet implemented")

    def _get_dir_content_list(self):
        self.content_list = glob.glob(self.path + '/*')

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

    def _get_zipped_band_filename(self, band):
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

    def _get_zipped_band(self, fband):
        """
        Return a gdal object from an image in a zip archive
        :param fband:
        :return: gdal object
        """
        self.logger.debug('Gdal.Open using /vsizip/%s/%s' % (self.path, fband))
        return gdal.Open('/vsizip/%s/%s' % (self.path, fband))

    def _get_zipped_band_asarray(self, fband):
        img = self._get_zipped_band(fband)
        return img.ReadAsArray()


class Maja_acix_product(Product):
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
                           "SRE_B12.",]

        self.sre_scalef = 10000
        self.clm_name = "CLM_R1"
        self.edg_name = "EDG_R1"


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
                           "SRE_B12.",]

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
