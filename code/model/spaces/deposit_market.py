from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.deposit_supplier import DepositSupplier
from model.roles.deposit_demander import DepositDemander
from model.roles.deposit_guarantee import DepositGuarantee


class DepositMarket(EcoSpace):

    def add_supplier(self, agent):
        return self.add_role(DepositSupplier, agent, "deposit_supplier")

    def add_demander(self, bank):
        return self.add_role(DepositDemander, bank, "deposit_demander")

    def add_guarantee(self, agent):
        return self.add_role(DepositGuarantee, agent, "deposit_guarantee")

    def join_bank(self, supplier, demander, amount=0):
        supplier.bank_id = demander.id
        supplier.deposit_demander = demander
        self.transfer_stock("cash", supplier.id, demander.id, amount)
        self.transfer_stock("deposits", demander.id, supplier.id, amount)
        self.graph.add_edge(supplier, demander, amount=amount)

    def leave_bank(self, supplier):
        bank_id = supplier.bank_id
        demander = supplier.deposit_demander
        amount = self.graph[supplier][demander]["amount"]
        supplier.bank_id = None
        supplier.deposit_demander = None
        self.transfer_stock("cash", bank_id, supplier.id, amount)
        self.transfer_stock("deposits", supplier.id, bank_id, amount)
        self.graph.remove_edge(supplier, demander)

    def pay_interests(self, demander, supplier, amount):
        self.transfer_stock("deposits", demander.id, supplier.id, amount)
        self.make_transaction("dep_interests", demander.id, supplier.id, amount)
        self.graph[supplier][demander]["amount"] += amount

    def reimburse_deposits(self, guarantee, supplier, amount):
        bank_id = supplier.deposit_demander.id
        self.transfer_stock("cash", guarantee.id, supplier.id, amount)
        self.transfer_stock("deposits", supplier.id, bank_id, amount)

    def make_deposits(self, supplier, amount):
        bank_id = supplier.deposit_demander.id
        self.transfer_stock("cash", supplier.id, bank_id, amount)
        self.transfer_stock("deposits", bank_id, supplier.id, amount)
        self.graph[supplier][supplier.deposit_demander]["amount"] += amount

    def withdraw_deposits(self, supplier, amount):
        bank_id = supplier.deposit_demander.id
        self.transfer_stock("cash", bank_id, supplier.id, amount)
        self.transfer_stock("deposits", supplier.id, bank_id, amount)
        self.graph[supplier][supplier.deposit_demander]["amount"] -= amount
