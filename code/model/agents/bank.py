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
        self.country = None

        # accointances
        self.central_bank = None

    def update_deposit_rate(self):
        cb = self.central_bank
        self.deposit_rate = self.p.zeta * cb.discount_rate

    def pay_deposit_interests(self):
        for market in self.model.deposit_markets.values():
            for deposit in market.get_bank_deposits(self):
                amount = self.deposit_rate * deposit["amount"]
                market.pay_interests(deposit["client"], self, amount)

    def grant_loans(self):
        role = self.roles["lender"]
        applicants = role.loan_applicants
        random = self.model.random
        random.shuffle(applicants)
        capacity = self.credit_capacity
        choice = self.model.nprandom.choice
        for borrower in applicants:
            if capacity <= 0:
                break
            prob = self.calc_loan_probability(borrower)
            rate = self.calc_loan_rate(borrower)
            amount = min(capacity, borrower.loan_demand)
            if choice([0, 1], p=[1 - prob, prob]):
                role.grant_loan(borrower, amount, rate)
                capacity -= amount
        role.loan_applicants = []

    def update_credit_capacity(self):
        equity = self.account.stocks["equity"]
        self.credit_capacity = equity * self.p.mu1

    def calc_loan_probability(self, borrower):
        return math.exp(-self.p.iota_l * borrower.target_leverage)

    def calc_loan_rate(self, borrower):
        cb = self.central_bank
        leverage = borrower.target_leverage
        return self.p.chi * leverage + cb.discount_rate

    def request_cash_advances(self):
        stocks = self.account.stocks
        required = self.p.mu2 * stocks["deposits"]
        shortage = max(required - stocks["cash"], 0)
        if shortage > 0:
            role = self.roles["lender"]
            role.request_advances(shortage)

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
        stocks = self.account.stocks
        required = self.p.mu2 * stocks["deposits"]
        return max(stocks["cash"] - required, 0)

    def calc_bond_purchases_probability(self, issuer):
        return math.exp(-self.p.iota_b * issuer.debt_ratio)

    def compute_profit_distribution(self):
        self.profit = self.calc_profit()
        self.taxes_payable = self.calc_taxes()
        self.dividends_payable = self.calc_dividends()

    def calc_profit(self):
        flows = self.account.flows
        return (
            flows["loan_interests"]
            + flows["bond_interests"]
            + flows["cash_interests"]
            - self.bad_debt
            - flows["dep_interests"]
            - flows["adv_interests"]
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
        self.net_worth += self.profit - self.taxes_payable - self.dividends_payable
        self.roles["company"].update_equity_holdings()
        return self.net_worth

    def pay_taxes(self):
        if self.taxes_payable > 0:
            taxes = self.taxes_payable
            role = self.roles["company"]
            role.pay_taxes(taxes)
            self.taxes_payable = 0

    def pay_dividends(self):
        if self.dividends_payable > 0:
            role = self.roles["company"]
            role.pay_dividends(self.dividends_payable)
            self.dividends_payable = 0

    def exit(self):
        role = self.roles["company"]
        average_wage = role.get_average_wage()
        if self.net_worth < average_wage:
            role.close_bank(self)
