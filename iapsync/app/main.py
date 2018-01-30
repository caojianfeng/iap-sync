#! /usr/bin/env python3

import argparse
import os
import sys
import shutil
import subprocess
from lxml import etree
import hashlib
import urllib
import importlib.util

from pathlib import Path, PurePath
from ..defs import defs
from ..config import config
from ..remote.fetch import get_products
from ..convert.convert import convert_product, fix_appstore_product
from ..model.product import AppStoreProduct, XML_NAMESPACE, Product
from ..validate import validate


def get_transporter():
    xcode_root_b = subprocess.check_output(['xcode-select', '-p'])
    xcode_root = PurePath(str(xcode_root_b, 'utf-8').rstrip()).parent
    transporter_ancestor_path = xcode_root.joinpath('Applications/Application Loader.app/Contents')
    transporter_b = subprocess.check_output(['find', transporter_ancestor_path.as_posix(), '-name', 'iTMSTransporter'])
    return str(transporter_b, 'utf-8').rstrip()

transporter_path = get_transporter()


def path_import(absolute_path):
    '''implementation taken from https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly'''
    spec = importlib.util.spec_from_file_location(absolute_path, absolute_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def is_product_changed(product_elem, product_dict, price_only=False):
    pm = AppStoreProduct(product_elem)
    # cleared_for_sale, type is always checked
    cleared_for_sale_now = pm.cleared_for_sale()
    cleared_for_sale_next = product_dict[defs.KEY_CLEARED_FOR_SALE]
    if cleared_for_sale_next and not cleared_for_sale_now:
        return True
    if cleared_for_sale_now and not cleared_for_sale_next:
        return True

    type_now = pm.type()
    type_next = product_dict[defs.KEY_TYPE]
    if type_now != type_next:
        return True

    price_tier_now = pm.price_tier()
    price_tier_next = int(product_dict[defs.KEY_WHOLESALE_PRICE_TIER])
    if price_tier_now != price_tier_next:
        return True

    # only care about price tier
    if price_only:
        return False

    review_notes_now = pm.review_notes()
    review_notes_next = product_dict[defs.KEY_REVIEW_NOTES]
    if review_notes_next != review_notes_now:
        return True

    locales = product_dict['locales']
    for lc in locales:
        title_now = pm.title(lc)
        title_next = product_dict[lc][defs.KEY_TITLE]
        if title_next != title_now:
            return True

        desc_now = pm.description(lc)
        desc_next = product_dict[lc][defs.KEY_DESCRIPTION]
        if desc_next != desc_now:
            return True

    return False


def fix_appstore_screenshots(in_app_purchases, opts):
    nspc = opts['nspc']
    screenshot_dir = opts['screenshot_dir']
    existing_iaps = in_app_purchases.xpath(
        'x:in_app_purchase',
        namespaces=nspc
    )

    if not existing_iaps or len(existing_iaps) <= 0:
        return

    # bundled default screenshot
    DEFAULT_SCREENSHOT_PATH = config.DEFAULT_SCREENSHOT_PATH
    screenshot_file = Path(DEFAULT_SCREENSHOT_PATH)
    md5 = hashlib.md5(open(screenshot_file.as_posix(), 'rb').read()).hexdigest()
    size = screenshot_file.stat().st_size

    for p in existing_iaps:
        pid = p.xpath(
            'x:product_id',
            namespaces=nspc
        )[0].text

        size_node = p.xpath(
            'x:review_screenshot/x:size',
            namespaces=nspc
        )[0]
        md5_node = p.xpath(
            'x:review_screenshot/x:checksum[@type="md5"]',
            namespaces=nspc
        )[0]
        name_node = p.xpath(
            'x:review_screenshot/x:file_name',
            namespaces=nspc
        )[0]
        screenshot_name = '%s.%s' % (pid, 'png')
        name_node.text = screenshot_name
        md5_node.text = str(md5)
        size_node.text = str(size)
        screenshot_path = screenshot_dir.joinpath(screenshot_name).as_posix()
        shutil.copy(DEFAULT_SCREENSHOT_PATH, screenshot_path)


def fix_appstore_products(in_app_purchases, options):
    nspc = options['nspc']
    params = options['params']
    limits = params['limits']
    existing_iaps = in_app_purchases.xpath(
        'x:in_app_purchase',
        namespaces=nspc
    )

    if not existing_iaps or len(existing_iaps) <= 0:
        return

    for p in existing_iaps:
        pp = AppStoreProduct(p)
        fix_appstore_product(pp, limits)


def update_product(elem, p, options):
    price_only = options.get('price_only', False)

    pm = AppStoreProduct(elem)
    if not is_product_changed(elem, p, price_only):
        return

    print('update: id: %s, name: %s' % (p[defs.KEY_PRODUCT_ID], p[p['locales'][0]][defs.KEY_TITLE]))

    locales = p['locales']
    # print('update: now: %s, next: %s' % (pm, Product(Product.create_node(p))))
    pm.set_price_tier(p[defs.KEY_WHOLESALE_PRICE_TIER])
    pm.set_cleared_for_sale(p[defs.KEY_CLEARED_FOR_SALE])
    pm.set_reference_name(p[defs.KEY_REFERENCE_NAME])
    pm.set_review_notes(p[defs.KEY_REVIEW_NOTES])
    for lc in locales:
        pm.set_title(p[lc][defs.KEY_TITLE], lc)
        pm.set_description(p[lc][defs.KEY_DESCRIPTION], lc)


def find_product(in_app_purchases, product_dict, nspc):
    res_set = in_app_purchases.xpath(
        'x:in_app_purchase[x:product_id[text()=$pid]]',
        namespaces=nspc,
        pid=product_dict[defs.KEY_PRODUCT_ID]
    )
    return res_set[0] if len(res_set) > 0 else None


def append_product(in_app_purchases, product_dict):
    node = AppStoreProduct.create_node(product_dict)
    in_app_purchases.append(node)


def extract_params(parser):
    config_path = Path(parser.config_file)
    if config_path.is_absolute():
        config_full_path = config_path
    else:
        config_full_path = Path(os.getcwd()).joinpath(parser.config_file)

    config_md = path_import(config_full_path.as_posix())
    api_meta = config_md.api_meta
    itc_conf = config_md.itc_conf
    defaults = config_md.defaults if hasattr(config_md, 'defaults') else None
    excludes = itc_conf.get('excludes', {})
    fix_screenshots = True if parser.fix_screenshots else False
    force_update = True if parser.force_update else False

    limits = {
        'NAME_MAX': 25,
        'DESC_MAX': 45,
        'NAME_MIN': 2,
        'DESC_MIN': 10,
        'REVIEW_MAX': 200,
        'REVIEW_MIN': 20,
    }
    for k in limits.keys():
        if itc_conf.get(k) is not None:
            limits[k] = itc_conf.get(k)
        else:
            limits[k] = config.ITC_CONF.get(k)

    APP_SKU = itc_conf['SKU']
    APPSTORE_PACKAGE_NAME = '%s.itmsp' % APP_SKU

    return {
        'api_meta': api_meta,
        'itc_conf': itc_conf,
        'defaults': defaults,
        'excludes': excludes,
        'limits': limits,
        'APP_SKU': APP_SKU,
        'APPSTORE_PACKAGE_NAME': APPSTORE_PACKAGE_NAME,
        'username': itc_conf['username'],
        'password': itc_conf['password'],
        'skip_appstore': True if parser.skip_appstore else False,
        'price_only': True if not fix_screenshots and not force_update and parser.price_only else False,
        'fix_screenshots': fix_screenshots,
        'force_update': force_update,
    }


def sync(params, opts):
    namespaces = opts['namespaces']

    api_meta = params['api_meta']
    defaults = params['defaults']
    excludes = params['excludes']
    limits = params['limits']
    APP_SKU = params['APP_SKU']
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    username = params['username']
    password = params['password']

    DEFAULT_SCREENSHOT_PATH = config.DEFAULT_SCREENSHOT_PATH
    if defaults and defaults.get('DEFAULT_SCREENSHOT_PATH'):
        DEFAULT_SCREENSHOT_PATH = defaults.get('DEFAULT_SCREENSHOT_PATH')

    app_store_dir = Path(config.APPSTORE_META_DIR)
    skip_appstore = params.get('skip_appstore', False)
    if not skip_appstore:
        # clear APPSTORE_META dir
        if app_store_dir.exists():
            shutil.rmtree(app_store_dir.as_posix())
        app_store_dir.mkdir()

        # 下载App Store元数据
        try:
            subprocess.run([
                transporter_path, '-m', 'lookupMetadata', '-u', username, '-p', password,
                '-destination', app_store_dir.as_posix(), '-vendor_id', APP_SKU, '-subitemtype', 'InAppPurchase'])
        except:
            print('获取App Store数据失败：%s.' % sys.exc_info()[0])
            raise
        print('下载App Store元数据完成.')


    # clear tmp dir
    tmp_dir = Path(config.TMP_DIR)
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir.as_posix())
    tmp_dir.mkdir()

    # 初始化etree
    metadata_path = app_store_dir.joinpath(APPSTORE_PACKAGE_NAME).joinpath(config.APPSTORE_METAFILE)
    try:
        f = open(metadata_path.as_posix(), mode='rb')
        doc_tree = etree.parse(f)
    except OSError:
        print('io 错误：%s' % sys.exc_info()[0])
        raise
    except:
        print('拷贝元数据失败：%s.' % sys.exc_info()[0])
        raise

    # 访问etree/.../in_app_purchases
    software_metadata_q = doc_tree.xpath('/x:package/x:software/x:software_metadata', namespaces = namespaces)
    if len(software_metadata_q) != 1:
        err = 'xpath fail: package/software/software_metadata should point to a single tag, but found: %d' % len(software_metadata_q)
        raise TypeError(err)
    software_metadata = software_metadata_q[0]
    in_app_purchases_q = software_metadata.xpath('x:in_app_purchases', namespaces = namespaces)
    if len(in_app_purchases_q) <= 0:
        in_app_purchases = etree.SubElement(software_metadata, '{%s}in_app_purchases' % XML_NAMESPACE)
    else:
        in_app_purchases = in_app_purchases_q[0]

    # 下载后台商品数据
    new_package_path = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)
    raw_products = get_products(api_meta)

    if raw_products is None:
        print('some how failed to get products')
        sys.exit(-1)

    if len(raw_products) <= 0:
        print('nothing to do, no products fetched')
        sys.exit(0)

    # 转换，计算价格阶梯，必须先于filter，后者排出阶梯=-1的商品
    options = {
        'default_screenshot': DEFAULT_SCREENSHOT_PATH,
        'screenshot_dir': new_package_path.as_posix(),
    }
    options.update(limits)
    converted_products = list(map(
        lambda pr: convert_product(Product(pr), options).unwrapped(),
        raw_products))

    # 过滤
    new_products = list(filter(lambda pp: pp[defs.KEY_PRODUCT_ID] not in excludes and validate.validate(pp), converted_products))
    if len(new_products) <= 0:
        print('nothing to do, all filtered out')
        sys.exit(0)

    # copy screenshots，顺序相关，必须在update_product之前运行，不然无法计算size, md5
    new_package_path.mkdir()
    for pp in new_products:
        screenshot_path = new_package_path.joinpath('%s.%s' % (pp[defs.KEY_PRODUCT_ID], 'png')).as_posix()
        screenshot_url = pp[defs.KEY_REVIEW_SCREENSHOT]
        if screenshot_url:
            try:
                urllib.request.urlretrieve(screenshot_url, screenshot_path)
            except:
                shutil.copy(DEFAULT_SCREENSHOT_PATH, screenshot_path)
        else:
            pp[defs.KEY_REVIEW_SCREENSHOT] = screenshot_path
            shutil.copy(DEFAULT_SCREENSHOT_PATH, screenshot_path)

    # merge in_app_purchases
    for p in new_products:
        e = find_product(in_app_purchases, p, namespaces)
        if e is None:
            if p[defs.KEY_PRODUCT_ID] not in excludes:
                print('new: id: %s, name: %s' % (p[defs.KEY_PRODUCT_ID], p[p['locales'][0]][defs.KEY_TITLE]))
                append_product(in_app_purchases, p)
        else:
            update_product(e, p, params)

    # appstore screenshot may used to be edited manually, which cannot pass verify
    # : screenshot name and stats not persistent, fix by writing them
    if params.get('fix_screenshots'):
        fix_appstore_screenshots(in_app_purchases, {'nspc': namespaces, 'screenshot_dir': new_package_path})

    if params.get('force_update'):
        fix_appstore_products(in_app_purchases, {'nspc': namespaces, 'params': params})

    # save things
    new_metafile_path = new_package_path.joinpath(config.APPSTORE_METAFILE)
    doc_tree.write(new_metafile_path.as_posix(), pretty_print=True, xml_declaration = True, encoding='utf-8')


