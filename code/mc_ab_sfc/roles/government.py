from ..base import EcoRole


class GovernmentRole(EcoRole):

    @property
    def tax_rate(self):
        return self.agent.tax_rate

    def get_gdp(self):
        return self.space.gdp

    def get_average_price(self):
        return self.space.average_price

    def get_average_productivity(self):
        return self.space.average_productivity

    def get_discount_rate(self):
        return self.space.discount_rate

    def get_households(self):
        return self.space.get_households()

    def pay_public_transfers(self, household, transfers):
        self.space.pay_public_transfers(self, household, transfers)
