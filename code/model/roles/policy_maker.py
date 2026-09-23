from model.base import EcoRole


class PolicyMaker(EcoRole):

    @property
    def discount_rate(self):
        return self.agent.discount_rate

    def get_average_inflation(self):
        return self.env.average_inflation
