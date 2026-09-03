from agentpy import AgentDList
from model.base import EcoSpace


class MonetaryUnion(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.inflation = 0
        self.monetary_authority = None
        self.good_market = None
        self.bond_market = None
        self.credit_market = None

    #
    # Role management
    #
    

    #
    # Firm creation
    #
    def place_firm(self, firm, tradable):
        self.credit_market.add_borrower(firm)
        if tradable:
            self.good_market.add_supplier(firm)

    #
    # Bank creation
    #
    def place_bank(self, bank):
        self.credit_market.add_lender(bank)
        self.bond_market.add_buyer(bank)
