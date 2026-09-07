from model.base import EcoRole


class MonetaryAuthority(EcoRole):

    @property
    def discount_rate(self):
        return self.agent.discount_rate

    def get_average_inflation(self):
        return self.space.average_inflation

    def get_union_discount_rate(self):
        return self.space.union.monetary_authority.discount_rate

    def transfer_profit(self, amount):
        self.space.transfer_central_bank_profits(amount)
