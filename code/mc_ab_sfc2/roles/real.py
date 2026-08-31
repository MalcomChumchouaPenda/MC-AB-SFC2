from ..base import EcoRole


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


class ProducerRole(EcoRole):

    @property
    def price(self):
        return self.agent.price

    @property
    def productivity(self):
        return self.agent.productivity

    @property
    def position(self):
        return self.agent.position

    @property
    def available_quantity(self):
        return self.agent.inventories

    def get_average_price(self):
        return self.space.average_price

    def get_average_productivity(self):
        return self.space.average_productivity


class ConsumerRole(EcoRole):

    @property
    def demand(self):
        if self.space.tradable:
            return self.agent.desired_trad_cons
        return self.agent.desired_non_trad_cons

    def search_suppliers(self, psi):
        return self.space.search_suppliers(psi)

    def get_average_price(self):
        return self.space.average_price

    def buy_goods(self, suppliers):
        cash = self.agent.cash
        demand = self.demand
        market = self.space
        for supplier in suppliers:
            price = supplier.price
            residual = demand / price
            affordable = cash / price
            available = supplier.available_quantity
            quantity = min(residual, available, affordable)
            market.buy_goods(self, supplier, quantity)
            demand -= quantity * price
            cash -= quantity * price
            if demand <= 0 or cash <= 0:
                break
