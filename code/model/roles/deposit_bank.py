from model.base import EcoRole


class DepositBank(EcoRole):

    def setup(self):
        super().setup()
        self.defaulted = False
    
    #
    # Perceptions
    #

    def find_deposit_accounts(self, deposit_bank):
        return self.space.find_deposit_accounts(deposit_bank)

    #
    # Actions
    #
    def pay_interests(self, depositor, amount):
        self.space.pay_interests(self, depositor, amount)