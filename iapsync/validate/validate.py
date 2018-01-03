from ..defs import defs

def validate(p):
    if p[defs.KEY_WHOLESALE_PRICE_TIER] == -1:
        print('ignore: id: %s, name: %s' % (p[defs.KEY_PRODUCT_ID], p[p['locales'][0]][defs.KEY_TITLE]))
        return False
    return True

