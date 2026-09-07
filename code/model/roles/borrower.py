from model.base import EcoRole


class Borrower(EcoRole):

    def setup(self):
        super().setup()
        self.loan_demand = 0
        self.net_worth = 0

    #
    # Perceptions
    #
    def find_lenders(self):
        return self.space.find_lenders()

    def find_loans(self):
        return self.space.find_loans(self)

    #
    # Actions
    #
    def request_loans(self, lender):
        lender.receive_request(self)

    def repay_loans(self, lender, principal, interests):
        self.space.repay_loans(self, lender, principal, interests)
