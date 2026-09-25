from model.base import EcoRole


class MonetaryAuthority(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.discount_rate = 0.0

    def transfer_profit(self, amount):
        self.env.transfer_central_bank_profits(amount)
