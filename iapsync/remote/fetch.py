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
        by_env = {'meta': mt, 'products': []}
        ret.append(by_env)
        k_m = mt['key_map']
        api = mt['api']
        env = mt['env']
        json = requests.get(api).json()
        if not isinstance(json, list) and not isinstance(json, dict):
            continue
        product_list = access_list(json, mt['key_path'])
        for p in product_list:
            new_item = {
                defs.KEY_ENV: env,
                defs.KEY_PRODUCT_RAW_ID: k_m[defs.KEY_PRODUCT_RAW_ID](p),
                defs.KEY_REFERENCE_NAME: k_m[defs.KEY_REFERENCE_NAME](p),
                defs.KEY_TYPE: k_m[defs.KEY_TYPE](p),
                defs.KEY_REVIEW_SCREENSHOT:
                    k_m[defs.KEY_REVIEW_SCREENSHOT](p) if k_m[defs.KEY_REVIEW_SCREENSHOT] else None,
                defs.KEY_REVIEW_NOTES:
                    k_m[defs.KEY_REVIEW_SCREENSHOT](p) if k_m[defs.KEY_REVIEW_SCREENSHOT] else mt['review_notes'],
                defs.CONST_PRICE: k_m[defs.CONST_PRICE](p),
                defs.KEY_CLEARED_FOR_SALE:
                    k_m[defs.KEY_CLEARED_FOR_SALE](p) if k_m[defs.KEY_CLEARED_FOR_SALE] else True,
                defs.KEY_VALIDITY: k_m[defs.KEY_VALIDITY](p) if k_m.get(defs.KEY_VALIDITY, None) else None,
                defs.KEY_VALIDITY_TYPE:
                    k_m[defs.KEY_VALIDITY_TYPE](p) if k_m.get(defs.KEY_VALIDITY_TYPE, None) else None,
            }
            locates = mt['locales']
            new_item['locales'] = locates
            for lc in locates:
                desc = {
                    defs.KEY_TITLE: k_m[lc][defs.KEY_TITLE](p),
                    defs.KEY_DESCRIPTION: k_m[lc][defs.KEY_DESCRIPTION](p),
                }
                new_item[lc] = desc
            by_env['products'].append(new_item)

    return ret

