from model.base import EcoRole


class DepositGuarantee(EcoRole):

    #
    # Perceptions
    #
    def find_defaulted_banks(self):
        return self.env.find_defaulted_banks()

    def find_deposit_accounts(self, deposit_bank):
        return self.env.find_deposit_accounts(deposit_bank)

    #
    # Actions
    #
    def reimburse_deposits(self, depositor, amount):
        self.env.reimburse_deposits(self, depositor, amount)
