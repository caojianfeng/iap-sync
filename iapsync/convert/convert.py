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

def convert_product(product, options):
    converters = [convert_price, fix_description, fix_title, fix_review]
    ret = product
    for t in converters:
        ret = t(ret, options)
    return ret

