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
        return [
            {"founder": founder, "share": data["amount"]}
            for _, founder, data in self.space.graph.edges(self, data=True)
        ]

    def get_average_wage(self):
        return self.space.average_wage

    #
    #  Actions methods
    #
    def pay_dividends(self, founder, amount):
        self.space.pay_dividends(self, founder, amount)
