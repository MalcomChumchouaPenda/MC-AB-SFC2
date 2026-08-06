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

    @property
    def demand(self):
        if self.space.tradable:
            return self.owner.desired_trad_cons
        return self.owner.desired_non_trad_cons

    def search_suppliers(self, psi):
        return self.space.search_suppliers(psi)

    def get_average_price(self):
        return self.space.average_price

    def buy_goods(self, suppliers):
        cash = self.owner.cash
        demand = self.demand
        market = self.space
        for supplier in suppliers:
            price = supplier.get_price()
            available = supplier.get_available_quantity()
            residual = demand / price
            affordable = cash / price
            quantity = min(residual, available, affordable)
            market.buy_goods(self, supplier, quantity)
            demand -= quantity * price
            cash -= quantity * price
            if demand <= 0 or cash <= 0:
                break


class ProducerRole(EcoRole):

    def get_position(self):
        return self.owner.position

    def get_price(self):
        return self.owner.price

    def get_available_quantity(self):
        return self.owner.inventories
