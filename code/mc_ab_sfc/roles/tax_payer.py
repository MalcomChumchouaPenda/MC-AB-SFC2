from ..base import EcoRole


class TaxPayerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.government = None

    def get_tax_rate(self):
        return self.government.tax_rate

    def pay_taxes(self, amount):
        self.space.pay_taxes(self, amount)
