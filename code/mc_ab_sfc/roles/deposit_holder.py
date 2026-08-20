from ..base import EcoRole


class DepositHolderRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.deposit_bank = None

    @property
    def deposits(self):
        return self.agent.deposits

    def get_deposit_rate(self):
        return self.deposit_bank.deposit_rate

    def make_deposits(self, amount):
        if self.deposit_bank is not None:
            self.space.make_deposits(self, self.deposit_bank, amount)
