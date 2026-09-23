from model.base import EcoRole


class Producer(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.price = 0
        self.productivity = 0
        self.inventories = 0

    @property
    def variety(self):
        return self.agent.variety

    #
    # Perceptions
    #
    def get_average_price(self):
        return self.env.average_price

    def get_average_productivity(self):
        return self.env.average_prod

    # Actions
    def produce_goods(self, labor):
        self.inventories += self.productivity * labor
