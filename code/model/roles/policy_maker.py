from model.base import EcoRole


class PolicyMaker(EcoRole):

    #
    # perceptions
    #
    def get_discount_rate(self):
        return self.env.discount_rate

    def get_average_inflation(self):
        return self.env.average_inflation

    #
    # actions
    #
    def set_discount_rate(self, rate):
        self.env.discount_rate = rate
