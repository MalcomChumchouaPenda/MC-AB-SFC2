
from model.base import EcoSpace, EcoRole
from ..agents.firm import Firm
from ..agents.bank import Bank


class Country(EcoSpace):

    def setup(self):
        super().setup()
        self.government = None
        self.central_bank = None
        self.union = None
        self.goods_market = None
        self.labor_market = None
        self.deposit_market = None
        self.citizens = []
        self.companies = []
        self.discount_rate = 0.0
        self.tax_rate = 0
        
    @property
    def inflation(self):
        return self.goods_market.inflation

    @property
    def average_price(self):
        return self.goods_market.average_price

    @property
    def average_productivity(self):
        return self.goods_market.average_productivity

    @property
    def average_wage(self):
        return self.labor_market.average_wage


    def add_citizen(self, household):
        role = self.add_role(Citizen, household)
        self.citizens.append(role)
        return role

    def add_company(self, agent, founders, sector):
        company = self.add_role(Company, agent)
        company.sector = sector
        graph = self.graph
        for founder in founders:
            graph.add_edge(company, founder)
            founder.company = company
        self.companies.append(company)
        return company

    def fund_company(self, founder, company, amount):
        founder.equity += amount
        founder.cash -= amount
        company.equity += amount
        company.cash += amount

    def pay_dividends(self, company, founder, amount):
        company.dividends += amount
        company.cash -= amount
        founder.dividends += amount
        founder.cash += amount

    def update_equity_holdings(self, issuer):
        new_equity = issuer.net_worth
        issuer.clear_stock("equity")
        issuer.increase_stock("equity", new_equity)
        for _, holder in self.graph.edges(issuer):
            value = new_equity * holder.share
            holder.clear_stock("equity")
            holder.increase_stock("equity", value)

    def update_equity_shares(self, issuer):
        for _, holder in self.graph.edges(issuer):
            holder.share = holder.equity / issuer.equity

    def request_cash_advances(self, bank_role, amount):
        central_role = self.central_bank_role
        central_role.increase_stock("reserves", amount)
        central_role.increase_stock("cash_advances", amount)
        bank_role.increase_stock("reserves", amount)
        bank_role.increase_stock("cash_advances", amount)

    def get_potential_investors(self, exclude=None):
        return [
            n
            for n in self.graph.nodes()
            if isinstance(n, Citizen)
            and n.desired_equity > 0
            and n.equity == 0
            and n is not exclude
        ]

    def create_firm(self, founders, tradable):
        firm = Firm(self.model)
        firm.tradable = tradable
        issuer = self.add_company(firm)
        self._distribute_firm_equity(issuer, founders)
        self._create_firm_market_roles(firm, tradable)
        # self.update_equity_shares(issuer) # TODO
        self.model.firms.append(firm)
        return firm

    def _distribute_firm_equity(self, issuer, founders):
        equity = sum([f.desired_equity for f in founders])
        issuer.increase_stock("equity", equity)
        issuer.increase_stock("cash", equity)
        for founder in founders:
            share = founder.desired_equity
            founder.increase_stock("equity", share)
            founder.decrease_stock("cash", share)
            self.assign_citizen(issuer, founder)

    def _create_firm_market_roles(self, firm, tradable):
        self.labor_market.add_employer(firm)
        self.union.credit_market.add_borrower(firm)
        self.deposit_market.add_client(firm)
        if tradable:
            self.union.goods_market.add_supplier(firm)
        else:
            self.goods_market.add_supplier(firm)

    def create_bank(self, founders):
        bank = Bank(self.model)
        issuer = self.add_company(bank)
        self._distribute_bank_equity(issuer, founders)
        self._create_bank_market_roles(bank)
        self.model.banks.append(bank)
        return bank

    def _distribute_bank_equity(self, issuer, founders):
        equity = sum([f.desired_equity for f in founders])
        issuer.increase_stock("equity", equity)
        issuer.increase_stock("reserves", equity)
        for founder in founders:
            share = founder.desired_equity
            founder.increase_stock("equity", share)
            founder.decrease_stock("cash", share)
            self.assign_citizen(issuer, founder)

    def _create_bank_market_roles(self, bank):
        self.union.credit_market.add_lender(bank)
        self.union.bond_market.add_buyer(bank)
        self.deposit_market.add_bank(bank)

    def update_statistics(self):
        self.goods_market.update_statistics()


class Company(EcoRole):

    def setup(self):
        super().setup()
        self.name = 'company'
        self.sector = ''
        self.equity = 0
        self.net_worth = 0
        self.defaulted = False

    def get_founders(self):
        return [
            citizen
            for _, citizen in self.space.graph.edges(self)
        ]

    def get_average_wage(self):
        return self.space.average_wage

    def update_equity(self, founder, value):
        self.space.update_equity(self, founder, value)

    def pay_dividends(self, founder, amount):
        self.space.pay_dividends(self, founder, amount)



class Citizen(EcoRole):

    def setup(self):
        super().setup()
        self.name = "citizen"
        self.equity = 0
        self.desired_equity = 0
        self.company = None

    def get_prob_failure(self):
        return self.space.prob_failure

    def find_investors(self):
        for citizen in self.space.citizens:
            print(citizen)
        return [
            citizen
            for citizen in self.space.citizens
            if citizen.desired_equity > 0 and citizen.equity == 0 and citizen is not self
        ]

    def get_bank_firm_ratios(self):
        country = self.space
        fequities = [c.equity for c in country.companies if c.sector[0] == 'F']
        bequities = [c.equity for c in country.companies if c.sector[0] == 'B']
        if len(fequities) == 0:
            return 1.0, 1.0
        return len(bequities) / len(fequities), sum(bequities) / sum(fequities)

    def get_sector_equity_range(self, sector):
        country = self.space
        equities = [c.equity for c in country.companies if c.sector == sector]
        if len(equities) == 0:
            return None
        return min(equities), max(equities)

    def create_firm(self, firm, founders, tradable=False):
        self.space.create_firm(firm, founders, tradable)

    def create_bank(self, bank, founders):
        self.space.create_bank(bank, founders)