def verify(params, opts):
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    username = params['username']
    password = params['password']
    tmp_dir = Path(config.TMP_DIR)
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)
    # 初始化etree
    try:
        subprocess.run([
            transporter_path,
            '-m', 'verify', '-u', username, '-p', password, '-f', p.as_posix()])
    except:
        print('验证失败：%s.' % sys.exc_info()[0])
        raise


def upload(params, opts):
    username = params['username']
    password = params['password']
    APPSTORE_PACKAGE_NAME = params['APPSTORE_PACKAGE_NAME']
    tmp_dir = Path(config.TMP_DIR)
    p = tmp_dir.joinpath(APPSTORE_PACKAGE_NAME)
    # 初始化etree
    try:
        subprocess.run([
            transporter_path,
            '-m', 'upload', '-u', username, '-p', password, '-f', p.as_posix()])
    except:
        print('上传失败：%s.' % sys.exc_info()[0])
        raise


dispatch_tbl = {
    'sync': sync,
    'verify': verify,
    'upload': upload,
}


def main():
    parser = argparse.ArgumentParser(
        description='''
        -m | --mode sync: fetch from api defined by --config-file, generate itmsp package, for uploading to itunesconnect
        -m | --mode verify: verify generated itmsp package by sync mode
        -m | --mode upload: upload generated itmsp package to itunes connect by sync mode
        '''
    )
    parser.add_argument('-c', '--config-file')
    parser.add_argument('-m', '--mode')
    parser.add_argument('--skip-appstore', default=False, type=bool)
    parser.add_argument('--price-only', default=False, type=bool)
    parser.add_argument('--fix-screenshots', default=False, type=bool)
    parser.add_argument('--force-update', default=False, type=bool)
    parser = parser.parse_args()
    params = extract_params(parser)
    dispatch_tbl[parser.mode](params, {'namespaces': {'x': XML_NAMESPACE}})

