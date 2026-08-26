from ..base import EcoSpace
from ..agents import FirmAgent, BankAgent, HouseholdAgent
from ..roles import (
    GovernmentRole,
    TaxPayerRole,
    EquityHolderRole,
    EquityIssuerRole,
    NationalCentralBankRole,
    CommercialBankRole,
)


class CountrySpace(EcoSpace):

    def setup(self):
        self.monetary_union = None
        self.government_role = None
        self.central_bank_role = None
        self.bank_roles = []
        self.firm_roles = []
        self.discount_rate = 0.0
        self.tax_rate = 0
        self.markets = {}

    def add_government(self, govt):
        govt_role = self.add_role(GovernmentRole, govt, "government")
        self.government_role = govt_role
        return govt_role

    def add_central_bank(self, central_bank):
        cb_role = self.add_role(NationalCentralBankRole, central_bank, "central_bank")
        cb_role.government = self.government_role
        self.central_bank_role = cb_role
        self.graph.add_edge(cb_role, self.government_role)
        return cb_role

    @property
    def inflation(self):
        return self.markets["goods"].inflation

    @property
    def average_price(self):
        return self.markets["goods"].average_price

    @property
    def average_productivity(self):
        return self.markets["goods"].average_productivity

    @property
    def average_wage(self):
        return self.markets["labor"].average_wage

    def add_commercial_bank(self, agent):
        bank_role = self.add_role(CommercialBankRole, agent, "commercial_bank")
        bank_role.central_bank = self.central_bank_role
        self.graph.add_edge(self.central_bank_role, bank_role)
        return bank_role

    def add_tax_payer(self, agent):
        govt_role = self.government_role
        payer_role = self.add_role(TaxPayerRole, agent, "tax_payer")
        payer_role.government = govt_role
        self.graph.add_edge(govt_role, payer_role)
        return payer_role

    def pay_taxes(self, tax_payer, amount):
        govt_role = self.government_role
        govt_role.increase_stock("reserves", amount)
        govt_role.increase_flow("taxes", amount)
        if isinstance(tax_payer.agent, BankAgent):
            tax_payer.decrease_stock("reserves", amount)
            tax_payer.increase_flow("taxes", amount)
        else:
            tax_payer.decrease_stock("cash", amount)
            tax_payer.increase_flow("taxes", amount)

    def add_equity_issuer(self, agent):
        role = self.add_role(EquityIssuerRole, agent, "equity_issuer")
        if isinstance(agent, BankAgent):
            self.bank_roles.append(role)
        else:
            self.firm_roles.append(role)
        return role

    def add_equity_holder(self, household):
        return self.add_role(EquityHolderRole, household, "equity_holder")

    def assign_equity_holder(self, issuer, holder):
        self.graph.add_edge(holder, issuer)
        holder.equity_issuer = issuer

    def distribute_dividends(self, issuer, amount):
        source = "reserves" if isinstance(issuer.agent, BankAgent) else "cash"
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

    def transfer_profit(self, central_bank_role, amount):
        govt_role = central_bank_role.government
        govt_role.increase_flow("profit", amount)
        govt_role.increase_stock("reserves", amount)
        central_bank_role.increase_flow("profit", amount)
        central_bank_role.increase_stock("reserves", amount)

    def get_households(self):
        return [
            role
            for role in self.graph.nodes
            if isinstance(role, TaxPayerRole) and isinstance(role.agent, HouseholdAgent)
        ]

    def pay_public_transfers(self, governement, household, amount):
        governement.decrease_stock("reserves", amount)
        governement.increase_flow("public_transfers", amount)
        household.increase_stock("cash", amount)
        household.increase_flow("public_transfers", amount)

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
        firm = FirmAgent(self.model)
        firm.tradable = tradable
        issuer = self.add_equity_issuer(firm)
        self._distribute_firm_equity(issuer, founders)
        self._create_firm_market_roles(firm, tradable)
        # self.update_equity_shares(issuer)
        self.add_tax_payer(firm)
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
        self.markets["labor"].add_employer(firm)
        self.markets["credit"].add_borrower(firm)
        self.markets["deposit"].add_deposit_holder(firm)
        if tradable:
            self.monetary_union.markets["goods"].add_supplier(firm)
        else:
            self.markets["goods"].add_supplier(firm)

    def create_bank(self, founders):
        bank = BankAgent(self.model)
        issuer = self.add_equity_issuer(bank)
        self._distribute_bank_equity(issuer, founders)
        self._create_bank_market_roles(bank)
        self.add_tax_payer(bank)
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
        self.markets["credit"].add_lender(bank)
        self.markets["deposit"].add_deposit_bank(bank)
        self.model.bond_market.add_buyer(bank)

    def update_statistics(self):
        self.markets["goods"].update_statistics()
