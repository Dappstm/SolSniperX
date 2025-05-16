class UserSession:
    def __init__(self):
        self.private_key = None
        self.sol_amount = 0.01
        self.sniping = False

    def masked_wallet(self):
        return self.private_key[:4] + "..." + self.private_key[-4:] if self.private_key else "Not Set"