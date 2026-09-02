from agentpy.objects import Object
from networkx import Graph
from model.base import EcoSpace, EcoRole


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


class LenderRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.loan_applicants = []

    def receive_request(self, applicant):
        self.loan_applicants.append(applicant)

    def grant_loan(self, borrower, amount, rate):
        self.space.grant_loan(self, borrower, amount, rate)


class BorrowerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.loan_demand = 0

    @property
    def target_leverage(self):
        agent = self.agent
        return agent.desired_loans / agent.equity

    def search_lenders(self):
        return self.space.search_lenders()

    def request_loan(self, lender):
        lender.receive_request(self)
