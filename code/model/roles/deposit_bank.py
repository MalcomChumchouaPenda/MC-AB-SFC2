from model.base import EcoRole


class DepositBank(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.defaulted = False

    #
    # Perceptions
    #

    def find_deposit_accounts(self):
        return self.env.find_deposit_accounts(self)

    #
    # Actions
    #
    def pay_interests(self, depositor, amount):
        self.env.pay_interests(self, depositor, amount)
