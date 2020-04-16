import zipfile
import sys
import os
import subprocess, shlex
from xml.dom import minidom
import gdal
import numpy as np
from PIL import Image as pillow

class Product:
    def __init__(self, path, logger, ptype="ZIP"):
        """
        Create a product object
        :param path: product path or product file name if ptype is ZIP
        :param logger: logger instance
        :param ptype: defaults to "ZIP"
        """
        self.path = path
        self.logger = logger
        self.ptype = ptype

        # Consistency check
        if self.ptype == "ZIP":
            try:
                if zipfile.is_zipfile(self.path):
                    logger.info("Valid ZIP file found")
                    self.get_zip_content_list()
                else:
                    logger.error("Invalid ZIP file found")
                    sys.exit(2)

            except FileNotFoundError as err:
                logger.error(err)
                sys.exit(1)



    def get_zip_content_list(self):
        """
        Creates a zip_content_list attribute with the list of files in a zip archive
        :return:
        """
        if self.ptype == "ZIP":
            with zipfile.ZipFile(self.path, 'r') as zip:
                self.zip_content_list = zip.namelist()
                self.logger.info("Looking into ZIP file content")
                for element in self.zip_content_list:
                    self.logger.debug(element)

        else:
            self.logger.warning("Not yet implemented")

    def get_zipped_band_filename(self, band):
        fband_name = [b for b in self.zip_content_list if band in b]
        if len(fband_name) == 1:
            self.logger.info("Found file %s for band name %s" % (fband_name[0], band))
            return fband_name[0]
        else:
            self.logger.error("No match found for band name %s" % band)
            sys.exit(2)

    def get_zipped_band_subset_asarray(self, fband, logger, ulx, uly, lrx, lry):
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
            translate = 'gdal_translate -projwin %s %s %s %s /vsizip/%s/%s %s' % (ulx, uly, lrx, lry, self.path, fband, ".tmp.tif")
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

        return img.ReadAsArray()

    def get_zipped_band(self, fband):
        """
        Return a gdal object from an image in a zip archive
        :param fband:
        :return: gdal object
        """
        self.logger.debug('Gdal.Open using /vsizip/%s/%s' % (self.path, fband))
        return gdal.Open('/vsizip/%s/%s' % (self.path, fband))

    def get_zipped_band_asarray(self, fband):
        img = self.get_zipped_band(fband)
        return img.ReadAsArray()

    def make_quicklook(self, r, g, b, logger, outfile="quicklook.png"):
        """
        Generate a quicklook as PNG
        :param r: band name (should match string name in filename)
        :param g: band name (should match string name in filename)
        :param b: band name (should match string name in filename)
        :param logger:
        :param outfile:
        :return: void
        """
        logger.info("Generating quicklook...")
        red_band = self._convert_band_uint8(r)
        green_band = self._convert_band_uint8(g)
        blue_band = self._convert_band_uint8(b)

        array_stack = np.dstack((red_band, green_band, blue_band))
        img = pillow.fromarray(array_stack)
        if outfile[-4:] != ".png":
            outfile += ".png"

        img.save(outfile)

    def _convert_band_uint8(self, band):
        """Convert a band array to unint8
        :return: an unint8 numpy array
        """
        b_max = np.nanmax(band)
        if b_max > 0:
            img = band / b_max * 256
        else:
            img = band * 0

        return img.astype(np.uint8)

class Venus_product(Product):
    def get_bands(self):
        return ["SRE_B2", "SRE_B4", "SRE_B7"]

    def get_mask(self, mtype):
        pass

    def parse_metadata(self):
        fname = self.get_metadata_fname()
        self.xml_meta = minidom.parse(fname)

    def get_metadata_fname(self):
        fmeta = [f for f in self.zip_content_list if "MTD_ALL.xml" in f]
        if len(fmeta) == 1:
            self.logger.info("Found metadata file %s" % (fmeta[0]))
            return fmeta[0]
        else:
            self.logger.error("No match found for metadata file")
            sys.exit(2)






