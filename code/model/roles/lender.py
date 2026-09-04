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
        self.space.grant_loan(self, borrower, amount, rate)

    def request_advances(self, amount):
        self.space.request_advances(self, amount)

    def repay_advances(self, principal, interests):
        self.space.repay_advances(self, principal, interests)
