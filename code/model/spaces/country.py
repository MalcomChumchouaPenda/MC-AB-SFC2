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

        self.tax_rate = 0

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
        agent.cb_account = self.monetary_authority.account
        self.union.add_account(agent)
        self.citizens.append(role)
        return role

    def add_company(self, agent, sector):
        role = self.add_role(Company, agent, "company")
        role.sector = sector
        agent.cb_account = self.monetary_authority.account
        self.companies.append(role)
        self.union.add_account(agent)
        return role

    #
    # Current indicators
    #

    def calc_bank_number_ratio(self):
        companies = self.companies
        firm_sector = companies.select([c.sector[0] == "F" for c in companies])
        if len(firm_sector) == 0:
            return 1.0
        bank_sector = companies.select(companies.sector == "B")
        return len(bank_sector) / len(firm_sector)

    def calc_bank_equity_ratio(self):
        companies = self.companies
        firm_sector = companies.select([c.sector[0] == "F" for c in companies])
        if len(firm_sector) == 0:
            return 1.0
        bank_sector = companies.select(companies.sector == "B")
        return sum(bank_sector.equity) / sum(firm_sector.equity)

    def calc_sector_equity_range(self, sector):
        equities = [c.equity for c in self.companies if c.sector == sector]
        if len(equities) == 0:
            return None
        return min(equities), max(equities)

    #
    # Equity investment
    #

    def find_investors(self, initiator=None):
        citizens = self.citizens
        investors = citizens.select(citizens.resid_equity > 0)
        if initiator in investors:
            investors.remove(initiator)
        return investors

    def fund_company(self, company, founder, amount):
        if self.graph.has_edge(company, founder):
            self.graph[company][founder]["value"] += amount
        else:
            self.graph.add_edge(company, founder, value=amount)
        company.debit_stock("equities", amount)
        company.credit_stock("cash", amount)
        founder.credit_stock("equities", amount)
        founder.debit_stock("cash", amount)
        founder.resid_equity -= amount

    #
    # Dividends
    #

    def find_equity_shares(self, company):
        return [
            {"founder": founder, **data}
            for _, founder, data in self.graph.edges(company, data=True)
        ]

    def pay_dividends(self, company, founder, amount):
        company.debit_flow("dividends", amount)
        company.debit_stock("cash", amount)
        founder.credit_flow("dividends", amount)
        founder.credit_stock("cash", amount)

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
            self.good_market.add_producer(firm)

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

    #
    # Evolution
    #
    def update_state(self):
        companies = self.companies
        defaults = companies.select(companies.defaulted == True)
        self.prob_failure = len(defaults) / max(1, len(companies))
        self.inflation = self.good_market.calc_inflation()
        self.gdp = self.good_market.calc_gdp()
