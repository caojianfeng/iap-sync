import requests
import json
import operator
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from ..config import config


def upload(data, params):
    for it in data:
        result = it.get('result', None)
        if not result:
            continue
        updated = result.get('updated', [])
        added = result.get('added', [])
        products = operator.concat(updated, added)
        if len(products) <= 0:
            continue

        payload = {'products': json.dumps(products)}
        callback = it.get('callback', None)
        params = it.get('callback_params', {})
        if not callback:
            continue
        try:
            resp = requests.post(callback, params=params, json=payload)
            result['response'] = resp
            print('callback: %s' % callback)
            print('callback_params: %s' % params)
            if resp and 200 <= resp.status_code < 400:
                print('resp data: %s\n\n\n' % resp.json())
            else:
                print('resp: %s\n\n\n' % resp)
        except:
            print('callback failed: %s' % callback)
            result['response'] = 'failed to upload to backend'


def notify(data, params):
    def send_email(receivers, subject, content):
        smtp_conf = params.get('smtp_conf', None)
        if not smtp_conf:
            return
        email_sender = params['email_sender']
        sender = email_sender if email_sender else config.EMAIL_SENDER
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = sender

        host = smtp_conf['host']
        port = smtp_conf['port']
        user = smtp_conf['user']
        password = smtp_conf['password']

        print('will send: %s, to: %s' % (content, receivers))

        s = smtplib.SMTP_SSL()
        try:
            s.connect(host, port)
        except:
            print('failed to connecto to smtp host: %s, port: %d', (host, port))
        try:
            s.login(user, password)
        except:
            print(
                'failed to login to smtp host: %s, port: %d, user: %s, password: %s',
                (host, port, user, password))
        try:
            s.sendmail(sender, receivers, msg.as_string())
        except:
            print('failed to send to smtp host: %s, port: %d, user: %s, password: %s, msg: %s',
                  (host, port, user, password, msg.as_string()))

        try:
            s.quit()
        except:
            print('did send to smtp host: %s, port: %d, user: %s, password: %s, msg: %s, but failed to quit',
                  (host, port, user, password, msg.as_string()))
        print('did send: %s, to: %s' % (content, receivers))

    message = ''
    subject = 'App Store商品更新'
    for it in data:
        result = it.get('result', {})
        updated = result.get('updated', [])
        added = result.get('added', [])
        if len(updated) <= 0 and len(added) <= 0:
            continue
        meta = it.get('meta', {})
        message = '%sapi: %s\n' % (message, meta['api'])
        message = '%senvironment: %s\n' % (message, meta['env'])
        message = '%supdated: %d, added: %d\n' % (message, len(updated), len(added))
        resp = result.get('response', None)
        if not resp:
            message = message
        elif 200 <= resp.status_code < 400:
            message = '%sresponse data: %s\n' % (message, resp.json())
        else:
            message = '%shttp response: %s\n' % (message, resp)

    emails = params.get('subscribers', [])
    if len(emails) and message != '':
        message = '%s\n\ntimestamp: %s\n\n\n' % (message, datetime.today().isoformat())
        send_email(emails, subject, message)


def handle(data, params):
    # mutating
    if not params.get('dry_run'):
        upload(data, params)
    notify(data, params)

