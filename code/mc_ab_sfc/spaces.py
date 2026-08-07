import agentpy as ap
from networkx import DiGraph
from .base import EcoSpace
from .roles import (
    EmployerRole,
    WorkerRole,
    CitizenRole,
    ConsumerRole,
    ProducerRole,
    EquityHolderRole,
    EquityIssuerRole,
    DepositHolderRole,
    DepositBankRole,
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

    def add_citizen(self, household):
        return self.add_role(CitizenRole, household, "citizen")


class GoodsMarket(EcoSpace):

    def __init__(self, model, tradable=True, **kwargs):
        super().__init__(model, **kwargs)
        self.tradable = tradable

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

    def calc_average_productivity(self):
        nodes = self.graph.nodes  # roles
        values = [n.productivity for n in nodes if isinstance(n, ProducerRole)]
        return sum(values) / max(1, len(values))


class LaborMarket(EcoSpace):

    def add_employer(self, firm):
        return self.add_role(EmployerRole, firm, "employer")

    def add_worker(self, household):
        return self.add_role(WorkerRole, household, "worker")

    def create_job(self, worker, employer, quantity):
        self.graph.add_edge(worker, employer, wage=employer.wage, quantity=quantity)

    def search_employers(self, psi):
        employers = [n for n in self.nodes if isinstance(n, EmployerRole)]
        return self.model.random.sample(employers, k=min(psi, len(employers)))

    def get_labor_sold(self, worker):
        edges = self.graph.edges  # contracts
        return sum(data["quantity"] for (w, e), data in edges.items() if w == worker)


class CreditMarket(EcoSpace):
    pass


class DepositMarket(EcoSpace):

    def add_client(self, household):
        return self.add_role(DepositHolderRole, household, "deposit_holder")

    def add_deposit_bank(self, bank):
        return self.add_role(DepositBankRole, bank, "deposit_bank")

    def assign_deposit_bank(self, deposit_holder, deposit_bank):
        deposit_holder.deposit_bank = deposit_bank
        self.graph.add_edge(deposit_holder, deposit_bank)


class BondMarket(EcoSpace):
    pass


class EquitySpace(EcoSpace):

    def add_equity_issuer(self, agent):
        return self.add_role(EquityIssuerRole, agent, "equity_issuer")

    def add_equity_holder(self, household):
        return self.add_role(EquityHolderRole, household, "equity_holder")
