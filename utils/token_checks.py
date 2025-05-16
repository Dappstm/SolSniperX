import requests

def is_token_rug(token_address):
    url = f"https://api.pump.fun/token/{token_address}"
    resp = requests.get(url).json()
    liquidity = resp.get("liquidity", 0)
    holders = resp.get("holders", 0)
    if liquidity < 1 or holders < 5:
        return True
    return False

def get_holder_count(token_address):
    url = f"https://api.pump.fun/token/{token_address}"
    resp = requests.get(url).json()
    return resp.get("holders", 0)
