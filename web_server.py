import webbrowser
from etrade_auth import *
from flask import Flask, request
from config import CONSUMER_KEY_SANDBOX as CONS_KEY, CONSUMER_SECRET_SANDBOX as CONS_SECRET

app = Flask(__name__)

@app.before_first_request
def setup_credentials():
	global ACCESS_TOKEN, ACCESS_SECRET
	ACCESS_TOKEN, ACCESS_SECRET = login()
#----------------------------------------------------

#ACCOUNTS

#List Accounts

#Account Balances

#List Transactions

#List Transaction Details

#View Portfolio

#----------------------------------------------------

#ALERTS

#List Alerts

#List Alert Details

#Delete Alert

#----------------------------------------------------

#MARKET

#Get Quotes

#Look Up Product

#Get Option Chains

@app.route('/optionchains/<symbol>')
def get_option_chain_data(symbol, sandbox=True, json=True):
    sandbox_url = 'https://apisb.etrade.com/v1/market/optionchains'
    live_url = 'https://api.etrade.com/v1/market/optionchains'
    if sandbox:
        url = sandbox_url
    else:
        url = live_url
    if json:
        url += '.json'

    allowable_params = ['expiryYear', 'expiryMonth', 'expiryDay', 'strikePriceNear', 'noOfStrikes', 'includeWeekly', 'skipAdjusted',
    					'optionCategory', 'chainType', 'priceType']
    params = {'symbol': symbol}

    for param in allowable_params:
    	val = request.args.get(param)
    	if val:
    		params[param] = val
    authorization = create_authorization_header(
        url, ACCESS_TOKEN, ACCESS_SECRET, params=params)
    
    param_formatter = [str(k) + '=' + str(params[k]) for k in params]
    full_url = url + '?' + '&'.join(param_formatter)
    r = requests.get(full_url, headers=authorization, timeout=TIMEOUT)

    return r.text

#Get Option Expire Dates

#---------------------------------------------------

#ORDER

#List Orders

#Preview Order

#Place Order

#Cancel Order

#Change Previewed Order

#Place Changed Order
