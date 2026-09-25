from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.employer import Employer
from model.roles.worker import Worker


class LaborMarket(EcoSpace):

    def setup(self):
        super().setup()
        self.average_wage = 0
        self.unemployment = 0

    def add_employer(self, firm):
        return self.add_role(Employer, firm, "employer")

    def add_worker(self, household):
        return self.add_role(Worker, household, "worker")

    #
    # labor matching
    #
    def hire_worker(self, worker, employer, quantity):
        wage = employer.wage
        worker.labor_supply -= quantity
        employer.labor_demand -= quantity
        self.graph.add_edge(worker, employer, wage=wage, quantity=quantity)

    #
    # wages payment
    #

    #
    # evolution
    #
    def update_state(self):
        self._update_average_wage()
        self._update_unemployment()

    def _update_average_wage(self):
        employers = self.roles["employer"]
        self.average_wage = sum(employers.wage) / max(1, len(employers))

    def _update_unemployment(self):
        workers = self.roles["worker"]
        unemployed = workers.select(workers.labor_supply == 1.0)
        self.unemployment = len(unemployed) / max(1, len(workers))
