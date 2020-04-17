import Product
import utilities

logger = utilities.get_logger('test', verbose=True)

p = Product.Product("test_data/VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip", logger, ptype="ZIP")

def test_product_name():
    assert p.name == "VENUS-XS_20200402-191352-000_L2A_GALLOP30_D.zip"