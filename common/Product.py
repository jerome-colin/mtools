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
import osgeo.gdal as gdal
import glob
import numpy as np
try:
    import utilities
except ModuleNotFoundError:
    this_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(this_dir)
    import utilities


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
        self.sre_scalef = 1.

        # Consistency check
        # TODO: move this test to Collection and use subclasses
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

    def find_band(self, band):
        fband_name = [b for b in self.content_list if band in b]
        if len(fband_name) == 1:
            self.logger.info("Found file %s for band name %s" % (fband_name[0], band))
            return fband_name[0]
        else:
            self.logger.error("No match found for band name %s" % band)
            sys.exit(2)

    def get_band(self, band, scalef=None, layer=None, tiny=False):
        """
        Return a gdal object from an image in a zip archive
        :param fband:
        :return: gdal object
        """
        self.logger.debug('Gdal.Open using %s' % (band))
        if self.ptype == "DIR":
            if scalef is not None:
                band_arr = gdal.Open('%s' % (band)).ReadAsArray() / scalef
            else:
                band_arr = gdal.Open('%s' % (band)).ReadAsArray()
        if self.ptype == "ZIP":
            if scalef is not None:
                band_arr = gdal.Open('/vsizip/%s/%s' % (self.path, band)).ReadAsArray() / scalef
            else:
                band_arr = gdal.Open('/vsizip/%s/%s' % (self.path, band)).ReadAsArray()

        if tiny:
            band_arr = (band_arr*10000).astype(np.uint16)

        if layer is not None:
            return band_arr[layer,:,:]
        else:
            return band_arr

    def get_band_subset(self, band, roi=None, ulx=None, uly=None, lrx=None, lry=None, scalef=None, layer=None):
        """Extract a subset from an image file
        :param band: product image filename from content_list
        :param ulx: upper left x
        :param uly: upper left y
        :param lrx: lower right x
        :param lry: lower right y
        :return: a Gdal object
        """
        if roi is not None:
            ulx = roi.ulx
            uly = roi.uly
            lrx = roi.lrx
            lry = roi.lry
        else:
            ulx = ulx
            uly = uly
            lrx = lrx
            lry = lry

        try:
            if self.ptype == "ZIP":
                translate = 'gdal_translate -projwin %s %s %s %s /vsizip/%s/%s %s' % (
                    ulx, uly, lrx, lry, self.path, band, ".tmp.tif")
            else:
                translate = 'gdal_translate -projwin %s %s %s %s %s %s' % (
                    ulx, uly, lrx, lry, band, ".tmp.tif")

            self.logger.debug(translate)
            args = shlex.split(translate)
            prog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = prog.communicate()
            self.logger.debug('Gdal_translate stdout: %s' % out)
            self.logger.debug('Gdal_translate stderr: %s' % err)
            img = gdal.Open(".tmp.tif")
            os.remove(".tmp.tif")

        except RuntimeError as err:
            self.logger.error('ERROR: Unable to open ' + band)
            self.logger.error(err)
            sys.exit(1)

        if scalef is not None:
            band_arr = img.ReadAsArray() / scalef
        else:
            band_arr = img.ReadAsArray()

        if layer is not None:
            return band_arr[layer,:,:]
        else:
            return band_arr

    def get_content_list(self):
        self.content_list = glob.glob(self.path + '/*')

    def get_mask(self, clm, edg, stats=False, use_nodata=False):
        """
        Return a 'validity mask' such that valid pixel is 1, non-valid pixel is 0
        :param clm: cloud mask numpy array
        :param edg: edge mask numpy array
        :param stats: return a fraction of valid pixels in percent
        :param use_nodata: if True, NaN in masks are used instead of 0
        :return: an array with 'valid' = 1, 'non-valid' = 0
        """

        # TODO: consider revising (numpy.ma ?)
        clm = clm
        edg = edg

        dummy = np.zeros_like(clm) + 1
        self.logger.debug("Dummy size=%i, sum=%i" % (np.size(dummy), np.sum(dummy)))

        if use_nodata:
            dummy[~np.isnan(clm)] = 0
            dummy[~np.isnan(edg)] = 0
        else:
            dummy[np.nonzero(clm)] = 0
            dummy[np.nonzero(edg)] = 0

        validity_ratio = np.nansum(dummy) / np.size(clm) * 100

        self.logger.debug("Product.get_mask: NaN in clm=%i, NaN in edg=%i, Non-zero in mask=%i, result=%i, ratio=%4.2f%%" %
                          (utilities.count_nan(clm), utilities.count_nan(edg), np.count_nonzero(dummy), np.nansum(dummy),
                           validity_ratio))

        if stats:
            return dummy, validity_ratio
        else:
            return dummy


class Product_dir_maja(Product):
    """
    Sub-class of Product for Maja specific methods
    TODO: Add R1 & R2 to band_names
    TODO: Preload CLM_R1, CLM_R2, EDG_R1 and EDG_R2 to create a boolean MASK_R1 and MASK_R2 to use in get_band to return a numpy.ma
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


class Product_hdf(Product):
    """
    Sub-class of Product for HDF specific methods
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

    def get_band(self, fband, scalef=None, tiny=False):
        """
        Overriding mother class method
        :param fband:
        :return:
        """
        if scalef is not None:
            if tiny:
                return (gdal.Open(self.content_list[fband][0], gdal.GA_ReadOnly).ReadAsArray() / scalef * 10000).astype(np.uint16)
            else:
                return gdal.Open(self.content_list[fband][0], gdal.GA_ReadOnly).ReadAsArray() / scalef
        else:
            return gdal.Open(self.content_list[fband][0], gdal.GA_ReadOnly).ReadAsArray().astype(np.int16)

    def get_band_subset(self):
        self.logger.warning("Product_hdf.get_band_subset not yet implemented !")

    def get_content_list(self):
        hdf_ds = gdal.Open(self.path, gdal.GA_ReadOnly)
        self.content_list = hdf_ds.GetSubDatasets()


class Product_hdf_acix(Product_hdf):
    """
    Subclass of Product_hdf for ACIX reference products
    """

    def __init__(self, path, logger):
        super().__init__(path, logger)
        self.sre_scalef = 10000


class Product_zip(Product):
    """
    Product subclass for zip
    """

    def __init__(self, path, logger):
        super().__init__(path, logger)

    def get_content_list(self):
        """

        :return: a list of files within a zip
        """
        self.name = self.path.split('/')[-1]
        with zipfile.ZipFile(self.path, 'r') as zip:
            self.content_list = zip.namelist()
            self.logger.info("Looking into ZIP file content")
            for element in self.content_list:
                self.logger.debug(element)


class Product_zip_venus(Product_zip):
    """
    Sub-class of Product_zip for Venus specific methods
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
        self.aot_scalef = 200
        self.vap_scalef = 20
        self.aot_name = "ATB_XS"
        self.vap_name = "ATB_XS"
        self.aot_layer = 1
        self.vap_layer = 0
        self.clm_name = "CLM_XS"
        self.edg_name = "EDG_XS"
