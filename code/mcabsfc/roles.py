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


class ConsumerRole(EcoRole):

    def search_suppliers(self, psi):
        return self.space.search_suppliers(psi)

    def get_average_price(self):
        return self.space.avg_price


class ProducerRole:
    pass

