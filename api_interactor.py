import time
import hmac
import random
import requests
import webbrowser
from config import CONSUMER_KEY_SANDBOX as CONS_KEY, CONSUMER_SECRET_SANDBOX as CONS_SECRET
from urllib.parse import quote_plus, unquote_plus, urlencode
from base64 import b64encode
from hashlib import sha1


TIMEOUT = 5  # seconds


def generate_nonce(length=8):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def etrade_signature(cons_secret, token_secret, method, url, headers):
    key = bytes(quote_plus(cons_secret) + '&' +
                quote_plus(token_secret), 'utf-8')
    sorted_headers = [quote_plus(k) + '=' + quote_plus(headers[k])
                      for k in sorted(headers)]
    header_string = '&'.join(sorted_headers)
    base_string = quote_plus(method) + '&' + \
        quote_plus(url) + '&' + quote_plus(header_string)
    raw = bytes(base_string, 'utf-8')

    hashed = hmac.new(key, raw, sha1)

    return quote_plus(b64encode(hashed.digest()).decode('utf-8'))


def request_etrade_token(url):
    timestamp = str(round(time.time()))
    nonce = generate_nonce()
    access_token = ''
    access_secret = ''
    headers = {'oauth_consumer_key': CONS_KEY, 'oauth_nonce': nonce, 'oauth_signature_method': 'HMAC-SHA1',
               'oauth_timestamp': timestamp, 'oauth_callback': 'oob'}

    signature = etrade_signature(
        CONS_SECRET, access_secret, 'GET', url, headers)

    headers['oauth_signature'] = signature
    params = ','.join([k+'='+headers[k] for k in headers])
    authorization = {'Authorization': 'OAuth {}'.format(params)}
    r = requests.get(url, headers=authorization, timeout=TIMEOUT)

    d = {}
    if r.ok:
        info = r.text.split('&')
        for i in info:
            j, k = i.split('=')
            d[j] = k
    return unquote_plus(d['oauth_token']), unquote_plus(d['oauth_token_secret'])


def get_access_token(url, oauth_token, oauth_token_secret, oauth_verifier):
    timestamp = str(round(time.time()))
    nonce = generate_nonce()
    signature_method = 'HMAC-SHA1'

    headers = {'oauth_consumer_key': CONS_KEY, 'oauth_nonce': nonce, 'oauth_signature_method': signature_method,
               'oauth_timestamp': timestamp, 'oauth_token': oauth_token, 'oauth_verifier': oauth_verifier}

    signature = etrade_signature(
        CONS_SECRET, oauth_token_secret, 'GET', url, headers)

    headers['oauth_token'] = quote_plus(oauth_token)
    headers['oauth_signature'] = signature

    params = ','.join([k+'='+headers[k] for k in headers])
    authorization = {'Authorization': 'OAuth realm="",{}'.format(params)}
    # print(authorization)

    r = requests.get(url, headers=authorization, timeout=TIMEOUT)
    d = {}
    if r.ok:
        info = r.text.split("&")
        for i in info:
            j, k = i.split('=')
            d[j] = k

    return unquote_plus(d['oauth_token']), unquote_plus(d['oauth_token_secret'])


def create_authorization_header(base_url, access_token, access_secret, params={}):
    timestamp = str(round(time.time()))
    nonce = generate_nonce()
    signature_method = 'HMAC-SHA1'
    headers = {'oauth_consumer_key': CONS_KEY, 'oauth_nonce': nonce, 'oauth_signature_method': signature_method,
               'oauth_timestamp': timestamp, 'oauth_token': access_token}

    headers.update(params)

    signature = etrade_signature(
        CONS_SECRET, access_secret, 'GET', base_url, headers)
    headers['oauth_token'] = quote_plus(access_token)
    headers['oauth_signature'] = signature
    oauth_format = ','.join([k+'='+headers[k] for k in sorted(headers)])
    authorization = {'Authorization': 'OAuth realm="",{}'.format(oauth_format)}

    return authorization


def get_option_chain_data(symbol, access_token, access_secret, sandbox=True, json=True):
    sandbox_url = 'https://apisb.etrade.com/v1/market/optionchains'
    live_url = 'https://api.etrade.com/v1/market/optionchains'
    if sandbox:
        url = sandbox_url
    else:
        url = live_url
    if json:
        url += '.json'
    params = {'symbol': symbol}
    authorization = create_authorization_header(
        url, access_token, access_secret, params=params)
    param_formatter = [str(k) + '=' + params[k] for k in params]
    full_url = url + '?' + '&'.join(param_formatter)
    r = requests.get(full_url, headers=authorization, timeout=TIMEOUT)

    print(r.text)


if __name__ == "__main__":
    url = 'https://api.etrade.com/oauth/request_token'

    token, token_secret = request_etrade_token(url)

    auth_url = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}'.format(
        CONS_KEY, token)
    webbrowser.open_new(auth_url)

    verification_code = input(
        "Please accept agreement and enter text code after logging in\n")
    token_url = 'https://api.etrade.com/oauth/access_token'

    access_token, access_secret = get_access_token(
        token_url, token, token_secret, verification_code)
    symbol = 'AAPL'
    get_option_chain_data(symbol, access_token, access_secret)
