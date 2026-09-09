from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.depositor import Depositor
from model.roles.deposit_bank import DepositBank
from model.roles.deposit_guarantee import DepositGuarantee


class DepositMarket(EcoSpace):

    def setup(self):
        super().setup()
        self.deposit_banks = AgentDList(self.model)
        self.depositors = AgentDList(self.model)
        self.deposit_guarantee = None

    def add_depositor(self, agent):
        role = self.add_role(Depositor, agent, "depositor")
        self.depositors.append(role)
        return role

    def add_deposit_bank(self, bank):
        role = self.add_role(DepositBank, bank, "deposit_bank")
        self.deposit_banks.append(role)
        return role

    def add_deposit_guarantee(self, agent):
        role = self.add_role(DepositGuarantee, agent, "deposit_guarantee")
        self.deposit_guarantee = role
        return role

    def find_deposit_accounts(self, bank):
        return [
            dict(depositor=depositor, **data)
            for _, depositor, data in self.graph.edges(bank, data=True)
        ]

    def find_deposit_banks(self):
        return list(self.deposit_banks)

    def find_defaulted_banks(self):
        banks = self.deposit_banks
        return banks.select(banks.defaulted == True)

    def link_depositor_to_bank(self, depositor, deposit_bank, amount=0):
        depositor.account.credit_stock("deposits", amount)
        depositor.account.debit_stock("cash", amount)
        deposit_bank.account.debit_stock("deposits", amount)
        deposit_bank.account.credit_stock("cash", amount)
        depositor.bank_account = deposit_bank.account
        depositor.deposit_bank = deposit_bank
        self.graph.add_edge(depositor, deposit_bank, amount=amount)

    def unlink_depositor_with_bank(self, depositor):
        deposit_bank = depositor.deposit_bank
        amount = self.graph[depositor][deposit_bank]["amount"]
        depositor.account.debit_stock("deposits", amount)
        depositor.account.credit_stock("cash", amount)
        depositor.bank_account.credit_stock("deposits", amount)
        depositor.bank_account.debit_stock("cash", amount)
        depositor.bank_account = None
        depositor.deposit_bank = None
        self.graph.remove_edge(depositor, deposit_bank)

    def pay_interests(self, deposit_bank, depositor, amount):
        depositor.account.credit_stock("deposits", amount)
        depositor.account.credit_flow("dep_interests", amount)
        deposit_bank.debit_stock("deposits", amount)
        deposit_bank.debit_flow("dep_interests", amount)
        self.graph[depositor][deposit_bank]["amount"] += amount

    def reimburse_deposits(self, guarantee, depositor, amount):
        depositor.account.debit_stock("deposits", amount)
        depositor.account.credit_stock("cash", amount)
        depositor.deposit_bank.credit_stock("deposits", amount)
        guarantee.account.debit_stock("cash", amount)

    def make_deposits(self, depositor, amount):
        depositor.account.credit_stock("deposits", amount)
        depositor.account.debit_stock("cash", amount)
        depositor.deposit_bank.debit_stock("deposits", amount)
        depositor.deposit_bank.credit_stock("cash", amount)
        self.graph[depositor][depositor.deposit_bank]["amount"] += amount

    def withdraw_deposits(self, depositor, amount):
        depositor.account.debit_stock("deposits", amount)
        depositor.account.credit_stock("cash", amount)
        depositor.deposit_bank.credit_stock("deposits", amount)
        depositor.deposit_bank.debit_stock("cash", amount)
        self.graph[depositor][depositor.deposit_bank]["amount"] -= amount
