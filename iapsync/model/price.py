from ..defs import defs

def extract_price(data):
    ret = []
    for it in data:
        if not it or len(it['products']) <= 0:
            continue
        by_env = {}
        ret.append(by_env)
        by_env['callback'] = it['meta']['callback']
        by_env['callback_params'] = it['meta']['callback_params']
        by_env['products'] = list(map(
            lambda p: {
                'product_id': p[defs.KEY_PRODUCT_RAW_ID],
                'product_price': int(100 * p[defs.KEY_APPSTORE_PRICE])
            },
            it['products']
        ))
    return ret
