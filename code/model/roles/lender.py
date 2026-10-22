from model.extensions import EcoRole


class Lender(EcoRole):

    def __init__(self, agent, env, prefix=""):
        super().__init__(agent, env, prefix=prefix)
        self.loan_applicants = []
        self.defaulted = False

    #
    #   Actions
    #
    def receive_request(self, applicant):
        self.loan_applicants.append(applicant)

    def grant_loan(self, borrower, amount, rate):
        self.env.grant_loan(self, borrower, amount, rate)
