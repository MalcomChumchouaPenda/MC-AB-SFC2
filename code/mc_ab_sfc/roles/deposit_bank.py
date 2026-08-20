from ..base import EcoRole


class DepositBankRole(EcoRole):

    @property
    def deposit_rate(self):
        return self.agent.deposit_rate

    @property
    def defaulted(self):
        return self.agent.defaulted

    @property
    def defaulted_deposits(self):
        if not self.agent.defaulted:
            return 0
        return self.agent.deposits

    def pay_deposit_interest(self):
        self.space.pay_deposit_interest(self)
