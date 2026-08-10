from .base import EcoSpace
from .agents import BankAgent
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
    LenderRole,
    BorrowerRole,
    CentralBankRole,
    CommercialBankRole,
    BondBuyerRole,
    BondIssuerRole,
)


class MonetaryUnionSpace(EcoSpace):

    def __init__(self, model, central_bank, **kwargs):
        super().__init__(model, **kwargs)
        central_role = self.add_role(CentralBankRole, central_bank, "central_bank")
        self.central_bank_role = central_role
        self.countries = {}
        self.markets = {}

    def add_commercial_bank(self, agent):
        bank_role = self.add_role(CommercialBankRole, agent, "commercial_bank")
        bank_role.central_bank = self.central_bank_role
        self.graph.add_edge(self.central_bank_role, bank_role)
        return bank_role

    def request_cash_advances(self, bank_role, amount):
        central_role = self.central_bank_role
        central_role.increase_stock("reserves", amount)
        central_role.increase_stock("cash_advances", amount)
        bank_role.increase_stock("reserves", amount)
        bank_role.increase_stock("cash_advances", amount)


class CountrySpace(EcoSpace):

    def __init__(self, model, government, **kwargs):
        super().__init__(model, **kwargs)
        govt_role = self.add_role(GovernmentRole, government, "government_role")
        self.government_role = govt_role
        self.markets = {}

    def setup(self):
        self.tax_rate = 0

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
        return self.add_role(EquityIssuerRole, agent, "equity_issuer")

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


class GoodsMarket(EcoSpace):

    def __init__(self, model, tradable=True, **kwargs):
        super().__init__(model, **kwargs)
        self.tradable = tradable
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
        producer.increase_stock("cash", amount)
        producer.increase_flow("sales", amount)
        producer.decrease_stock("inventories", quantity)
        consumer.decrease_stock("cash", amount)
        if self.tradable:
            consumer.increase_flow("tradable_cons", amount)
        else:
            consumer.increase_flow("non_tradable_cons", amount)

    def update_statistics(self):
        nodes = self.graph.nodes  # roles
        producers = [n for n in nodes if isinstance(n, ProducerRole)]
        self.average_price = self._calc_average_price(producers)
        self.average_productivity = self._calc_average_productivity(producers)

    def _calc_average_price(self, producers):
        return sum(prod.price for prod in producers) / max(1, len(producers))

    def _calc_average_productivity(self, producers):
        return sum(prod.productivity for prod in producers) / max(1, len(producers))


class LaborMarket(EcoSpace):

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

    def add_deposit_holder(self, household):
        return self.add_role(DepositHolderRole, household, "deposit_holder")

    def add_deposit_bank(self, bank):
        return self.add_role(DepositBankRole, bank, "deposit_bank")

    def assign_deposit_bank(self, deposit_holder, deposit_bank):
        deposit_holder.deposit_bank = deposit_bank
        self.graph.add_edge(deposit_bank, deposit_holder)

    def pay_deposit_interest(self, deposit_bank):
        deposit_rate = deposit_bank.deposit_rate
        print(deposit_rate, deposit_bank)
        for _, holder in self.graph.edges(deposit_bank):
            interest = holder.deposits * deposit_rate
            holder.increase_stock("deposits", interest)
            holder.increase_flow("deposit_interest", interest)
            deposit_bank.increase_stock("deposits", interest)
            deposit_bank.increase_flow("deposit_interest", interest)


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
