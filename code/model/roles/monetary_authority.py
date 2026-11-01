from model.extensions import EcoRole


class MonetaryAuthority(EcoRole):

    #
    # Perceptions
    #

    @property
    def cash(self):
        return [
            {"amount": cash.amount, "interests": cash.interests}
            for cash in self.env.cash.values()
        ]

    #
    # Actions
    #
    def transfer_profit(self, amount):
        self.env.transfer_central_bank_profits(amount)

    def set_discount_rate(self, rate):
        self.env.discount_rate = rate
