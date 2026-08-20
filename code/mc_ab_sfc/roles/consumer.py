from ..base import EcoRole


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
