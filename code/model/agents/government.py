from model.base import EcoAgent


class Government(EcoAgent):

    def setup(self):
        super().setup()
        self._defaults = []

        # stocks
        self.reserves = 0

        # flows
        self.taxes = 0
        self.profits = 0
        self.public_transfers = 0

        # choices
        self.tax_rate = 0.0
        self.bond_rate = 0.0
        self.bond_supply = 0
        self.desired_public_spending = 0
        self.prev_public_spending = 0
        self.public_spending = 0
        self.prev_budget_surplus = 0
        self.new_public_debt = 0

        # indicators
        self.gdp = 0
        self.budget_deficit = 0
        self.budget_surplus = 0
        self.country = None

        # accointances
        self.central_bank = None

    #
    # Public tranfers
    #
    def pay_public_transfers(self):
        role = self.roles["fiscal_authority"]
        citizens = role.find_citizens()
        if len(citizens) > 0:
            transfers = self.public_spending / len(citizens)
            for household in citizens:
                role.pay_public_transfers(household, transfers)

    #
    # Fiscal policy
    #
    def calc_budget_balance(self):
        flows = self.account.flows
        balance = flows["taxes"] - flows["public_transfers"] - flows["bond_interests"]
        self.budget_deficit = max(0, -balance)
        self.budget_surplus = max(0, balance)
        return balance

    def update_fiscal_policy(self):
        p = self.p
        random = self.model.random
        variation = random.uniform(0, p.delta)
        gdp = self.roles["fiscal_authority"].get_gdp()
        ratio = self.budget_deficit / gdp
        target = self.calc_desired_public_spending()
        self._update_policy_randomly(ratio, target, variation)
        self.apply_tax_rate_bounds()
        self.apply_public_spending_bounds()

    def _update_policy_randomly(self, ratio, target, variation):
        if ratio >= self.p.dmax:
            if target <= self.public_spending:
                self.public_spending *= 1 - variation
                self.tax_rate *= 1 + variation
            else:
                self.tax_rate *= 1 + variation
        else:
            if target <= self.public_spending:
                self.public_spending *= 1 - variation
                self.tax_rate *= 1 - variation
            else:
                self.public_spending *= 1 + variation

    def calc_desired_public_spending(self):
        role = self.roles["fiscal_authority"]
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
        gdp = self.roles["fiscal_authority"].get_gdp()
        minimum = self.p.g_min * gdp
        maximum = self.p.g_max * gdp
        self.public_spending = max(minimum, self.public_spending)
        self.public_spending = min(maximum, self.public_spending)

    #
    # Bond Supply
    #
    def issue_bonds(self):
        self.calc_new_debt()
        new_bonds = self.calc_new_bonds()
        self.bond_supply += new_bonds
        gdp = self.roles["fiscal_authority"].get_gdp()
        role = self.roles["bond_issuer"]
        role.debt_ratio = self.bond_supply / gdp
        role.bond_value = self.bond_supply / 100
        role.bond_number = 100

    def calc_new_debt(self):
        bonds = self.account.stocks["bonds"]
        new_debt = bonds + self.budget_deficit - self.prev_budget_surplus
        self.new_public_debt = new_debt
        return new_debt

    def calc_new_bonds(self):
        bonds = self.account.stocks["bonds"]
        return max(0, self.new_public_debt - bonds)

    #
    # Bonds repayment
    #
    def repay_bonds(self):
        bond_rate = self.bond_rate
        role = self.roles["bond_issuer"]
        for bond in role.find_bonds():
            principal = bond["amount"]
            interests = bond_rate * principal
            role.repay_bonds(bond["buyer"], principal, interests)

    def update_bond_rate(self):
        bonds = self.account.stocks["bonds"]
        role = self.roles["fiscal_authority"]
        gdp = role.get_gdp()
        discount_rate = role.get_discount_rate()
        bond_rate = self.p.chi * (bonds / gdp) + discount_rate
        self.bond_rate = bond_rate
        return bond_rate

    #
    # Deposit guarantee
    #
    def issue_deposit_guarantee_bonds(self):
        guarantee_role = self.roles["deposit_guarantee"]
        defaults = guarantee_role.find_defaulted_banks()
        needs = sum([b.account.stocks["deposits"] for b in defaults])
        self.bond_supply += abs(needs)
        self._defaults = defaults
        issuer_role = self.roles["bond_issuer"]
        issuer_role.bond_number = 100
        issuer_role.bond_value = self.bond_supply / 100

    def reimburse_deposits(self):
        role = self.roles["deposit_guarantee"]
        for bank in self._defaults:
            for deposit in role.find_deposit_accounts(bank):
                amount = deposit["amount"]
                client = deposit["depositor"]
                role.reimburse_deposits(client, amount)

    #
    # History
    #
    def update_history(self):
        self.prev_budget_surplus = self.budget_surplus
        self.prev_public_spending = self.public_spending
