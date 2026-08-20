from .base import EcoSpace
from .agents import FirmAgent, BankAgent, HouseholdAgent
from .roles import (
    EmployerRole,
    WorkerRole,
    GovernmentRole,
    TaxPayerRole,
    ConsumerRole,
    ProducerRole,
    EquityHolderRole,
    EquityIssuerRole,
    DepositHolderRole,
    DepositBankRole,
    DepositGuaranteeRole,
    LenderRole,
    BorrowerRole,
    UnionCentralBankRole,
    NationalCentralBankRole,
    CommercialBankRole,
    BondBuyerRole,
    BondIssuerRole,
)


class MonetaryUnionSpace(EcoSpace):

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self._discount_rate = 0.0
        self.average_inflation = 0
        self.central_bank_role = None
        self.countries = {}
        self.markets = {}

    @property
    def discount_rate(self):
        return self._discount_rate

    @discount_rate.setter
    def discount_rate(self, rate):
        self._discount_rate = rate
        for country in self.countries.values():
            country.discount_rate = rate

    def add_central_bank(self, central_bank):
        cb_role = self.add_role(UnionCentralBankRole, central_bank, "central_bank")
        self.central_bank_role = cb_role
        return cb_role

    def calc_average_inflation(self):
        countries = self.countries
        countries_gdps = [c.gdp for c in countries.values()]
        weighted_inflations = [c.gdp * c.inflation for c in countries.values()]
        return sum(weighted_inflations) / sum(countries_gdps)

    def update_statistics(self):
        for country in self.countries.values():
            country.update_statistics()
        self.average_inflation = self.calc_average_inflation()


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

    def assign_equity_holder(self, holder, issuer, share):
        self.graph.add_edge(holder, issuer, share=share)

    def distribute_dividends(self, issuer, amount):
        source = "reserves" if isinstance(issuer.agent, BankAgent) else "cash"
        issuer.increase_flow("dividends", amount)
        issuer.decrease_stock(source, amount)
        for _, holder, data in self.graph.edges(issuer, data=True):
            dividend = amount * data["share"]
            holder.increase_flow("dividends", dividend)
            holder.increase_stock("cash", dividend)

    def update_equity_holdings(self, issuer):
        new_equity = issuer.net_worth
        issuer.clear_stock("equity")
        issuer.increase_stock("equity", new_equity)
        for _, holder, data in self.graph.edges(issuer, data=True):
            value = new_equity * data["share"]
            holder.clear_stock("equity")
            holder.increase_stock("equity", value)

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
            self.assign_equity_holder(issuer, founder, share / equity)

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
            self.assign_equity_holder(issuer, founder, share / equity)

    def _create_bank_market_roles(self, bank):
        self.markets["credit"].add_lender(bank)
        self.markets["deposit"].add_deposit_bank(bank)
        self.markets["bond"].add_bond_buyer(bank)

    def update_statistics(self):
        self.markets["goods"].update_statistics()


class GoodsMarket(EcoSpace):

    def __init__(self, model, tradable=True, **kwargs):
        super().__init__(model, **kwargs)
        self.tradable = tradable
        self.gdp = 0
        self.inflation = 0.0
        self.average_price = 0
        self.average_productivity = 0

    def add_supplier(self, firm):
        return self.add_role(ProducerRole, firm, "producer")

    def add_consumer(self, household):
        key = "consumer_tradable" if self.tradable else "consumer_non_tradable"
        return self.add_role(ConsumerRole, household, key)

    def search_suppliers(self, psi):
        suppliers = [n for n in self.nodes if isinstance(n, ProducerRole)]
        return self.model.random.sample(suppliers, k=min(psi, len(suppliers)))

    def buy_goods(self, consumer, producer, quantity):
        amount = quantity * producer.price
        producer.decrease_stock("inventories", quantity)
        producer.increase_stock("cash", amount)
        producer.increase_flow("sales", amount)
        consumer.decrease_stock("cash", amount)
        if self.tradable:
            consumer.increase_flow("tradable_cons", amount)
        else:
            consumer.increase_flow("non_tradable_cons", amount)

    def update_statistics(self):
        nodes = self.graph.nodes  # roles
        producers = [n for n in nodes if isinstance(n, ProducerRole)]
        self.gdp = self.calc_gdp(producers)
        self.inflation = self.calc_inflation(producers)
        self.average_price = self.calc_average_price(producers)
        self.average_productivity = self.calc_average_productivity(producers)

    def calc_inflation(self, producers):
        prev_price = self.average_price
        current_price = self.calc_average_price(producers)
        if prev_price <= 0:
            return 0
        return (current_price - prev_price) / prev_price

    def calc_average_price(self, producers):
        return sum(prod.price for prod in producers) / max(1, len(producers))

    def calc_average_productivity(self, producers):
        return sum(prod.productivity for prod in producers) / max(1, len(producers))

    def calc_gdp(self, producers):
        return sum(prod.sales for prod in producers)


