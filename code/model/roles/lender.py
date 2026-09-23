from model.base import EcoRole


class Lender(EcoRole):

    def __init__(self, agent, env):
        super().__init__(agent, env)
        self.loan_applicants = []

    #
    #   Actions
    #
    def receive_request(self, applicant):
        self.loan_applicants.append(applicant)

    def grant_loan(self, borrower, amount, rate):
        self.env.grant_loan(self, borrower, amount, rate)

    def request_advances(self, amount):
        self.env.request_advances(self, amount)

    def repay_advances(self, principal, interests):
        self.env.repay_advances(self, principal, interests)
