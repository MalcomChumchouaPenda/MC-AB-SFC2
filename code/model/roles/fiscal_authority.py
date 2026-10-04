from model.base import EcoRole


class FiscalAuthority(EcoRole):

    #
    # Perceptions
    #
    def get_gdp(self):
        return self.env.gdp

    def get_discount_rate(self):
        return self.env.discount_rate

    def get_average_price(self):
        return self.env.spaces["goods_market"].average_price

    def get_average_productivity(self):
        return self.env.spaces["goods_market"].average_prod

    def find_citizens(self):
        return self.env.find_all_roles("citizen")

    #
    # Perceptions
    #
    def pay_public_transfers(self, citizen, amount):
        self.env.pay_public_transfers(self, citizen, amount)

    def set_tax_rate(self, rate):
        self.env.tax_rate = rate
