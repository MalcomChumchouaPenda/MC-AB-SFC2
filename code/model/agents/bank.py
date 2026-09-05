import math
from model.base import EcoAgent


class Bank(EcoAgent):

    def setup(self):
        # stocks
        self.loans = 0
        self.cash_advances = 0
        self.reserves = 0
        self.equity = 0

        # flows
        self.loan_interest = 0
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
        self.country = None

        # accointances
        self.central_bank = None

    @property
    def bonds(self):
        bond_market = self.country.union.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["principal"] for b in bonds])

    @property
    def bond_interests(self):
        bond_market = self.country.union.bond_market
        bonds = bond_market.get_buyer_bonds(self)
        return sum([b["interests"] for b in bonds])

    @property
    def deposits(self):
        total = 0
        for market in self.model.deposit_markets.values():
            deposits = market.get_bank_deposits(self)
            total += sum([d["amount"] for d in deposits])
        return total

    @property
    def dep_interests(self):
        total = 0
        for market in self.model.deposit_markets.values():
            deposits = market.get_bank_deposits(self)
            total += sum([d["interests"] for d in deposits])
        return total

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
        self.credit_capacity = self.equity * self.p.mu1

    def calc_loan_probability(self, borrower):
        return math.exp(-self.p.iota_l * borrower.target_leverage)

    def calc_loan_rate(self, borrower):
        cb = self.central_bank
        leverage = borrower.target_leverage
        return self.p.chi * leverage + cb.discount_rate

    def request_cash_advances(self):
        required = self.p.mu2 * self.deposits
        shortage = max(required - self.reserves, 0)
        if shortage > 0:
            cb = self.central_bank
            cb.cash_advances += shortage
            cb.reserves += shortage
            self.cash_advances += shortage
            self.reserves += shortage

    def buy_bonds(self):
        bond_market = self.country.union.bond_market
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
        bond_market = self.country.union.bond_market
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
            - self.dep_interests
            - self.cash_advance_interest
        )

    def calc_taxes(self):
        if self.profit <= 0:
            return 0
        govt = self.model.governments[self.country]
        return govt.tax_rate * self.profit

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
            govt = self.model.governments[self.country]
            govt.taxes += taxes
            govt.reserves += taxes
            self.taxes += taxes
            self.reserves -= taxes
            self.taxes_payable = 0

    def pay_dividends(self):
        if self.dividends_payable > 0:
            role = self.roles["company"]
            role.distribute_dividends(self.dividends_payable)
            self.dividends_payable = 0

    def exit(self):
        role = self.roles["company"]
        average_wage = role.get_average_wage()
        if self.net_worth < average_wage:
            role.close_bank(self)
