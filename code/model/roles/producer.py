from model.base import EcoRole


class Producer(EcoRole):

    def setup(self):
        super().setup()
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
        return self.space.average_price

    def get_average_productivity(self):
        return self.space.average_prod

    # Actions
    def produce_goods(self, labor):
        self.inventories += self.productivity * labor
