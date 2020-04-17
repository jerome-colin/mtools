"""
Pytest for Product

"""

__author__ = "Jerome Colin"
__license__ = "MIT"
__version__ = "0.1.0"

import Product
import utilities

logger = utilities.get_logger('test_Product', verbose=True)

p = Product.Product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger, ptype="ZIP")

def test_product_name():
    assert p.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"

v = Product.Venus_product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger, ptype="ZIP")

def test_venus_product_name():
    assert v.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"