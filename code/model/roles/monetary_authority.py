from model.base import EcoRole


class MonetaryAuthority(EcoRole):

    @property
    def discount_rate(self):
        return self.agent.discount_rate

    def transfer_profit(self, amount):
        self.env.transfer_central_bank_profits(amount)
