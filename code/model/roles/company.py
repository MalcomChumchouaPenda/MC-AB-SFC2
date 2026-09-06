from model.base import EcoRole


class Company(EcoRole):

    def setup(self):
        super().setup()
        self.sector = ""
        self.equity = 0
        self.net_worth = 0
        self.defaulted = False

    #
    # perceptions method
    #

    def get_equity_shares(self):
        return self.space.find_equity_shares(self)

    def get_average_wage(self):
        return self.space.average_wage

    def get_tax_rate(self):
        return self.space.fiscal_authority.tax_rate

    def get_discount_rate(self):
        return self.space.monetary_authority.discount_rate

    #
    #  Actions methods
    #
    def pay_dividends(self, founder, amount):
        self.space.pay_dividends(self, founder, amount)
