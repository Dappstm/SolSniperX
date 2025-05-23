import requests

def check_insider_distribution(token_address):
    url = f"https://frontend-api-v3.pump.fun/coins/latest{token_address}"
    resp = requests.get(url).json()
    holders_data = resp.get("holders_info", [])
    largest = max([h["percentage"] for h in holders_data[:5]], default=0)
    return largest < 10  # Not too insider-heavy
