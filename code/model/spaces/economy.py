
from agentpy import AgentDList
from model.base import EcoSpace, EcoRole


class Economy(EcoSpace):

    def setup(self):
        super().setup()
        model = self.model

        # shared state
        self.gdp = 0
        self.inflation = 0
        self.prob_failure = 0

        # agent roles and accounts
        self.accounts = AgentDList(model)
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
        role = self.add_role(Citizen, agent, 'citizen')
        self.citizens.append(role)
        return role

    def add_company(self, agent, sector):
        role = self.add_role(Company, agent, 'company')
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
        company = self.add_company(bank, sector='B')
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




class Citizen(EcoRole):

    def setup(self):
        super().setup()
        self.resid_equity = 0

    #
    # Perception methods
    #
    def get_prob_failure(self):
        return self.space.prob_failure

    def find_investors(self):
        citizens = self.space.citizens
        investors = citizens.select(citizens.resid_equity > 0)
        if self in investors:
            investors.remove(self)
        return investors
    
    def get_bank_firm_ratios(self):
        companies = self.space.companies
        print(companies)
        firm_sector = companies.select([c.sector[0] == 'F' for c in companies])
        bank_sector = companies.select(companies.sector == 'B')
        if len(firm_sector) == 0:
            return 1.0, 1.0
        ratio1 = len(bank_sector) / len(firm_sector)
        ratio2 = sum(bank_sector.equity) / sum(firm_sector.equity)
        return ratio1, ratio2

    def get_sector_equity_range(self, sector):
        economy = self.space
        equities = [c.equity for c in economy.companies if c.sector == sector]
        if len(equities) == 0:
            return None
        return min(equities), max(equities)

    #
    # Creation actions
    #
    def create_firm(self, firm, shares, tradable):
        self.space.create_firm(firm, shares, tradable)

    def create_bank(self, bank, shares):
        self.space.create_bank(bank, shares)


class Company(EcoRole):
    
    def setup(self):
        super().setup()
        self.sector = ''
        self.equity = 0
        self.net_worth = 0
        self.defaulted = False

    #
    # perceptions method
    #
    def get_equity_shares(self):
        return [
            {"founder":v, "share":d["amount"]}
            for _, v, d in self.space.graph.edges(self, data=True)
        ]

    def get_average_wage(self):
        return self.space.average_wage

    #
    #  Actions methods
    #
    def pay_dividends(self, founder, amount):
        self.space.pay_dividends(self, founder, amount)

