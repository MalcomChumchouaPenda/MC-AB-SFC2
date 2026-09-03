from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.citizen import Citizen
from model.roles.company import Company


class Economy(EcoSpace):

    def setup(self):
        super().setup()
        model = self.model

        # shared state
        self.gdp = 0
        self.inflation = 0
        self.prob_failure = 0

        # agent roles and accounts
        self.citizens = AgentDList(model)
        self.companies = AgentDList(model)
        self.fiscal_auths = {}
        self.monetary_auths = {}

        # env sub spaces
        self.labor_markets = {}
        self.good_markets = {}
        self.deposit_markets = {}
        self.credit_market = None
        self.bond_market = None

    #
    # Role management
    #
    def add_citizen(self, agent):
        role = self.add_role(Citizen, agent, "citizen")
        self.citizens.append(role)
        return role

    def add_company(self, agent, sector):
        role = self.add_role(Company, agent, "company")
        role.sector = sector
        self.companies.append(role)
        return role

    #
    # Equity transactions
    #
    def fund_company(self, company, founder, amount):
        if self.graph.has_edge(company, founder):
            self.graph[company][founder]["share"] += amount
        else:
            self.graph.add_edge(company, founder, amount)
        company.account.debit_stock("equities", amount)
        company.account.credit_stock("cash", amount)
        founder.account.credit_stock("equities", amount)
        founder.account.debit_stock("cash", amount)

    def pay_dividends(self, company, founder, amount):
        company.account.debit_flow("dividends", amount)
        company.account.debit_stock("cash", amount)
        founder.account.credit_flow("dividends", amount)
        founder.account.credit_stock("cash", amount)

    #
    # Firm creation
    #
    def create_firm(self, firm, shares, tradable):
        sector = "FT" if tradable else "FNT"
        company = self.add_company(firm, sector=sector)
        self._place_firm_in_markets(firm, tradable)
        for share in shares:
            founder = share["founder"]
            amount = share["amount"]
            self.fund_company(company, founder, amount)

    def _place_firm_in_markets(self, firm, tradable):
        k = firm.position
        self.deposit_markets[k].add_depositor(firm)
        self.labor_markets[k].add_employer(firm)
        self.credit_market.add_borrower(firm)
        if tradable:
            self.good_markets[0].add_supplier(firm)
        else:
            self.good_markets[k].add_supplier(firm)

    #
    # Bank creation
    #
    def create_bank(self, bank, shares):
        company = self.add_company(bank, sector="B")
        for share in shares:
            founder = share["founder"]
            amount = share["amount"]
            self.fund_company(company, founder, amount)
        self._place_bank_in_markets(bank)

    def _place_bank_in_markets(self, bank):
        k = bank.position
        self.deposit_markets[k].add_bank(bank)
        self.credit_market.add_lender(bank)
        self.bond_market.add_buyer(bank)
