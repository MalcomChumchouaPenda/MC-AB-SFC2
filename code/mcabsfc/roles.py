import agentpy as ap
from .base import EcoRole


class CitizenRole(EcoRole):

    def get_tax_rate(self):
        return self.space.tax_rate


class EmployerRole(EcoRole):
    pass


class WorkerRole(EcoRole):

    def search_employers(self, psi):
        return self.space.search_employers(psi)

    def create_job(self, employer, quantity):
        self.space.create_job(self, employer, quantity)

    def get_labor_sold(self):
        return self.space.get_labor_sold(self)

    def get_unemployment_rate(self):
        return self.space.unemployment_rate


class ConsumerRole(ap.AgentNode):

    def __init__(self, owner, market):
        super().__init__(owner.id)
        self.owner = owner
        self.market = market
