from ..base import EcoRole


class LenderRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.loan_applicants = []

    def receive_request(self, applicant):
        self.loan_applicants.append(applicant)

    def grant_loan(self, borrower, amount, rate):
        self.space.grant_loan(self, borrower, amount, rate)
