
from model.base import EcoSpace, EcoRole
from ..agents.firm import Firm
from ..agents.bank import Bank


class Country(EcoSpace):

    def setup(self):
        super().setup()
        # agent refs
        self.government = None
        self.central_bank = None

        # space refs
        self.union = None
        self.goods_market = None
        self.labor_market = None
        self.deposit_market = None

        self.discount_rate = 0.0
        self.tax_rate = 0
        self.markets = {}

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

    def add_equity_issuer(self, agent):
        role = self.add_role(EquityIssuerRole, agent, "equity_issuer")
        # if isinstance(agent, Bank):
        #     self.bank_roles.append(role)
        # else:
        #     self.firm_roles.append(role)
        return role

    def add_equity_holder(self, household):
        return self.add_role(EquityHolderRole, household, "equity_holder")

    def assign_equity_holder(self, issuer, holder):
        self.graph.add_edge(holder, issuer)
        holder.equity_issuer = issuer

    def distribute_dividends(self, issuer, amount):
        source = "reserves" if isinstance(issuer.agent, Bank) else "cash"
        issuer.increase_flow("dividends", amount)
        issuer.decrease_stock(source, amount)
        for _, holder in self.graph.edges(issuer):
            dividend = amount * holder.share
            holder.increase_flow("dividends", dividend)
            holder.increase_stock("cash", dividend)

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
            if isinstance(n, EquityHolderRole)
            and n.desired_equity > 0
            and n.equity == 0
            and n is not exclude
        ]

    def create_firm(self, founders, tradable):
        firm = Firm(self.model)
        firm.tradable = tradable
        issuer = self.add_equity_issuer(firm)
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
            self.assign_equity_holder(issuer, founder)

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
        issuer = self.add_equity_issuer(bank)
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
            self.assign_equity_holder(issuer, founder)

    def _create_bank_market_roles(self, bank):
        self.union.credit_market.add_lender(bank)
        self.union.bond_market.add_buyer(bank)
        self.deposit_market.add_bank(bank)

    def update_statistics(self):
        self.goods_market.update_statistics()


class EquityIssuerRole(EcoRole):

    @property
    def equity(self):
        return self.agent.equity

    @property
    def net_worth(self):
        return self.agent.net_worth

    def get_average_wage(self):
        return self.space.average_wage

    def update_equity_holdings(self):
        self.space.update_equity_holdings(self)

    def distribute_dividends(self, amount):
        self.space.distribute_dividends(self, amount)

    def close_firm(self, firm):
        self.space.close_firm(firm)

    def close_bank(self, bank):
        self.space.close_bank(bank)


class EquityHolderRole(EcoRole):

    def setup(self):
        super().setup()
        self.equity_issuer = None
        self.share = 0.0


    @property
    def equity(self):
        return self.agent.equity

    @property
    def desired_equity(self):
        return self.agent.desired_equity

    def get_default_probability(self):
        return self.space.default_probability

    def get_potential_investors(self):
        return self.space.get_potential_investors(exclude=self)

    def get_bank_firm_number_ratio(self):
        country = self.space
        if len(country.firm_roles) == 0:
            return 1.0
        return len(country.bank_roles) / len(country.firm_roles)

    def get_bank_firm_equity_ratio(self):
        country = self.space
        if len(country.firm_roles) == 0:
            return 1.0
        firm_equities = sum([r.equity for r in country.firm_roles])
        bank_equities = sum([r.equity for r in country.bank_roles])
        return bank_equities / firm_equities

    def get_sector_equity_range(self, sector):
        country = self.space
        if sector == "banks":
            equities = [r.equity for r in country.bank_roles]
        else:
            firms = [r.agent for r in country.firm_roles]
            if sector == "tradable_firms":
                equities = [f.equity for f in firms if f.tradable]
            else:
                equities = [f.equity for f in firms if not f.tradable]
        if len(equities) == 0:
            return None
        return min(equities), max(equities)

    def create_firm(self, founders, tradable):
        self.space.create_firm(founders, tradable)

    def create_bank(self, founders):
        self.space.create_bank(founders)
