import os

#DEFAULT_TYPE = 'non-renewing subscription'

ITC_CONF = {
    'NAME_MAX': 25,
    'DESC_MAX': 45,
    'NAME_MIN': 2,
    'DESC_MIN': 10,
    'REVIEW_MAX': 200,
    'REVIEW_MIN': 20,
}

_this_dir_ = os.path.dirname(os.path.realpath(__file__))

APPSTORE_META_DIR = 'APPSTORE_META'
APPSTORE_METAFILE = 'metadata.xml'

DEFAULT_SCREENSHOT_PATH = '%s/product-screenshot.png' % _this_dir_
TMP_DIR = 'TMP'
TMP_PRODUCTS_PERSIST_FILE = '%s/products.json' % TMP_DIR

