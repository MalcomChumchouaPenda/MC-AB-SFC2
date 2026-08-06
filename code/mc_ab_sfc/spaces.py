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
    EquityEntityRole,
    DepositorRole,
    DepositEntityRole,
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
        citizen = CitizenRole(household, self)
        household.roles["citizen"] = citizen
        self.graph.add_node(citizen)
        return citizen


class GoodsMarket(EcoSpace):

    def __init__(self, model, tradable=True, **kwargs):
        super().__init__(model, graph=None, **kwargs)
        self.tradable = tradable

    def add_producer(self, firm):
        producer = ProducerRole(firm, self)
        firm.roles["producer"] = producer
        self.graph.add_node(producer)
        return producer

    def add_consumer(self, household):
        consumer = ConsumerRole(household, self)
        role_id = "consumer_tradable" if self.tradable else "consumer_non_tradable"
        household.roles[role_id] = consumer
        self.graph.add_node(consumer)
        return consumer

    def search_suppliers(self, psi):
        suppliers = [node for node in self.nodes if isinstance(node, ProducerRole)]
        return self.model.random.sample(suppliers, k=min(psi, len(suppliers)))

    def buy_goods(self, consumer, producer, quantity):
        price = producer.get_price()
        amount = quantity * price
        producer.increase_stock("cash", amount)
        producer.increase_flow("sales", amount)
        producer.decrease_stock("inventories", quantity)
        consumer.decrease_stock("cash", amount)
        if self.tradable:
            consumer.increase_flow("tradable_cons", amount)
        else:
            consumer.increase_flow("non_tradable_cons", amount)


class LaborMarket(EcoSpace):

    def __init__(self, model, **kwargs):
        super().__init__(model, graph=DiGraph(), **kwargs)

    def add_employer(self, firm):
        employer = EmployerRole(firm, self)
        firm.roles["employer"] = employer
        self.graph.add_node(employer)
        return employer

    def add_worker(self, household):
        worker = WorkerRole(household, self)
        household.roles["worker"] = worker
        self.graph.add_node(worker)
        return worker

    def create_job(self, worker, employer, quantity):
        self.graph.add_edge(worker, employer, wage=employer.wage, quantity=quantity)

    def search_employers(self, psi):
        employers = [n for n in self.nodes if isinstance(n, EmployerRole)]
        return self.model.random.sample(employers, k=min(psi, len(employers)))

    def get_labor_sold(self, worker):
        return sum(
            contract["quantity"]
            for (w, e), contract in self.graph.edges.items()
            if w == worker
        )


class CreditMarket(EcoSpace):
    pass


class DepositMarket(EcoSpace):

    def __init__(self, model, **kwargs):
        super().__init__(model, graph=DiGraph(), **kwargs)

    def add_depositor(self, household):
        role = DepositorRole(household, self)
        household.roles["depositor"] = role
        self.graph.add_node(role)
        return role

    def add_bank(self, bank):
        role = DepositEntityRole(bank, self)
        bank.roles["deposit_entity"] = role
        self.graph.add_node(role)
        return role

    def assign_bank(self, client, bank_role):
        client.bank = bank_role
        self.graph.add_edge(client, bank_role)


class BondMarket(EcoSpace):
    pass


class EquitySpace(EcoSpace):

    def add_equity_entity(self, agent):
        equity_entity = EquityEntityRole(agent, self)
        agent.roles["equity_entity"] = equity_entity
        self.graph.add_node(equity_entity)
        return equity_entity

    def add_equity_holder(self, household):
        equity_holder = EquityHolderRole(household, self)
        household.roles["equity_holder"] = equity_holder
        self.graph.add_node(equity_holder)
        return equity_holder
