from ..base import EcoRole


class EquityIssuerRole(EcoRole):

    @property
    def equity(self):
        return self.agent.equity

    @property
    def net_worth(self):
        return self.agent.net_worth

    def get_average_wage(self):
        return self.space.average_wage

    def update_equity_holdings(self):
        self.space.update_equity_holdings(self)

    def distribute_dividends(self, amount):
        self.space.distribute_dividends(self, amount)

    def close_firm(self, firm):
        self.space.close_firm(firm)

    def close_bank(self, bank):
        self.space.close_bank(bank)
