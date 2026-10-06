from model.extensions import EcoSpace
from model.roles.depositor import Depositor
from model.roles.deposit_bank import DepositBank
from model.roles.deposit_guarantee import DepositGuarantee


class DepositMarket(EcoSpace):

    def setup(self):
        super().setup()
        self.country_pos = 0

    @property
    def deposit_rate(self):
        return self.p.zeta * self.env.discount_rate

    #
    # Roles management
    #
    def add_household(self, household):
        self.add_role(Depositor, household, "depositor")

    def add_firm(self, firm):
        c = self.country_pos
        self.add_role(Depositor, firm, f"depositor_{c}")

    def add_bank(self, bank):
        self.add_role(DepositBank, bank, "deposit_bank")

    def add_government(self, govt):
        self.add_role(DepositGuarantee, govt, "deposit_guarantee")

    #
    # Transactions
    #

    def join_deposit_bank(self, depositor, deposit_bank, amount=0):
        self.transfer_stock("cash", depositor.id, deposit_bank.id, amount)
        self.transfer_stock("deposits", deposit_bank.id, depositor.id, amount)
        self.graph.add_edge(depositor, deposit_bank, amount=amount)

    def leave_deposit_bank(self, depositor, deposit_bank):
        amount = self.graph[depositor][deposit_bank]["amount"]
        self.transfer_stock("cash", deposit_bank.id, depositor.id, amount)
        self.transfer_stock("deposits", depositor.id, deposit_bank.id, amount)
        self.graph.remove_edge(depositor, deposit_bank)

    def pay_interests(self, deposit_bank, depositor, amount):
        self.transfer_stock("deposits", deposit_bank.id, depositor.id, amount)
        self.make_transaction("dep_interests", deposit_bank.id, depositor.id, amount)
        self.graph[depositor][deposit_bank]["amount"] += amount

    def reimburse_deposits(self, guarantee, depositor, deposit_bank, amount):
        self.transfer_stock("cash", guarantee.id, depositor.id, amount)
        self.transfer_stock("deposits", depositor.id, deposit_bank.id, amount)
        self.make_transaction("loan_defaults", guarantee.id, deposit_bank.id, amount)
        self.graph.remove_edge(depositor, deposit_bank)

    def make_deposits(self, depositor, deposit_bank, amount):
        self.transfer_stock("cash", depositor.id, deposit_bank.id, amount)
        self.transfer_stock("deposits", deposit_bank.id, depositor.id, amount)
        self.graph[depositor][deposit_bank]["amount"] += amount

    def withdraw_deposits(self, depositor, deposit_bank, amount):
        self.transfer_stock("cash", deposit_bank.id, depositor.id, amount)
        self.transfer_stock("deposits", depositor.id, deposit_bank.id, amount)
        self.graph[depositor][deposit_bank]["amount"] -= amount
