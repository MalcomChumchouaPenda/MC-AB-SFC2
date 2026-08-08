from .base import EcoSpace
from .roles import (
    EmployerRole,
    WorkerRole,
    CitizenRole,
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
)


class MonetaryUnionSpace(EcoSpace):

    def setup(self):
        super().setup()
        self.countries = {}
        self.markets = {}


class CountrySpace(EcoSpace):

    def setup(self):
        super().setup()
        self.markets = {}
        self.tax_rate = 0

    def add_citizen(self, household):
        return self.add_role(CitizenRole, household, "citizen")

    def add_tax_payer(self, agent):
        return self.add_role(TaxPayerRole, agent, "tax_payer")


class CentralBankSpace:
    pass


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


class DepositMarket(EcoSpace):

    def add_deposit_holder(self, household):
        return self.add_role(DepositHolderRole, household, "deposit_holder")

    def add_deposit_bank(self, bank):
        return self.add_role(DepositBankRole, bank, "deposit_bank")

    def assign_deposit_bank(self, deposit_holder, deposit_bank):
        deposit_holder.deposit_bank = deposit_bank
        self.graph.add_edge(deposit_holder, deposit_bank)

    def pay_deposit_interest(self, deposit_bank):
        deposit_rate = deposit_bank.deposit_rate
        for _, holder in self.graph.edges(deposit_bank):
            interest = holder.deposits * deposit_rate
            holder.increase_stock("deposits", interest)
            holder.increase_flow("deposit_interest", interest)
            deposit_bank.increase_stock("deposits", interest)
            deposit_bank.increase_flow("deposit_interest", interest)


class BondMarket(EcoSpace):
    pass


class EquitySpace(EcoSpace):

    def add_equity_issuer(self, agent):
        return self.add_role(EquityIssuerRole, agent, "equity_issuer")

    def add_equity_holder(self, household):
        return self.add_role(EquityHolderRole, household, "equity_holder")

    def distribute_dividends(self, issuer, amount):
        issuer.increase_flow("dividends", amount)
        issuer.decrease_stock("cash", amount)
        for _, holder, data in self.graph.edges(issuer, data=True):
            dividend = amount * data["share"]
            holder.increase_flow("dividends", dividend)
            holder.increase_stock("cash", dividend)

    def update_equity_holdings(self, issuer):
        new_equity = issuer.net_worth
        for _, holder, data in self.graph.edges(issuer, data=True):
            value = new_equity * data["share"]
            holder.clear_stock("equity")
            holder.increase_stock("equity", value)
