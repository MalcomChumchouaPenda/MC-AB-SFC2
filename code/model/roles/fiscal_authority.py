from model.base import EcoRole


class FiscalAuthority(EcoRole):

    @property
    def tax_rate(self):
        return self.agent.tax_rate

    def get_gdp(self):
        return self.env.gdp

    def get_average_price(self):
        return self.env.spaces["good_market"].average_price

    def get_average_productivity(self):
        return self.env.spaces["good_market"].average_prod

    def find_citizens(self):
        return self.env.find_citizens()

    def pay_public_transfers(self, citizen, amount):
        self.env.pay_public_transfers(self, citizen, amount)
