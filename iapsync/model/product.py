__author__ = 'wansongHome'
import hashlib
from lxml import etree
from copy import deepcopy
from datetime import date, timedelta

from pathlib import PurePath, Path
from ..defs import defs

XML_NAMESPACE = 'http://apple.com/itunes/importer'

YESTODAY = (date.today() + timedelta(days = -1)).strftime('%Y-%m-%d')

__template_str = '''
<in_app_purchase xmlns="%s">
    <product_id>111111111111111</product_id>
    <reference_name>11111111111111111</reference_name>
    <type>non-consumable</type>
    <products>
        <product>
            <cleared_for_sale>true</cleared_for_sale>
            <intervals>
                <interval>
                    <start_date>%s</start_date>
                    <wholesale_price_tier>1</wholesale_price_tier>
                </interval>
            </intervals>
        </product>
    </products>
    <locales>
        <locale name="en-US">
            <title>11111111111111</title>
            <description>11111111111111</description>
        </locale>
        <locale name="zh-Hans">
            <title>11111111111</title>
            <description>111111111111</description>
        </locale>
    </locales>
    <review_screenshot>
        <size>111111111111</size>
        <file_name>111111111111</file_name>
        <checksum type="md5">111111111111111</checksum>
    </review_screenshot>
    <review_notes>1111111111111111</review_notes>
</in_app_purchase>
''' % (XML_NAMESPACE, YESTODAY)

TEMPLATE_NODE = etree.fromstring(__template_str)


class Product:
    def create_node(p_dict):
        ret = deepcopy(TEMPLATE_NODE)
        pm = Product(ret)

        pm.set_product_id(p_dict[defs.KEY_PRODUCT_ID])
        pm.set_reference_name(p_dict[defs.KEY_REFERENCE_NAME])
        pm.set_price_tier(p_dict[defs.KEY_WHOLESALE_PRICE_TIER])
        locs = p_dict['locales']
        for loc in locs:
            pm.set_title(p_dict[loc][defs.KEY_TITLE], loc)
            pm.set_description(p_dict[loc][defs.KEY_DESCRIPTION], loc)

        screenshot_file = Path(p_dict[defs.KEY_REVIEW_SCREENSHOT])
        md5 = hashlib.md5(open(screenshot_file.as_posix(), 'rb').read()).hexdigest()
        pm.set_screenshot_md5(md5)
        pm.set_screenshot_size(screenshot_file.stat().st_size)
        pm.set_screenshot_name(PurePath(p_dict[defs.KEY_REVIEW_SCREENSHOT]).name)
        pm.set_review_notes(p_dict[defs.KEY_REVIEW_NOTES])
        pm.set_cleared_for_sale(p_dict[defs.KEY_CLEARED_FOR_SALE])
        return ret

    def __init__(self, p_elem, namespace = XML_NAMESPACE):
        self.elem = p_elem
        self.namespaces = {'x': namespace}

    def price_tier(self):
        text = self.elem.xpath(
            'x:products/x:product/x:intervals/x:interval/x:wholesale_price_tier',
            namespaces = self.namespaces
        )[0].text
        return int(text)

    def set_price_tier(self, value):
        node = self.elem.xpath(
            'x:products/x:product/x:intervals/x:interval/x:wholesale_price_tier',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def screenshot_md5(self):
        return self.elem.xpath(
            'x:review_screenshot/x:checksum',
            namespaces = self.namespaces
        )[0].text

    def set_screenshot_md5(self, value):
        node = self.elem.xpath(
            'x:review_screenshot/x:checksum',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def screenshot_size(self):
        text = self.elem.xpath(
            'x:review_screenshot/x:size',
            namespaces = self.namespaces
        )[0].text
        return int(text)

    def set_screenshot_size(self, value):
        node = self.elem.xpath(
            'x:review_screenshot/x:size',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def screenshot_name(self):
        return self.elem.xpath(
            'x:review_screenshot/x:file_name',
            namespaces = self.namespaces
        )[0].text

    def set_screenshot_name(self, value):
        node = self.elem.xpath(
            'x:review_screenshot/x:file_name',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def set_product_id(self, value):
        node = self.elem.xpath(
            'x:product_id',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def reference_name(self):
        node = self.elem.xpath(
            'x:reference_name',
            namespaces = self.namespaces
        )[0]
        return node.text

    def set_reference_name(self, value):
        node = self.elem.xpath(
            'x:reference_name',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def title(self, locale):
        node = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:title',
            namespaces = self.namespaces,
            loc = locale
        )
        return node[0].text if node and len(node) else ''

    def set_title(self, value, locale):
        node = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:title',
            namespaces = self.namespaces,
            loc = locale
        )[0]
        node.text = str(value)

    def description(self, locale):
        node = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:description',
            namespaces = self.namespaces,
            loc = locale
        )
        return node[0].text if node and len(node) else ''

    def set_description(self, value, locale):
        node = self.elem.xpath(
            'x:locales/x:locale[@name = $loc]/x:description',
            namespaces = self.namespaces,
            loc = locale
        )[0]
        node.text = str(value)

    def review_notes(self):
        node = self.elem.xpath(
            'x:review_notes',
            namespaces = self.namespaces
        )
        return node[0].text if node and len(node) else ''

    def set_review_notes(self, value):
        node = self.elem.xpath(
            'x:review_notes',
            namespaces = self.namespaces
        )[0]
        node.text = str(value)

    def cleared_for_sale(self):
        text = self.elem.xpath(
            'x:products/x:product/x:cleared_for_sale',
            namespaces = self.namespaces
        )[0].text
        return str(text) == 'true'

    def set_cleared_for_sale(self, value):
        node = self.elem.xpath(
            'x:products/x:product/x:cleared_for_sale',
            namespaces = self.namespaces
        )[0]
        node.text = 'true' if value else 'false'

    def __str__(self):
        return str(etree.tostring(self.elem, encoding = 'utf-8'), 'utf-8')

