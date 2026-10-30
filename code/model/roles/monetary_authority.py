import math
from model.extensions import EcoRole


class MonetaryAuthority(EcoRole):

    #
    # Perceptions
    #

    def get_cash(self):
        env = self.env
        model = env.model
        if model.t == 200:
            total = sum([cash.amount for cash in self.env.cash.values()])
            print(f"\nat {model.t} n_cash={len(env.cash)} total_cash={total} in {env}")
            print(f"\n{ {key :c.amount for key, c in env.cash.items()} }\n")
        return math.fsum([cash.amount for cash in self.env.cash.values()])

    #
    # Actions
    #
    def transfer_profit(self, amount):
        self.env.transfer_central_bank_profits(amount)

    def set_discount_rate(self, rate):
        self.env.discount_rate = rate
