import time
import hmac
import requests
import webbrowser
from config import CONSUMER_KEY_SANDBOX, CONSUMER_SECRET_SANDBOX
from urllib.parse import quote_plus, unquote_plus, urlencode
from base64 import b64encode
from hashlib import sha1


TIMEOUT = 5 #seconds


def etrade_signature(cons_secret, token_secret, method, url, headers):
	key = bytes(quote_plus(cons_secret) + '&' + quote_plus(token_secret), 'utf-8')
	sorted_headers = [quote_plus(k) + '=' + quote_plus(headers[k]) for k in sorted(headers)]
	header_string = '&'.join(sorted_headers)
	base_string = quote_plus(method) + '&' + quote_plus(url) + '&' + quote_plus(header_string)
	raw = bytes(base_string, 'utf-8')

	hashed = hmac.new(key, raw, sha1)
	return quote_plus(b64encode(hashed.digest()).decode('utf-8'))


def request_etrade_token(url, cons_key, secret):
	timestamp = str(round(time.time()))
	nonce = '0bba225a40d1bbac2430aa0c6163ce44'
	access_token = ''
	access_secret = ''
	headers = {'oauth_consumer_key': cons_key, 'oauth_nonce': nonce, 'oauth_signature_method': 'HMAC-SHA1', 
				'oauth_timestamp': timestamp, 'oauth_callback': 'oob'}

	signature = etrade_signature(secret, access_secret, 'GET', url, headers)

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
	# print(r.text, d)
	print(d)
	return unquote_plus(d['oauth_token']), unquote_plus(d['oauth_token_secret'])

def get_access_token(url, cons_key, secret, oauth_token, oauth_token_secret, oauth_verifier):
	timestamp = str(round(time.time()))
	nonce = 'abba'
	signature_method = 'HMAC-SHA1'

	headers = {'oauth_consumer_key': cons_key, 'oauth_nonce': nonce, 'oauth_signature_method': signature_method,
				'oauth_timestamp': timestamp, 'oauth_token': oauth_token, 'oauth_verifier': oauth_verifier}

	signature = etrade_signature(secret, oauth_token_secret, 'GET', url, headers)
	headers['oauth_token'] = quote_plus(oauth_token)

	headers['oauth_signature'] = signature
	params = ','.join([k+'='+headers[k] for k in headers])
	authorization = {'Authorization': 'OAuth realm="",{}'.format(params)}
	# print(authorization)

	r = requests.get(url, headers=authorization, timeout=TIMEOUT)
	# print(r.text)
	print(r.status_code)
	d = {}
	if r.ok:
		info = r.text.split("&")
		for i in info:
			j, k = i.split('=')
			d[j] = k

	return unquote_plus(d['oauth_token']), unquote_plus(d['oauth_token_secret'])

if __name__ == "__main__":
	url = 'https://api.etrade.com/oauth/request_token'

	token, token_secret = request_etrade_token(url, CONSUMER_KEY_SANDBOX, CONSUMER_SECRET_SANDBOX)

	auth_url = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}'.format(CONSUMER_KEY_SANDBOX, token)
	webbrowser.open_new(auth_url)

	verification_code = input("Please accept agreement and enter text code after logging in\n")
	token_url = 'https://api.etrade.com/oauth/access_token'

	# token = unquote_plus(token)
	# token_secret = unquote_plus(token_secret)

	# print(token, token_secret)

	access_token, access_secret = get_access_token(token_url, CONSUMER_KEY_SANDBOX, CONSUMER_SECRET_SANDBOX, token, token_secret, verification_code)

	print(access_token, access_secret)

