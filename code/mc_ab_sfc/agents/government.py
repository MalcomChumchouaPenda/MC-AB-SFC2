
from ..base import EcoAgent

class GovernmentAgent(EcoAgent):

    def setup(self):
        self._defaults = []

        # stocks
        self.reserves = 0
        self.bonds = 0

        # flows
        self.taxes = 0
        self.profit = 0
        self.public_transfers = 0
        self.bond_interest = 0

        # choices
        self.tax_rate = 0.0
        self.bond_rate = 0.0
        self.desired_public_spending = 0
        self.prev_public_spending = 0
        self.public_spending = 0
        self.prev_budget_surplus = 0
        self.new_public_debt = 0

        # indicators
        self.gdp = 0
        self.budget_deficit = 0
        self.budget_surplus = 0

    def pay_public_transfers(self):
        role = self.roles["government"]
        households = role.get_households()
        transfers = self.public_spending / len(households)
        for household in households:
            role.pay_public_transfers(household, transfers)

    def calc_budget_balance(self):
        balance = self.taxes - self.public_spending - self.bond_interest
        self.budget_deficit = max(0, -balance)
        self.budget_surplus = max(0, balance)
        return balance

    def update_fiscal_policy(self):
        p = self.p
        random = self.model.random
        variation = random.uniform(0, p.delta)
        deficit_ratio = self.budget_deficit / self.gdp
        desired_spending = self.calc_desired_public_spending()
        if deficit_ratio >= p.dmax:
            if desired_spending <= self.public_spending:
                self.public_spending *= 1 - variation
                self.tax_rate *= 1 + variation
            else:
                self.tax_rate *= 1 + variation
        else:
            if desired_spending <= self.public_spending:
                self.public_spending *= 1 - variation
                self.tax_rate *= 1 - variation
            else:
                self.public_spending *= 1 + variation
        self.apply_tax_rate_bounds()
        self.apply_public_spending_bounds()

    def calc_desired_public_spending(self):
        role = self.roles["government"]
        average_price = role.get_average_price()
        average_prod = role.get_average_productivity()
        prev_spending = self.prev_public_spending
        desired_spending = average_price * average_prod * prev_spending
        self.desired_public_spending = desired_spending
        return desired_spending

    def apply_tax_rate_bounds(self):
        self.tax_rate = max(self.p.tax_min, self.tax_rate)
        self.tax_rate = min(self.p.tax_max, self.tax_rate)

    def apply_public_spending_bounds(self):
        minimum = self.p.g_min * self.gdp
        maximum = self.p.g_max * self.gdp
        self.public_spending = max(minimum, self.public_spending)
        self.public_spending = min(maximum, self.public_spending)

    def issue_bonds(self):
        self.calc_new_debt()
        new_bonds = self.calc_new_bonds()
        role = self.roles["bond_issuer"]
        role.issue_bonds(new_bonds)

    def calc_new_debt(self):
        new_debt = self.bonds + self.budget_deficit - self.prev_budget_surplus
        self.new_public_debt = new_debt
        return new_debt

    def calc_new_bonds(self):
        return max(0, self.new_public_debt - self.bonds)

    def pay_bond_debt(self):
        self.calc_bond_rate()
        role = self.roles["bond_issuer"]
        role.pay_bond_debt()

    def calc_bond_rate(self):
        role = self.roles["government"]
        discount_rate = role.get_discount_rate()
        bond_rate = self.p.chi * (self.bonds / self.gdp) + discount_rate
        self.bond_rate = bond_rate
        return bond_rate

    def issue_deposit_guarantee_bonds(self):
        guarantee_role = self.roles["deposit_guarantee"]
        defaults = guarantee_role.get_defaulted_banks()
        needs = sum([b.defaulted_deposits for b in defaults])
        issuer_role = self.roles["bond_issuer"]
        issuer_role.issue_bonds(needs)
        self._defaults = defaults

    def reimburse_deposits(self):
        guarantee_role = self.roles["deposit_guarantee"]
        for bank in self._defaults:
            guarantee_role.reimburse_deposits(bank)

    def update_history(self):
        role = self.roles["government"]
        self.gdp = role.get_gdp()
        self.prev_budget_surplus = self.budget_surplus
        self.prev_public_spending = self.public_spending
