from model.extensions import EcoRole


class Consumer(EcoRole):

    def __init__(self, agent, env, prefix=""):
        super().__init__(agent, env, prefix=prefix)
        self.preference = None

    #
    # perception
    #
    def find_suppliers(self, psi):
        return self.env.find_random_roles("producer", psi)

    def get_average_price(self):
        return self.env.average_price

    #
    # actions
    #
    def buy_goods(self, supplier, quantity):
        self.env.buy_goods(self, supplier, quantity)
