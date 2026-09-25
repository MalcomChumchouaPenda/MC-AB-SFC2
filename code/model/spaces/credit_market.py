from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.lender import Lender
from model.roles.borrower import Borrower


class CreditMarket(EcoSpace):

    @property
    def discount_rate(self):
        return self.env.discount_rate

    #
    # Roles management
    #
    def add_borrower(self, agent):
        return self.add_role(Borrower, agent, "borrower")

    def add_lender(self, agent):
        return self.add_role(Lender, agent, "lender")

    #
    # Loan matching
    #

    def grant_loan(self, lender, borrower, amount, rate):
        borrower.loan_demand -= amount
        self.transfer_stock("loans", borrower.id, lender.id, amount)
        self.transfer_stock("deposits", borrower.bank_id, borrower.id, amount)
        self.transfer_stock("cash", lender.id, borrower.bank_id, amount)
        self.graph.add_edge(borrower, lender, amount=amount, rate=rate)

    #
    # Loan repayment
    #
    def repay_loans(self, borrower, lender, principal, interests):
        total = principal + interests
        self.transfer_stock("loans", lender.id, borrower.id, principal)
        self.transfer_stock("cash", borrower.bank_id, lender.id, total)
        self.transfer_stock("deposits", borrower.id, borrower.bank_id, total)
        self.record_flow("loan_interests", borrower.id, lender.id, interests)
        self.graph[borrower][lender]["amount"] -= principal

    def make_defaults(self, borrower, lender, amount):
        self.transfer_stock("loans", lender.id, borrower.id, amount)
        self.record_flow("loan_defaults", lender.id, borrower.id, amount)
        self.graph[borrower][lender]["amount"] -= amount

    #
    # Cash advances
    #
    def request_advances(self, lender, amount):
        self.transfer_stock("cash", lender.cb_id, lender.id, amount)
        self.transfer_stock("advances", lender.id, lender.cb_id, amount)

    def repay_advances(self, lender, principal, interests):
        total = principal + interests
        self.transfer_stock("cash", lender.id, lender.cb_id, total)
        self.transfer_stock("advances", lender.cb_id, lender.id, principal)
        self.record_flow("adv_interests", lender.id, lender.cb_id, interests)
