from model.base import EcoRole


class FiscalAuthority(EcoRole):

    @property
    def tax_rate(self):
        return self.agent.tax_rate

    def get_gdp(self):
        return self.space.gdp

    def get_average_price(self):
        return self.space.good_market.average_price

    def get_average_productivity(self):
        return self.space.good_market.average_prod

    def find_citizens(self):
        return self.space.find_citizens()

    def pay_public_transfers(self, citizen, amount):
        self.space.pay_public_transfers(self, citizen, amount)