from datetime import datetime
from ..defs import defs
from ..appstore.appstore_pricing import calc_price_tier


def convert_price(product, options):
    tier = calc_price_tier(product[defs.CONST_PRICE])
    product[defs.KEY_WHOLESALE_PRICE_TIER] = tier
    return product

def pad_or_trim(s, max, min):
    ll = len(s)
    if ll < min:
        return s + '*' * (min - ll)
    if ll > max:
        return s[:max]
    return s

def fix_title(product, options):
    locales = product['locales']
    for lc in locales:
        t = product[lc][defs.KEY_TITLE]
        product[lc][defs.KEY_TITLE] = pad_or_trim(t, options['NAME_MAX'], options['NAME_MIN'])
    return product


def fix_description(product, options):
    locales = product['locales']
    for lc in locales:
        t = product[lc][defs.KEY_DESCRIPTION]
        product[lc][defs.KEY_DESCRIPTION] = pad_or_trim(t, options['DESC_MAX'], options['DESC_MIN'])
    return product

def fix_review(product, options):
    r = product[defs.KEY_REVIEW_NOTES]
    product[defs.KEY_REVIEW_NOTES] = pad_or_trim(r, options['REVIEW_MAX'], options['REVIEW_MIN'])
    return product

def add_validity(product, options):
    raw_product = product.get('raw_product', None)
    if not raw_product:
        return product

    validity_type = raw_product.get('validityType', None)
    validity = raw_product.get('validity', None)
    if validity is None or validity_type is None:
        return product

    if int(validity_type) == 1:
        validity_desc = '有效期%d天。' % int(validity)
    elif int(validity_type == 2):
        validity_desc = '有效期至%s。' % datetime.fromtimestamp(int(validity)).strftime('%Y-%m-%d')
    else:
        return product

    locales = product['locales']
    for lc in locales:
        t = product[lc][defs.KEY_DESCRIPTION]
        with_validity = '%s%s' % (validity_desc, t)
        product[lc][defs.KEY_DESCRIPTION] = pad_or_trim(
            with_validity,
            options['DESC_MAX'],
            options['DESC_MIN'])
    return product

def convert_product(product, options):
    converters = [convert_price, fix_description, add_validity, fix_title, fix_review]
    ret = product
    for t in converters:
        ret = t(ret, options)
    return ret

