from model.base import EcoSpace, EcoRole


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


class EmployerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.labor_demand = 0

    @property
    def wage_offer(self):
        return self.agent.wage_offer


class WorkerRole(EcoRole):

    def search_employers(self, psi):
        return self.space.search_employers(psi)

    def create_job(self, employer, quantity):
        self.space.create_job(self, employer, quantity)

    def get_labor_sold(self):
        return self.space.get_labor_sold(self)

    def get_unemployment_rate(self):
        return self.space.unemployment_rate
