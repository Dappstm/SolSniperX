import requests
from utils.token_checks import is_token_rug
from utils.insider_monitor import check_insider_distribution
from utils.jupiter_swap import get_best_route, execute_swap

class WalletSniper:
    def __init__(self, config, notifier):
        self.rpc_url = config["rpc_url"]
        self.auto_sell_percent = config["auto_sell_percent"]
        self.slippage = config["slippage"]
        self.notifier = notifier

    def fetch_wallet_buys(self, wallet):
        try:
            url = f"https://api.pump.fun/user/{wallet}"
            resp = requests.get(url, timeout=10).json()
            return resp.get("purchases", [])
        except Exception as e:
            print(f"Error fetching purchases for {wallet}: {e}")
            return []

    def should_buy(self, token):
        try:
            if is_token_rug(token["mint"]):
                return False
            if not check_insider_distribution(token["mint"]):
                return False
            return True
        except Exception as e:
            print(f"Error during token check: {e}")
            return False

    def buy_token(self, token, private_key, amount):
        try:
            route = get_best_route("So11111111111111111111111111111111111111112", token["mint"], int(amount * 1e9))
            execute_swap(private_key, route)
            self.notifier(f"✅ Bought {token.get('symbol', 'TOKEN')} — {token['mint']}")
        except Exception as e:
            self.notifier(f"❌ Failed to buy {token['mint']}: {e}")
