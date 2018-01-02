import requests
from ..defs import defs

def access_list(obj, key_path):
    key_paths = key_path.split('.')
    ret = obj
    for k in key_paths:
        ret = ret[k]
    return ret


def get_products(api_meta):
    metas = api_meta if isinstance(api_meta, list) else [api_meta]
    ret = []
    for mt in metas:
        k_m = mt['key_map']
        api = mt['api']
        json = requests.get(api).json()
        if not isinstance(json, list) and not isinstance(json, dict):
            continue
        product_list = access_list(json, mt['key_path'])
        for p in product_list:
            new_item = {
                'raw_product': p,
                defs.KEY_PRODUCT_ID: k_m[defs.KEY_PRODUCT_ID](p),
                defs.KEY_REFERENCE_NAME: k_m[defs.KEY_REFERENCE_NAME](p),
                defs.KEY_TYPE: k_m[defs.KEY_TYPE](p),
                defs.KEY_REVIEW_SCREENSHOT: k_m[defs.KEY_REVIEW_SCREENSHOT](p) if k_m[defs.KEY_REVIEW_SCREENSHOT] else None,
                defs.KEY_REVIEW_NOTES:
                    k_m[defs.KEY_REVIEW_SCREENSHOT](p) if k_m[defs.KEY_REVIEW_SCREENSHOT] else mt['review_notes'],
                defs.CONST_PRICE: k_m[defs.CONST_PRICE](p),
                defs.KEY_CLEARED_FOR_SALE:
                    k_m[defs.KEY_CLEARED_FOR_SALE](p) if k_m[defs.KEY_CLEARED_FOR_SALE] else True,
            }
            locates = mt['locales']
            new_item['locales'] = locates
            for lc in locates:
                desc = {
                    defs.KEY_TITLE: k_m[lc][defs.KEY_TITLE](p),
                    defs.KEY_DESCRIPTION: k_m[lc][defs.KEY_DESCRIPTION](p),
                }
                new_item[lc] = desc
            ret.append(new_item)
    return ret

