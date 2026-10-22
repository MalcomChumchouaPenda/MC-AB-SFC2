from model.extensions import EcoRole


class Company(EcoRole):

    def __init__(self, agent, env, prefix=""):
        super().__init__(agent, env, prefix=prefix)
        self.sector = ""
        self.defaulted = False

    @property
    def equity(self):
        amount = self.env.get_stock("equities", self.agent.id)
        return -1 * amount

    @property
    def net_worth(self):
        amount = self.env.get_stock("equities", self.agent.id)
        return -1 * amount

    #
    # perceptions method
    #

    def get_equity_shares(self):
        return self.env.links(self)

    def get_average_wage(self):
        return self.env.average_wage

    def get_tax_rate(self):
        return self.env.tax_rate

    def get_discount_rate(self):
        return self.env.discount_rate

    #
    #  Actions methods
    #
    def update_equity_shares(self, total_variation):
        env = self.env
        shares = self.get_equity_shares()
        total_shares = sum(share["value"] for share in shares)
        for share in shares:
            founder = share["citizen"]
            variation = share["value"] * total_variation / total_shares
            env.update_equity_share(self, founder, variation)

    def pay_dividends(self, founder, amount):
        self.env.pay_dividends(self, founder, amount)

    def pay_taxes(self, amount):
        self.env.pay_taxes(self, amount)

    def transfer_residual_cash(self, founder, amount):
        self.env.transfer_residual_cash(self, founder, amount)

    def request_advances(self, amount):
        self.env.request_advances(self, amount)

    def repay_advances(self, principal, interests):
        self.env.repay_advances(self, principal, interests)
