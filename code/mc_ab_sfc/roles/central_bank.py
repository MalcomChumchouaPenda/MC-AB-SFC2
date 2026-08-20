from ..base import EcoRole


class UnionCentralBankRole(EcoRole):

    @property
    def discount_rate(self):
        return self.space.discount_rate

    @discount_rate.setter
    def discount_rate(self, rate):
        self.space.discount_rate = rate

    def get_average_inflation(self):
        return self.space.average_inflation


class NationalCentralBankRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.government = None

    @property
    def discount_rate(self):
        return self.space.discount_rate

    def get_average_inflation(self):
        return self.space.average_inflation

    def transfer_profit(self, amount):
        self.space.transfer_profit(self, amount)
