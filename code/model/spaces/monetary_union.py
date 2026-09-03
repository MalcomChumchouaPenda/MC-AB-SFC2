from agentpy import AgentDList
from model.base import EcoSpace


class MonetaryUnion(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.inflation = 0
        self.monetary_authority = None

    #
    # Role management
    #
    

    #
    # Firm creation
    #
    def place_firm(self, firm, tradable):
        self.sub_spaces["credit_market"].add_borrower(firm)
        if tradable:
            self.sub_spaces["good_market"].add_supplier(firm)

    #
    # Bank creation
    #
    def place_bank(self, bank):
        self.sub_spaces["credit_market"].add_lender(bank)
        self.sub_spaces["bond_market"].add_buyer(bank)
