from model.base import EcoRole


class Consumer(EcoRole):

    @property
    def preference(self):
        return self.agent.preference

    #
    # perception
    #
    def find_suppliers(self, psi):
        return self.env.find_suppliers(psi)

    def get_average_price(self):
        return self.env.average_price

    #
    # actions
    #
    def buy_goods(self, supplier, quantity):
        self.env.buy_goods(self, supplier, quantity)

    # def buy_goods(self, suppliers):
    #     cash = self.agent.cash
    #     demand = self.demand
    #     market = self.space
    #     for supplier in suppliers:
    #         price = supplier.price
    #         residual = demand / price
    #         affordable = cash / price
    #         available = supplier.available_quantity
    #         quantity = min(residual, available, affordable)
    #         market.buy_goods(self, supplier, quantity)
    #         demand -= quantity * price
    #         cash -= quantity * price
    #         if demand <= 0 or cash <= 0:
    #             break
