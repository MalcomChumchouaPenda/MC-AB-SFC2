from model.base import EcoRole


class Lender(EcoRole):

    def setup(self):
        super().setup()
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
