from model.base import EcoRole


class Company(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.sector = ""
        self.equity = 0
        self.net_worth = 0
        self.defaulted = False

    #
    # perceptions method
    #

    def get_equity_shares(self):
        return self.env.find_links(self, "founder")

    def get_average_wage(self):
        return self.env.average_wage

    def get_tax_rate(self):
        return self.env.fiscal_authority.tax_rate

    def get_discount_rate(self):
        return self.env.monetary_authority.discount_rate

    #
    #  Actions methods
    #
    def update_equity_share(self, founder, variation):
        self.env.update_equity_share(self, founder, variation)

    def pay_dividends(self, founder, amount):
        self.env.pay_dividends(self, founder, amount)

    def pay_taxes(self, amount):
        self.env.pay_taxes(self, amount)

    def transfer_residual_cash(self, founder, amount):
        self.env.transfer_residual_cash(self, founder, amount)
