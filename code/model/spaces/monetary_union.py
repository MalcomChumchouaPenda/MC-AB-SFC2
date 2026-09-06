from agentpy import AgentDList
from model.base import EcoSpace, EcoAccount
from model.roles.monetary_authority import MonetaryAuthority


class MonetaryUnion(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.inflation = 0
        self.discount_rate = 0
        self.accounts = AgentDList(self.model)
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
        self._create_account(agent)
        return role

    def add_account(self, agent):
        account = self._create_account(agent)
        agent.cb_account = self.monetary_authority.account
        return account

    def _create_account(self, agent):
        account = EcoAccount(agent.model)
        account.agent = agent
        agent.account = account
        self.accounts.append(account)
        return account

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

    #
    # Cash transactions
    #
    def transfer_cash(self, source, target, amount):
        source.account.debit_stock("cash", amount)
        target.account.credit_stock("cash", amount)


