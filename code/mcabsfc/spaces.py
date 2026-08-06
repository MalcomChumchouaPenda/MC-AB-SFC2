import agentpy as ap
from networkx import DiGraph
from .base import EcoSpace
from .roles import EmployerRole, WorkerRole, CitizenRole, ConsumerRole, ProducerRole


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
        consumer.decrease_stock("cash", amount)
        consumer.increase_flow("consumption", amount)
        producer.increase_stock("cash", amount)
        producer.increase_flow("sales", amount)
        producer.decrease_stock("inventories", quantity)


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
    pass


class BondMarket(EcoSpace):
    pass


class EquityMarket(EcoSpace):
    pass
