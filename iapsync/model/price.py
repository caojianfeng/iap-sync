from ..defs import defs

def extract_price(data):
    ret = []
    for it in data:
        if not it or len(it['products']) <= 0:
            continue

        by_env = {}
        ret.append(by_env)
        meta = it['meta']
        by_env['callback'] = meta.get('callback', None)
        by_env['callback_params'] = meta.get('callback_params', None)
        by_env['products'] = list(map(
            lambda p: {
                'product_id': p[defs.KEY_PRODUCT_ID],
                'product_price': int(100 * p[defs.KEY_APPSTORE_PRICE])
            },
            it['products']
        ))
    return ret
