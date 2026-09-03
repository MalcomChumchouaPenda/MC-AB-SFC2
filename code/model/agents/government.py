from model.base import EcoAgent


class Government(EcoAgent):

    def setup(self):
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

    @property
    def bonds(self):
        bond_market = self.country.union.bond_market
        bonds = bond_market.get_issuer_bonds(self)
        return sum([b["principal"] for b in bonds])

    @property
    def bond_interests(self):
        bond_market = self.country.union.bond_market
        bonds = bond_market.get_issuer_bonds(self)
        return sum([b["interests"] for b in bonds])

    def pay_public_transfers(self):
        country = self.country
        model = self.model
        households = [h for h in model.households if h.country == country]
        if len(households) > 0:
            transfers = self.public_spending / len(households)
            for household in households:
                household.cash += transfers
                household.public_transfers += transfers
                self.public_transfers += transfers
                self.reserves -= transfers

    def calc_budget_balance(self):
        balance = self.taxes - self.public_spending - self.bond_interests
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
        goods_market = self.model.goods_markets[self.country]
        average_price = goods_market.average_price
        average_prod = goods_market.average_productivity
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
        self.bond_supply += new_bonds

    def calc_new_debt(self):
        new_debt = self.bonds + self.budget_deficit - self.prev_budget_surplus
        self.new_public_debt = new_debt
        return new_debt

    def calc_new_bonds(self):
        return max(0, self.new_public_debt - self.bonds)

    def repay_bonds(self):
        bond_rate = self.calc_bond_rate()
        bond_market = self.country.union.bond_market
        for bond in bond_market.get_issuer_bonds(self):
            principal = bond["principal"]
            interests = bond_rate * principal
            bond_market.repay_bonds(self, bond["buyer"], principal, interests)
        self.bond_rate = bond_rate

    def calc_bond_rate(self):
        discount_rate = self.central_bank.discount_rate
        return self.p.chi * (self.bonds / self.gdp) + discount_rate

    def issue_deposit_guarantee_bonds(self):
        deposit_market = self.model.deposit_markets[self.country]
        defaults = deposit_market.get_defaulted_banks()
        needs = sum([b.deposits for b in defaults])
        self.bond_supply += needs
        self._defaults = defaults

    def reimburse_deposits(self):
        market = self.model.deposit_markets[self.country]
        for bank in self._defaults:
            for deposit in market.get_bank_deposits(bank):
                client = deposit["client"]
                market.reimburse_deposits(self, client, bank)

    def update_history(self):
        goods_market = self.model.goods_markets[self.country]
        self.gdp = goods_market.gdp
        self.prev_budget_surplus = self.budget_surplus
        self.prev_public_spending = self.public_spending
