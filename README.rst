A script to fetch iaps from itunesconnect, fetch json from customed configured api, merge them, and push merged itmsp to itunesconnect  

Usage:  

```
pip3 install iapsync  

iapsync -c <your config file> -m <sync|verify|upload>  
```

Note: api data is extracted using a dict of lambda expressions, well, for my convenience ;], refer to the following sample config file  

A sample config file:  

[sample file link: https://raw.githubusercontent.com/bestofsong/iap-sync/master/assets/config.sample.py](https://raw.githubusercontent.com/bestofsong/iap-sync/master/assets/config.sample.py)


```python
# itc_conf, api_meta are required
# defaults is optional

from datetime import datetime

itc_conf = {
    'SKU': 'sku of your app',
    'username': 'itunesconnect account',
    'password': 'itunesconnect password',
    # optional:  在itc上删除过的商品，他们的id就不能重复使用了。同时transporter查询不到这些删除过的id；所以只能手工排除这些id。
    'excludes': {
        'live.2157',
        'live.2279',
        'live.2095',
        'live.2165',
        'live.1860',
        'live.2250',
        'live.2138',
        'live.2281',
        'live.2237',
    },
    # optional
    'NAME_MAX': 25,
    'DESC_MAX': 45,
    'NAME_MIN': 2,
    'DESC_MIN': 10,
    'REVIEW_MAX': 200,
    'REVIEW_MIN': 20,
}

# optional
defaults = {
   # optional
   'SCREENSHOT_PATH': '',
}

api_meta = [
    {
        # return json
        'api': 'url_that_responds with_json',

        # used to locate product list, i.e. json().get('data').get('productList ')
        'key_path': 'data.productList',

        # appstore => back end
        'locales': ['en-US', 'zh-Hans'],
        'key_map': {
            'product_id': lambda product: '%s%s' % ('live.', str(product['productId'])),
            'price': lambda product: float(product['cntPrice']),
            'en-US': {
                'title': lambda product: product['productName'],
                'description': lambda product: product['productName'],
            },
            'zh-Hans': {
                'title': lambda product: product['productName'],
                'description': lambda product: product['productName'],
            },
            'type': lambda product: 'non-consumable',
            'reference_name': lambda product: '%s-%s-%s' % (str(product['productId']), product['productName'], str(datetime.now())),
            # optional，默认True
            'cleared_for_sale': lambda product: True,
            # optional: 可选
            'review_notes': None,
            'review_screenshot': None,
        },
        'review_notes': '该商品包含一套课程讲义，对应每个章节有录制的高质量教学视频，用户可以通过app与教师进行互动（如打分，批改，答疑）。可以免费观看部分内容，购买之后可以观看完整课程。',
    },

    {
        # return json
        'api': 'another json endpoint',

        # locate product list
        'key_path': 'data.productList',

        # appstore => back end
        'locales': ['en-US', 'zh-Hans'],
        'key_map': {
            'product_id': lambda product: '%s%s' % ('dev.live.', str(product['productId'])),
            'price': lambda product: float(product['cntPrice']),
            'en-US': {
                'title': lambda product: product['productName'],
                'description': lambda product: product['productName'],
            },
            'zh-Hans': {
                'title': lambda product: product['productName'],
                'description': lambda product: product['productName'],
            },
            'reference_name': lambda product: '测试商品：%s-%s-%s' % (str(product['productId']), product['productName'], str(datetime.now())),
            'type': lambda product: 'non-consumable',
            # 可选，默认True
            'cleared_for_sale': lambda product: True,
            # 可选
            'review_notes': None,
            'review_screenshot': None,
        },
        'review_notes': '该商品包含一套课程讲义，对应每个章节有录制的高质量教学视频，用户可以通过app与教师进行互动（如打分，批改，答疑）。可以免费观看部分内容，购买之后可以观看完整课程。',
    }
]

```

