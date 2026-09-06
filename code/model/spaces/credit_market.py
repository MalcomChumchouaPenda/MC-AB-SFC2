from agentpy import AgentDList
from model.base import EcoSpace
from model.roles.lender import Lender
from model.roles.borrower import Borrower


class CreditMarket(EcoSpace):

    def setup(self):
        super().setup()
        self.monetary_union = None
        self.lenders = AgentDList(self.model)
        self.borrowers = AgentDList(self.model)

    @property
    def discount_rate(self):
        return self.monetary_union.discount_rate

    #
    # Roles management
    #
    def add_borrower(self, agent):
        role = self.add_role(Borrower, agent, "borrower")
        self.borrowers.append(role)
        return role

    def add_lender(self, agent):
        role = self.add_role(Lender, agent, "lender")
        self.lenders.append(role)
        return role

    #
    # Loan matching
    #
    def find_lenders(self):
        return list(self.lenders)

    def grant_loan(self, lender, borrower, amount, rate):
        borrower.loan_demand -= amount
        borrower.debit_stock("loans", amount)
        borrower.credit_stock("deposits", amount)
        borrower.bank_account.debit_stock("deposits", amount)
        borrower.bank_account.credit_stock("cash", amount)
        lender.debit_stock("cash", amount)
        lender.credit_stock("loans", amount)
        self.graph.add_edge(borrower, lender, amount=amount, rate=rate)

    #
    # Loan repayment
    #
    def find_loans(self, borrower):
        return [
            dict(lender=lender, **data)
            for _, lender, data in self.graph.edges(borrower, data=True)
        ]

    def repay_loan(self, borrower, lender, principal, interests):
        total = principal + interests
        borrower.credit_stock("loans", principal)
        borrower.debit_flow("loan_interests", interests)
        borrower.debit_stock("deposits", total)
        borrower.bank_account.credit_stock("deposits", total)
        borrower.bank_account.debit_stock("cash", total)
        lender.credit_stock("cash", total)
        lender.debit_stock("loans", principal)
        lender.credit_flow("loans_interests", interests)
        self.graph[borrower][lender]["amount"] -= principal

    #
    # Cash advances
    #
    def request_advances(self, lender, amount):
        lender.debit_stock("advances", amount)
        lender.credit_stock("cash", amount)
        lender.cb_account.credit_stock("advances", amount)
        lender.cb_account.debit_stock("cash", amount)

    def repay_advances(self, lender, principal, interests):
        total = principal + interests
        lender.debit_stock("cash", total)
        lender.credit_stock("advances", principal)
        lender.debit_flow("adv_interests", interests)
        lender.cb_account.credit_stock("cash", total)
        lender.cb_account.debit_stock("advances", principal)
        lender.cb_account.credit_flow("adv_interests", interests)
