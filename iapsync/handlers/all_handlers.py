import requests

def handle(data):
    for it in data:
        payload = {'products': it['products']}
        callback = it['callback']
        params = it['callback_params']
        if len(payload['products']) <= 0:
            continue
        try:
            resp = requests.post(callback, params=params, json=payload)
            print('callback: %s\n' % callback)
            print('callback_params: %s\n' % params)
            print('resp: %s\n\n\n' % resp)
        except:
            print('callback failed: %s' % callback)
