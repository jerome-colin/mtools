"""
Pytest for Product

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import Product
import utilities

logger = utilities.get_logger('test_Product', verbose=True)

generic_product = Product.Product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

def test_product_name():
    logger.info("test_product_name")
    assert generic_product.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

def test_product_type():
    logger.info("test_product_type")
    assert generic_product.ptype == "ZIP"

venus_product = Product.Venus_product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger)

def test_venus_product_name():
    logger.info("test_venus_product_name")
    assert venus_product.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

dir_product = Product.Product("test_data/acix_captentras/SENTINEL2A_20171007-103241-161_L2A_T31TFJ_C_V1-0", logger)

def test_dir_product_type():
    logger.info("test_dir_product_type")
    assert dir_product.ptype == "DIR"

def test_dir_content_list():
    logger.info("test_dir_content_list")
    logger.debug(dir_product.content_list)