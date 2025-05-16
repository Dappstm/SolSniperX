from wallet_sniper import WalletSniper
from config import CONFIG
import threading, time

user_sessions = {}
sniping_threads = {}

def start_sniping_for_user(uid, session):
    if session.sniping:
        return
    session.sniping = True
    sniper = WalletSniper(CONFIG, lambda msg: print(f"[{uid}] {msg}"))

    def run():
        while session.sniping:
            try:
                with open("watched_wallets.txt") as f:
                    wallets = [line.strip() for line in f if line.strip()]
                for w in wallets:
                    buys = sniper.fetch_wallet_buys(w)
                    for token in buys:
                        if sniper.should_buy(token):
                            sniper.buy_token(token, session.private_key, session.sol_amount)
                time.sleep(CONFIG["token_check_delay"])
            except Exception as e:
                print(f"[{uid}] Sniping error: {e}")

    t = threading.Thread(target=run, daemon=True)
    t.start()
    sniping_threads[uid] = t

def stop_sniping_for_user(uid):
    session = user_sessions.get(uid)
    if session:
        session.sniping = False
