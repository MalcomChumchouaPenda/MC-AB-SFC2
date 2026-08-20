from ..base import EcoSpace
from ..roles import (
    DepositHolderRole,
    DepositBankRole,
    DepositGuaranteeRole,
)


class DepositMarket(EcoSpace):

    def add_deposit_holder(self, agent):
        return self.add_role(DepositHolderRole, agent, "deposit_holder")

    def add_deposit_bank(self, bank):
        return self.add_role(DepositBankRole, bank, "deposit_bank")

    def add_deposit_guarantee(self, bank):
        return self.add_role(DepositGuaranteeRole, bank, "deposit_guarantee")

    def assign_deposit_bank(self, deposit_holder, deposit_bank):
        deposit_holder.deposit_bank = deposit_bank
        self.graph.add_edge(deposit_bank, deposit_holder)

    def pay_deposit_interest(self, deposit_bank):
        deposit_rate = deposit_bank.deposit_rate
        for _, holder in self.graph.edges(deposit_bank):
            interest = holder.deposits * deposit_rate
            holder.increase_stock("deposits", interest)
            holder.increase_flow("deposit_interest", interest)
            deposit_bank.increase_stock("deposits", interest)
            deposit_bank.increase_flow("deposit_interest", interest)

    def get_defaulted_banks(self):
        return [
            n
            for n in self.graph.nodes
            if isinstance(n, DepositBankRole) and n.defaulted
        ]

    def reimburse_deposits(self, guarantee, deposit_bank):
        for _, holder in self.graph.edges(deposit_bank):
            amount = holder.deposits
            holder.increase_stock("cash", amount)
            holder.decrease_stock("deposits", amount)
            guarantee.decrease_stock("reserves", amount)
            deposit_bank.decrease_stock("deposits", amount)

    def make_deposits(self, holder, bank, amount):
        holder.increase_stock("deposits", amount)
        holder.decrease_stock("cash", amount)
        bank.increase_stock("deposits", amount)
        bank.increase_stock("reserves", amount)
