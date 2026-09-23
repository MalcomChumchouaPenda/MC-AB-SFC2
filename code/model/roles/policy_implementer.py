from model.base import EcoRole


class PolicyImplementer(EcoRole):

    def get_discount_rate(self):
        return self.env.policy_maker.discount_rate
