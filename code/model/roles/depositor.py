from model.base import EcoRole


class Depositor(EcoRole):

    #
    # Perceptions
    #
    def find_deposit_banks(self):
        return self.env.find_all_roles("deposit_bank")

    def get_deposit_rate(self):
        return self.deposit_bank.deposit_rate

    #
    # Actions
    #
    def make_deposits(self, amount):
        self.env.make_deposits(self, amount)

    def withdraw_deposits(self, amount):
        self.env.withdraw_deposits(self, amount)

    def choose_bank(self, deposit_bank, amount=0):
        if self.deposit_bank is not None:
            self.env.leave_deposit_bank(self)
        self.env.join_deposit_bank(self, deposit_bank, amount)
