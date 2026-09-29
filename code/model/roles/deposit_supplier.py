from model.base import EcoRole


class DepositSupplier(EcoRole):

    #
    # Perceptions
    #
    def find_deposit_demanders(self):
        return self.env.find_all_roles("deposit_demander")

    def get_deposit_rate(self):
        return self.deposit_demander.deposit_rate

    #
    # Actions
    #
    def make_deposits(self, amount):
        self.env.make_deposits(self, amount)

    def withdraw_deposits(self, amount):
        self.env.withdraw_deposits(self, amount)

    def choose_bank(self, deposit_demander, amount=0):
        if self.deposit_demander is not None:
            self.env.leave_bank(self)
        self.env.join_bank(self, deposit_demander, amount)
