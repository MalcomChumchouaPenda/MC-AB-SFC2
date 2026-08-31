from ..base import EcoSpace
from ..agents.private import Firm, Bank
from ..roles import EquityHolderRole, EquityIssuerRole


class MonetaryUnion(EcoSpace):

    def setup(self):
        # agent refs
        self.central_bank = None

        # space refs
        self.goods_market = None
        self.credit_market = None
        self.bond_market = None


class Country(EcoSpace):

    def setup(self):
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
