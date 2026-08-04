import agentpy as ap
from networkx import DiGraph
from .roles import EmployerRole, WorkerRole


class LaborMarket(ap.Network):

    def __init__(self, model, **kwargs):
        super().__init__(model, graph=DiGraph(), **kwargs)

    def add_worker(self, household):
        worker = WorkerRole(household, self)
        household.roles["worker"] = worker
        self.graph.add_node(worker)
        return worker

    def create_job(self, worker, employer, quantity):
        print('create', worker, employer)
        self.graph.add_edge(worker, employer, wage=employer.wage, quantity=quantity)

    def find_employers(self, search_size=1):
        employers = [node for node in self.nodes if isinstance(node, EmployerRole)]
        return self.model.random.sample(employers, k=search_size)

    def labor_sold(self, worker):
        return sum(
            contract["quantity"]
            for (w, e), contract in self.graph.edges.items()
            if w == worker
        )


class GoodsMarket(ap.Network):
    pass
