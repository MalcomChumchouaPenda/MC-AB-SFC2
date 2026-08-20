from ..base import EcoRole


class DepositGuaranteeRole(EcoRole):

    def get_defaulted_banks(self):
        return self.space.get_defaulted_banks()

    def reimburse_deposits(self, bank):
        self.space.reimburse_deposits(self, bank)
