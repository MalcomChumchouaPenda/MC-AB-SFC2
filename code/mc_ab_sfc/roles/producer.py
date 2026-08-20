from ..base import EcoRole


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
