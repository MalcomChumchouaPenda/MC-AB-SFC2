import math
from model.base import EcoAgent


class Bank(EcoAgent):

    def setup(self):
        super().setup()
        # choices
        self.deposit_rate = 0
        self.taxes_payable = 0
        self.dividends_payable = 0

        # indicators
        self.profit = 0
        self.net_worth = 0
        self.credit_capacity = 0
        self.defaulted = False

        # accointances
        self.central_bank = None

    def update_deposit_rate(self):
        discount_rate = self.roles["company"].get_discount_rate()
        self.deposit_rate = self.p.zeta * discount_rate

    def pay_deposit_interests(self):
        role = self.roles["deposit_bank"]
        for deposit in role.find_deposits():
            amount = self.deposit_rate * deposit["amount"]
            role.pay_interests(deposit["depositor"], amount)

    def grant_loans(self):
        role = self.roles["lender"]
        applicants = self._list_applicants()
        capacity = self.calc_credit_capacity()
        choice = self.model.nprandom.choice
        for borrower in applicants:
            if capacity <= 0:
                break
            amount = min(capacity, borrower.loan_demand)
            prob = self.calc_loan_probability(borrower)
            rate = self.calc_loan_rate(borrower)
            if choice([0, 1], p=[1 - prob, prob]):
                self._fund_applicant(borrower, amount, rate)
                capacity -= amount
        role.loan_applicants = []

    def _list_applicants(self):
        applicants = self.roles["lender"].loan_applicants
        self.model.random.shuffle(applicants)
        return applicants

    def _fund_applicant(self, borrower, amount, rate):
        deposit_bank = self.roles["deposit_bank"]
        lender = self.roles["lender"]
        lender.grant_loan(borrower, amount, rate)
        depositor = deposit_bank.find_depositor(borrower.id)
        deposit_bank.make_deposits(depositor, amount)

    def calc_credit_capacity(self):
        equity = self.account["equities"]
        return equity * self.p.mu1

    def calc_loan_probability(self, borrower):
        leverage = borrower.loan_demand / borrower.net_worth
        return math.exp(-self.p.iota_l * leverage)

    def calc_loan_rate(self, borrower):
        discount_rate = self.roles["company"].get_discount_rate()
        leverage = borrower.loan_demand / borrower.net_worth
        return self.p.chi * leverage + discount_rate

    #
    # Cash advances
    #
    def request_cash_advances(self):
        account = self.account
        required = self.p.mu2 * account["deposits"]
        shortage = max(required - account["cash"], 0)
        if shortage > 0:
            role = self.roles["lender"]
            role.request_advances(shortage)

    def repay_cash_advances(self):
        discount_rate = self.roles["company"].get_discount_rate()
        principal = abs(self.account["advances"])
        if principal > 0:
            interests = discount_rate * principal
            role = self.roles["lender"]
            role.repay_advances(principal, interests)

    def buy_bonds(self):
        role = self.roles["bond_buyer"]
        bond_issuers = self.find_bond_issuers()
        excess = self.calc_excess_reserves()
        print(excess, bond_issuers)
        choice = self.model.nprandom.choice
        for issuer in bond_issuers:
            prob = self.calc_bond_purchases_probability(issuer)
            if choice([0, 1], p=[1 - prob, prob]):
                bond_value = issuer.bond_value
                purchase = min(excess / bond_value, issuer.bond_number)
                role.buy_bonds(issuer, purchase)
                excess -= purchase * bond_value
                if excess <= 0:
                    break

    def find_bond_issuers(self):
        role = self.roles["bond_buyer"]
        bond_issuers = role.find_issuers()
        random = self.model.random
        random.shuffle(bond_issuers)
        return bond_issuers

    def calc_excess_reserves(self):
        account = self.account
        required = self.p.mu2 * account["deposits"]
        return max(account["cash"] - required, 0)

    def calc_bond_purchases_probability(self, issuer):
        return math.exp(-self.p.iota_b * issuer.debt_ratio)

    #
    # Net worth and stats updates
    # Taxes and dividends payment
    #
    def compute_profit_distribution(self):
        self.profit = self.calc_profit()
        self.taxes_payable = self.calc_taxes()
        self.dividends_payable = self.calc_dividends()

    def calc_profit(self):
        account = self.account
        return (
            account["loan_interests"]
            + account["bond_interests"]
            + account["cash_interests"]
            - account["loan_defaults"]
            - account["dep_interests"]
            - account["adv_interests"]
        )

    def calc_taxes(self):
        if self.profit <= 0:
            return 0
        tax_rate = self.roles["company"].get_tax_rate()
        return tax_rate * self.profit

    def calc_dividends(self):
        if self.profit <= 0:
            return 0
        return self.p.rho * (self.profit - self.taxes_payable)

    def update_net_worth(self):
        account = self.account
        self.net_worth += self.profit - self.taxes_payable - self.dividends_payable
        self.update_equity_shares(self.net_worth + account["equities"])
        return self.net_worth

    def update_equity_shares(self, total_variation):
        role = self.roles["company"]
        shares = role.get_equity_shares()
        total_shares = sum(share["value"] for share in shares)
        for share in shares:
            variation = share["value"] * total_variation / total_shares
            role.update_equity_share(share["founder"], variation)

    def pay_taxes(self):
        if self.taxes_payable > 0:
            taxes = self.taxes_payable
            role = self.roles["company"]
            role.pay_taxes(taxes)
            self.taxes_payable = 0

    def pay_dividends(self):
        if self.dividends_payable > 0:
            role = self.roles["company"]
            shares = role.get_equity_shares()
            total_dividend = self.dividends_payable
            total_shares = sum(share["value"] for share in shares)
            for share in shares:
                dividend = share["value"] * total_dividend / total_shares
                role.pay_dividends(share["founder"], dividend)
            self.dividends_payable = 0

    def exit(self):
        role = self.roles["company"]
        average_wage = role.get_average_wage()
        if self.net_worth < average_wage:
            role.close_bank(self)
