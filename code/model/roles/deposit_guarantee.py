from model.base import EcoRole


class DepositGuarantee(EcoRole):

    #
    # Perceptions
    #
    def find_defaults(self):
        return self.env.find_defaults()

    def find_deposits(self, deposit_bank):
        return self.env.find_deposits(deposit_bank)

    #
    # Actions
    #
    def reimburse_deposits(self, depositor, amount):
        self.env.reimburse_deposits(self, depositor, amount)
