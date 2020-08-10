import etrade_auth

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

    return r.text

