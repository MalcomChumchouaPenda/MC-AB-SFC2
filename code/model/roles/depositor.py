from model.extensions import EcoRole


class Depositor(EcoRole):

    #
    # Perceptions
    #
    def find_deposit_banks(self):
        return self.env.find_all_roles("deposit_bank")

    def get_deposit_rate(self):
        return self.env.deposit_rate

    #
    # Actions
    #
    def make_deposits(self, bank_id, amount):
        deposit_bank = self.env.roles[bank_id]
        self.env.make_deposits(self, deposit_bank, amount)

    def withdraw_deposits(self, bank_id, amount):
        deposit_bank = self.env.roles[bank_id]
        self.env.withdraw_deposits(self, deposit_bank, amount)

    def leave_deposit_bank(self, bank_id):
        deposit_bank = self.env.roles[bank_id]
        self.env.leave_deposit_bank(self, deposit_bank)

    def join_deposit_bank(self, bank_id):
        deposit_bank = self.env.roles[bank_id]
        self.env.join_deposit_bank(self, deposit_bank, 0)
