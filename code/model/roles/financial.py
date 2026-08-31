from ..base import EcoRole


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