class LaborMarket(EcoSpace):

    def setup(self):
        self.average_wage = 0

    def add_employer(self, firm):
        return self.add_role(EmployerRole, firm, "employer")

    def add_worker(self, household):
        return self.add_role(WorkerRole, household, "worker")

    def create_job(self, worker, employer, quantity):
        wage = employer.wage_offer
        employer.labor_demand -= quantity
        self.graph.add_edge(worker, employer, wage=wage, quantity=quantity)

    def search_employers(self, psi):
        employers = [n for n in self.nodes if isinstance(n, EmployerRole)]
        return self.model.random.sample(employers, k=min(psi, len(employers)))

    def get_labor_sold(self, worker):
        edges = self.graph.edges  # contracts
        return sum(data["quantity"] for (w, e), data in edges.items() if w == worker)

    def update_statistics(self):
        nodes = self.graph.nodes  # roles
        employers = [n for n in nodes if isinstance(n, EmployerRole)]
        self.average_wage = self.calc_average_wage(employers)

    def calc_average_wage(self, employers):
        return sum([e.wage_offer for e in employers]) / max(1, len(employers))


class CreditMarket(EcoSpace):

    def add_borrower(self, firm):
        return self.add_role(BorrowerRole, firm, "borrower")

    def add_lender(self, bank):
        return self.add_role(LenderRole, bank, "lender")

    def search_lenders(self):
        return [n for n in self.nodes if isinstance(n, LenderRole)]

    def grant_loan(self, lender, borrower, amount, rate):
        borrower.loan_demand -= amount
        borrower.increase_stock("loans", amount)
        borrower.increase_stock("deposits", amount)
        lender.increase_stock("loans", amount)
        lender.increase_stock("deposits", amount)
        self.graph.add_edge(borrower, lender, amount=amount, rate=rate)


class DepositMarket(EcoSpace):

    def add_deposit_holder(self, agent):
        return self.add_role(DepositHolderRole, agent, "deposit_holder")

    def add_deposit_bank(self, bank):
        return self.add_role(DepositBankRole, bank, "deposit_bank")

    def add_deposit_guarantee(self, bank):
        return self.add_role(DepositGuaranteeRole, bank, "deposit_guarantee")

    def assign_deposit_bank(self, deposit_holder, deposit_bank):
        deposit_holder.deposit_bank = deposit_bank
        self.graph.add_edge(deposit_bank, deposit_holder)

    def pay_deposit_interest(self, deposit_bank):
        deposit_rate = deposit_bank.deposit_rate
        for _, holder in self.graph.edges(deposit_bank):
            interest = holder.deposits * deposit_rate
            holder.increase_stock("deposits", interest)
            holder.increase_flow("deposit_interest", interest)
            deposit_bank.increase_stock("deposits", interest)
            deposit_bank.increase_flow("deposit_interest", interest)

    def get_defaulted_banks(self):
        return [
            n
            for n in self.graph.nodes
            if isinstance(n, DepositBankRole) and n.defaulted
        ]

    def reimburse_deposits(self, guarantee, deposit_bank):
        for _, holder in self.graph.edges(deposit_bank):
            amount = holder.deposits
            holder.increase_stock("cash", amount)
            holder.decrease_stock("deposits", amount)
            guarantee.decrease_stock("reserves", amount)
            deposit_bank.decrease_stock("deposits", amount)

    def make_deposits(self, holder, bank, amount):
        holder.increase_stock("deposits", amount)
        holder.decrease_stock("cash", amount)
        bank.increase_stock("deposits", amount)
        bank.increase_stock("reserves", amount)


class BondMarket(EcoSpace):

    def add_bond_issuer(self, government):
        return self.add_role(BondIssuerRole, government, "bond_issuer")

    def add_bond_buyer(self, bank):
        return self.add_role(BondBuyerRole, bank, "bond_buyer")

    def get_bond_issuers(self):
        return [n for n in self.nodes if isinstance(n, BondIssuerRole)]

    def buy_bonds(self, buyer, issuer, amount):
        issuer.bond_supply -= amount
        issuer.increase_stock("bonds", amount)
        issuer.increase_stock("reserves", amount)
        if isinstance(buyer.agent, BankAgent):
            buyer.increase_stock("bonds", amount)
            buyer.decrease_stock("reserves", amount)
        else:
            buyer.increase_stock("bonds", amount)
            buyer.increase_stock("reserves", amount)
        self.graph.add_edge(issuer, buyer, amount=amount)

    def pay_bond_debt(self, issuer):
        graph = self.graph
        bond_rate = issuer.bond_rate
        for _, buyer in list(graph.edges(issuer)):
            principal = graph[issuer][buyer]["amount"]
            interest = bond_rate * principal
            issuer.decrease_stock("bonds", principal)
            issuer.increase_flow("bond_interest", interest)
            issuer.decrease_stock("reserves", principal + interest)
            if isinstance(buyer.agent, BankAgent):
                buyer.decrease_stock("bonds", principal)
                buyer.increase_flow("bond_interest", interest)
                buyer.increase_stock("reserves", principal + interest)
            else:
                buyer.decrease_stock("bonds", principal)
                buyer.increase_flow("bond_interest", interest)
                buyer.decrease_stock("reserves", principal + interest)
            self.graph.remove_edge(issuer, buyer)
