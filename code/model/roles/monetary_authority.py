from model.extensions import EcoRole


class MonetaryAuthority(EcoRole):

    #
    # Perceptions
    #

    def get_cash_amount(self):
        return sum(cash.amount for cash in self.env.cash.values())

    def get_cash_interests(self):
        return sum(cash.interests for cash in self.env.cash.values())

    #
    # Actions
    #
    def transfer_profit(self, amount):
        self.env.transfer_central_bank_profits(amount)

    def set_discount_rate(self, rate):
        self.env.discount_rate = rate
