import csv
import re
import os

_this_dir_ = os.path.dirname(os.path.realpath(__file__))

def get_price_tier_table(path):
    if not path:
        path = '%s/pricing-matrix.csv' % _this_dir_
    rows = None
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)
    if not rows:
        raise TypeError('failed to get price info')

    head = rows[0]
    china_jj = -1
    for jj, col_name in enumerate(head):
        if jj == 0:
            continue
        if col_name.find('China') != -1 and col_name.find('CNY') != -1:
            if china_jj != -1:
                raise  TypeError('multi columns matched: China and CNY, not sure which to go!')
            china_jj = jj

    if china_jj == -1:
        raise  TypeError('no column matched: China and CNY!')

    price_rmb = list(map(lambda row: float(row[china_jj]), rows[2:]))

    def extract_num(s):
        m = re.search('^\s*等级\s*(\d+)\s*$', s)
        if not m:
            return None
        if m.lastindex != 1:
            raise TypeError('price tier 提取失败，格式错误')
        return int(m.group(1))

    price_tier_raw = []
    for ii, r in enumerate(rows[2:]):
        if not r or len(r) < 1:
            raise TypeError('价格表格式有问题，有空行')
        tier_raw = r[0]
        tier_value = extract_num(tier_raw)
        if tier_value is None:
            if ii == 0:
                tier_value = 0
            else:
                break
        price_tier_raw.append(tier_value)

    if not len(price_tier_raw):
        raise TypeError('price tier vector empty, should not happen')
    ret = []
    for ii, t in enumerate(price_tier_raw):
        if len(price_rmb) <= ii:
            raise TypeError('inconsistency')
        ret.append((t, price_rmb[ii]))
    return ret


def calc_price_tier_floor(price, accept_zero_price):
    if price < 0:
        raise TypeError('price: %s is negative, not allowed' % str(price))
    tier_table = get_price_tier_table(None)
    last_t = None
    for ii, tup in enumerate(tier_table):
        t, p = tup
        if p > price:
            # last_t is surely not None, because price is non-negative, tier_table starts from 0
            return last_t if last_t[0] > 0 or accept_zero_price else (-1, -1)
        last_t = tup
    return -1, -1


def calc_price_tier_ceil(price, accept_zero_price):
    tier_table = get_price_tier_table(None)
    for ii, tup in enumerate(tier_table):
        t, p = tup
        if p >= price and (t > 0 or accept_zero_price):
            return tup
    return -1, -1


def calc_price_tier(price, ceil_price, accept_zero_price):
    if ceil_price:
        return calc_price_tier_ceil(price, accept_zero_price)
    else:
        return calc_price_tier_floor(price, accept_zero_price)

if __name__ == '__main__':
    print(calc_price_tier(13))
