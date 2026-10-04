from model.base import EcoRole


class MonetaryAuthority(EcoRole):

    #
    # Actions
    #
    def transfer_profit(self, amount):
        self.env.transfer_central_bank_profits(amount)

    def set_discount_rate(self, rate):
        self.env.discount_rate = rate
