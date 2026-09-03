from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.citizen import Citizen
from model.roles.company import Company
from model.roles.monetary_authority import MonetaryAuthority
from model.roles.fiscal_authority import FiscalAuthority


class Country(EcoSpace):

    def setup(self):
        super().setup()
        model = self.model
        self.gdp = 0
        self.inflation = 0
        self.prob_failure = 0

        # roles
        self.citizens = AgentDList(model)
        self.companies = AgentDList(model)
        self.monetary_authority = None
        self.fiscal_authority = None

        # sub spaces
        self.union = None
        self.good_market = None
        self.labor_market = None
        self.deposit_market = None

    #
    # Role management
    #

    def add_fiscal_authority(self, agent):
        role = self.add_role(FiscalAuthority, agent, "fiscal_authority")
        self.union.add_account(agent)
        self.fiscal_authority = role
        return role

    def add_monetary_authority(self, agent):
        role = self.add_role(MonetaryAuthority, agent, "monetary_authority")
        self.union.add_account(agent)
        self.monetary_authority = role
        return role

    def add_citizen(self, agent):
        role = self.add_role(Citizen, agent, "citizen")
        self.union.add_account(agent)
        self.citizens.append(role)
        return role

    def add_company(self, agent, sector):
        role = self.add_role(Company, agent, "company")
        role.sector = sector
        self.companies.append(role)
        self.union.add_account(agent)
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
        founder.resid_equity -= amount

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
        self._place_firm(firm, tradable)
        for share in shares:
            founder = share["founder"]
            amount = share["amount"]
            self.fund_company(company, founder, amount)

    def _place_firm(self, firm, tradable):
        self.union.place_firm(firm, tradable=tradable)
        self.deposit_market.add_depositor(firm)
        self.labor_market.add_employer(firm)
        if not tradable:
            self.good_market.add_supplier(firm)

    #
    # Bank creation
    #
    def create_bank(self, bank, shares):
        company = self.add_company(bank, sector="B")
        for share in shares:
            founder = share["founder"]
            amount = share["amount"]
            self.fund_company(company, founder, amount)
        self.union.place_bank(bank)
        self.deposit_market.add_bank(bank)
