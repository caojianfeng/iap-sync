import requests
import json

def handle(data):
    for it in data:
        payload = {'products': json.dumps(it['products'])}
        callback = it.get('callback', None)
        params = it.get('callback_params', {})
        if len(payload['products']) <= 0 or not callback:
            continue
        try:
            resp = requests.post(callback, params=params, json=payload)
            print('callback: %s' % callback)
            print('callback_params: %s' % params)
            if resp and 200 <= resp.status_code < 400:
                print('resp data: %s\n\n\n' % resp.json())
            else:
                print('resp: %s\n\n\n' % resp)
        except:
            print('callback failed: %s' % callback)
