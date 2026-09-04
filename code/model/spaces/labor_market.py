from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.employer import Employer
from model.roles.worker import Worker


class LaborMarket(EcoSpace):

    def setup(self):
        self.average_wage = 0
        self.unemployment = 0
        self.employers = AgentDList(self.model)
        self.workers = AgentDList(self.model)

    def add_employer(self, firm):
        role = self.add_role(Employer, firm, "employer")
        self.employers.append(role)
        return role

    def add_worker(self, household):
        role = self.add_role(Worker, household, "worker")
        self.workers.append(role)
        return role

    def hire_worker(self, worker, employer, quantity):
        wage = employer.wage
        worker.labor_supply -= quantity
        employer.labor_demand -= quantity
        self.graph.add_edge(worker, employer, wage=wage, quantity=quantity)

    def update_state(self):
        self._update_average_wage()
        self._update_unemployment()

    def _update_average_wage(self):
        employers = self.employers
        self.average_wage = sum(employers.wage) / max(1, len(employers))

    def _update_unemployment(self):
        workers = self.workers
        unemployed = workers.select(workers.labor_supply == 1.0)
        self.unemployment = len(unemployed) / max(1, len(workers))
