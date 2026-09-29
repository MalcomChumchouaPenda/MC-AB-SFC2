from model.base import EcoRole


class DepositDemander(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.defaulted = False

    #
    # Perceptions
    #

    def find_deposits(self):
        return self.env.find_links(self, "deposit_supplier")

    #
    # Actions
    #
    def pay_interests(self, deposit_supplier, amount):
        self.env.pay_interests(self, deposit_supplier, amount)
