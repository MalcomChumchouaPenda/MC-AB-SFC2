from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.depositor import Depositor
from model.roles.deposit_bank import DepositBank
from model.roles.deposit_guarantee import DepositGuarantee


class DepositMarket(EcoSpace):

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

    def join_deposit_bank(self, depositor, deposit_bank, amount=0):
        depositor.bank_id = deposit_bank.id
        depositor.deposit_bank = deposit_bank
        self.transfer_stock("cash", depositor.id, deposit_bank.id, amount)
        self.transfer_stock("deposits", deposit_bank.id, depositor.id, amount)
        self.graph.add_edge(depositor, deposit_bank, amount=amount)

    def leave_deposit_bank(self, depositor):
        bank_id = depositor.bank_id
        deposit_bank = depositor.deposit_bank
        amount = self.graph[depositor][deposit_bank]["amount"]
        depositor.bank_id = None
        depositor.deposit_bank = None
        self.transfer_stock("cash", bank_id, depositor.id, amount)
        self.transfer_stock("deposits", depositor.id, bank_id, amount)
        self.graph.remove_edge(depositor, deposit_bank)

    def pay_interests(self, deposit_bank, depositor, amount):
        self.transfer_stock("deposits", deposit_bank.id, depositor.id, amount)
        self.record_flow("dep_interests", deposit_bank.id, depositor.id, amount)
        self.graph[depositor][deposit_bank]["amount"] += amount

    def reimburse_deposits(self, guarantee, depositor, amount):
        bank_id = depositor.deposit_bank.id
        self.transfer_stock("cash", guarantee.id, depositor.id, amount)
        self.transfer_stock("deposits", depositor.id, bank_id, amount)

    def make_deposits(self, depositor, amount):
        bank_id = depositor.deposit_bank.id
        self.transfer_stock("cash", depositor.id, bank_id, amount)
        self.transfer_stock("deposits", bank_id, depositor.id, amount)
        self.graph[depositor][depositor.deposit_bank]["amount"] += amount

    def withdraw_deposits(self, depositor, amount):
        bank_id = depositor.deposit_bank.id
        self.transfer_stock("cash", bank_id, depositor.id, amount)
        self.transfer_stock("deposits", depositor.id, bank_id, amount)
        self.graph[depositor][depositor.deposit_bank]["amount"] -= amount
