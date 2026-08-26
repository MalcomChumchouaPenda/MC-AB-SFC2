import math
from ..base import EcoAgent


class Bank(EcoAgent):

    def setup(self):
        # stocks
        self.loans = 0
        self.deposits = 0
        self.cash_advances = 0
        self.reserves = 0
        self.equity = 0

        # flows
        self.loan_interest = 0
        self.deposit_interest = 0
        self.bond_interest = 0
        self.reserve_interest = 0
        self.cash_advance_interest = 0
        self.dividends = 0
        self.taxes = 0

        # choices
        self.deposit_rate = 0
        self.taxes_payable = 0
        self.dividends_payable = 0

        # indicators
        self.profit = 0
        self.net_worth = 0
        self.credit_capacity = 0
        self.defaulted = False

    @property
    def bonds(self):
        bond_market = self.model.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["principal"] for b in bonds])

    @property
    def bond_interests(self):
        bond_market = self.model.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["interests"] for b in bonds])

    def update_deposit_rate(self):
        role = self.roles["commercial_bank"]
        discount_rate = role.get_discount_rate()
        self.deposit_rate = self.p.zeta * discount_rate

    def pay_deposit_interest(self):
        role = self.roles["deposit_bank"]
        role.pay_deposit_interest()

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
        self.credit_capacity = self.equity * self.p.mu1

    def calc_loan_probability(self, borrower):
        return math.exp(-self.p.iota_l * borrower.target_leverage)

    def calc_loan_rate(self, borrower):
        bank_role = self.roles["commercial_bank"]
        discount_rate = bank_role.get_discount_rate()
        leverage = borrower.target_leverage
        return self.p.chi * leverage + discount_rate

    def request_cash_advances(self):
        required = self.p.mu2 * self.deposits
        shortage = max(required - self.reserves, 0)
        if shortage > 0:
            role = self.roles["commercial_bank"]
            role.request_cash_advances(shortage)

    def buy_bonds(self):
        bond_market = self.model.bond_market
        bond_issuers = self.find_bond_issuers()
        excess = self.calc_excess_reserves()
        choice = self.model.nprandom.choice
        for issuer in bond_issuers:
            prob = self.calc_bond_purchases_probability(issuer)
            if choice([0, 1], p=[1 - prob, prob]):
                purchase = min(excess, issuer.bond_supply)
                bond_market.buy_bonds(self, issuer, purchase)
                excess -= purchase
                if excess <= 0:
                    break

    def find_bond_issuers(self):
        bond_market = self.model.bond_market
        bond_issuers = bond_market.get_issuers()
        random = self.model.random
        random.shuffle(bond_issuers)
        return bond_issuers

    def calc_excess_reserves(self):
        required = self.p.mu2 * self.deposits
        return max(self.reserves - required, 0)

    def calc_bond_purchases_probability(self, issuer):
        return math.exp(-self.p.iota_b * issuer.bonds / issuer.gdp)

    def compute_profit_distribution(self):
        self.profit = self.calc_profit()
        self.taxes_payable = self.calc_taxes()
        self.dividends_payable = self.calc_dividends()

    def calc_profit(self):
        return (
            self.loan_interest
            + self.bond_interests
            + self.reserve_interest
            - self.bad_debt
            - self.deposit_interest
            - self.cash_advance_interest
        )

    def calc_taxes(self):
        if self.profit <= 0:
            return 0
        role = self.roles["tax_payer"]
        rate = role.get_tax_rate()
        return rate * self.profit

    def calc_dividends(self):
        if self.profit <= 0:
            return 0
        return self.p.rho * (self.profit - self.taxes_payable)

    def update_net_worth(self):
        self.net_worth += self.profit - self.taxes_payable - self.dividends_payable
        self.roles["equity_issuer"].update_equity_holdings()
        return self.net_worth

    def pay_taxes(self):
        if self.taxes_payable > 0:
            role = self.roles["tax_payer"]
            role.pay_taxes(self.taxes_payable)
            self.taxes_payable = 0

    def pay_dividends(self):
        if self.dividends_payable > 0:
            role = self.roles["equity_issuer"]
            role.distribute_dividends(self.dividends_payable)
            self.dividends_payable = 0

    def exit(self):
        role = self.roles["equity_issuer"]
        average_wage = role.get_average_wage()
        if self.net_worth < average_wage:
            role.close_bank(self)
