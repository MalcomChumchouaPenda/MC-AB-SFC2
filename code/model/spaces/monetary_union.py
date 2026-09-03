from agentpy import AgentDList
from model.base import EcoSpace, EcoAccount


class MonetaryUnion(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.inflation = 0
        self.accounts = AgentDList(self.model)
        self.monetary_authority = None
        self.good_market = None
        self.bond_market = None
        self.credit_market = None

    #
    # Account management
    #
    def add_account(self, agent):
        account = EcoAccount(agent.model)
        account.agent_id = agent.id
        agent.account = account
        self.accounts.append(account)
        return account

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
