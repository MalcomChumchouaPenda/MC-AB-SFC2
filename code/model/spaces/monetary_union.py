from agentpy import AgentDList
from model.base import EcoSpace, EcoAccount
from model.roles.monetary_authority import MonetaryAuthority


class MonetaryUnion(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.average_inflation = 0
        self.discount_rate = 0
        self.monetary_authority = None
        self.good_market = None
        self.bond_market = None
        self.credit_market = None

    #
    # Role / Account management
    #
    def add_monetary_authority(self, agent):
        role = self.add_role(MonetaryAuthority, agent, "monetary_authority")
        self.monetary_authority = role
        self.add_account(agent)
        return role

    #
    # Firm creation
    #
    def place_firm(self, firm, tradable):
        self.credit_market.add_borrower(firm)
        if tradable:
            self.good_market.add_producer(firm)

    #
    # Bank creation
    #
    def place_bank(self, bank):
        self.credit_market.add_lender(bank)
        self.bond_market.add_buyer(bank)

    #
    # Cash transactions
    #
    def transfer_cash(self, source, target, amount):
        source.account.debit_stock("cash", amount)
        target.account.credit_stock("cash", amount)

    #
    # Evolution
    #
    def update_average_inflation(self):
        countries = self.countries
        gdps = [c.gdp for c in countries.values()]
        weighted_inflations = [c.gdp * c.inflation for c in countries.values()]
        self.average_inflation = sum(weighted_inflations) / sum(gdps)
