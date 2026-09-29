from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.depositor import DepositSupplier
from model.roles.deposit_bank import DepositDemander
from model.roles.deposit_guarantee import DepositGuarantee


class DepositMarket(EcoSpace):

    def add_depositor(self, agent):
        return self.add_role(DepositSupplier, agent, "depositor")

    def add_deposit_bank(self, bank):
        return self.add_role(DepositDemander, bank, "deposit_bank")

    def add_guarantee(self, agent):
        return self.add_role(DepositGuarantee, agent, "deposit_guarantee")

    def join_deposit_bank(self, supplier, deposit_bank, amount=0):
        supplier.bank_id = deposit_bank.id
        supplier.deposit_bank = deposit_bank
        self.transfer_stock("cash", supplier.id, deposit_bank.id, amount)
        self.transfer_stock("deposits", deposit_bank.id, supplier.id, amount)
        self.graph.add_edge(supplier, deposit_bank, amount=amount)

    def leave_deposit_bank(self, supplier):
        bank_id = supplier.bank_id
        deposit_bank = supplier.deposit_bank
        amount = self.graph[supplier][deposit_bank]["amount"]
        supplier.bank_id = None
        supplier.deposit_bank = None
        self.transfer_stock("cash", bank_id, supplier.id, amount)
        self.transfer_stock("deposits", supplier.id, bank_id, amount)
        self.graph.remove_edge(supplier, deposit_bank)

    def pay_interests(self, deposit_bank, supplier, amount):
        self.transfer_stock("deposits", deposit_bank.id, supplier.id, amount)
        self.make_transaction("dep_interests", deposit_bank.id, supplier.id, amount)
        self.graph[supplier][deposit_bank]["amount"] += amount

    def reimburse_deposits(self, guarantee, supplier, amount):
        bank_id = supplier.deposit_bank.id
        self.transfer_stock("cash", guarantee.id, supplier.id, amount)
        self.transfer_stock("deposits", supplier.id, bank_id, amount)

    def make_deposits(self, supplier, amount):
        bank_id = supplier.deposit_bank.id
        self.transfer_stock("cash", supplier.id, bank_id, amount)
        self.transfer_stock("deposits", bank_id, supplier.id, amount)
        self.graph[supplier][supplier.deposit_bank]["amount"] += amount

    def withdraw_deposits(self, supplier, amount):
        bank_id = supplier.deposit_bank.id
        self.transfer_stock("cash", bank_id, supplier.id, amount)
        self.transfer_stock("deposits", supplier.id, bank_id, amount)
        self.graph[supplier][supplier.deposit_bank]["amount"] -= amount
