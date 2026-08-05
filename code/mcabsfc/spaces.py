import agentpy as ap
from networkx import DiGraph
from .base import EcoSpace
from .roles import EmployerRole, WorkerRole, CitizenRole


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
        employers = [node for node in self.nodes if isinstance(node, EmployerRole)]
        return self.model.random.sample(employers, k=psi)

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
