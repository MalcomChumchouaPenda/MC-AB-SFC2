from model.extensions import EcoSpace
from model.roles.lender import Lender
from model.roles.borrower import Borrower


class CreditMarket(EcoSpace):

    def setup(self):
        super().setup()

    @property
    def discount_rate(self):
        return self.env.discount_rate

    #
    # Roles management
    #
    def add_firm(self, firm):
        self.add_role(Borrower, firm)

    def add_bank(self, bank):
        self.add_role(Lender, bank)

    #
    # Loan matching
    #

    def grant_loan(self, lender, borrower, amount, rate):
        borrower.loan_demand -= amount
        self.transfer_stock("loans", borrower.id, lender.id, amount)
        self.transfer_stock("cash", lender.id, borrower.id, amount)
        self.graph.add_edge(borrower, lender, amount=amount, rate=rate)

    #
    # Loan repayment
    #
    def repay_loans(self, borrower, lender, principal, interests):
        total = principal + interests
        self.transfer_stock("loans", lender.id, borrower.id, principal)
        self.transfer_stock("cash", borrower.id, lender.id, total)
        self.make_transaction("loan_interests", borrower.id, lender.id, interests)
        self.graph[borrower][lender]["amount"] -= principal

    def make_defaults(self, borrower, lender, amount):
        self.transfer_stock("loans", lender.id, borrower.id, amount)
        self.make_transaction("loan_defaults", lender.id, borrower.id, amount)
        self.graph[borrower][lender]["amount"] -= amount
