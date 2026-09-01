from agentpy.objects import Object
from networkx import Graph
from model.base import EcoSpace
from model.roles.financial import LenderRole, BorrowerRole


class CreditMarket(EcoSpace):

    def add_borrower(self, firm):
        return self.add_role(BorrowerRole, firm, "borrower")

    def add_lender(self, bank):
        return self.add_role(LenderRole, bank, "lender")

    def search_lenders(self):
        return [n for n in self.nodes if isinstance(n, LenderRole)]

    def grant_loan(self, lender, borrower, amount, rate):
        borrower.loan_demand -= amount
        borrower.increase_stock("loans", amount)
        borrower.increase_stock("deposits", amount)
        lender.increase_stock("loans", amount)
        lender.increase_stock("deposits", amount)
        self.graph.add_edge(borrower, lender, amount=amount, rate=rate)
