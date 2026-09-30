from model.base import EcoRole


class DepositBank(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.defaulted = False

    #
    # Perceptions
    #

    def find_deposits(self):
        return self.env.find_links(self, "depositor")

    def find_depositor(self, id):
        return self.env.roles[id]

    #
    # Actions
    #
    def pay_interests(self, depositor, amount):
        self.env.pay_interests(self, depositor, amount)

    def make_deposits(self, depositor, amount):
        self.env.join_deposit_bank(depositor, self, amount)
