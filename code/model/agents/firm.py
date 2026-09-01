import math
from model.base import EcoAgent


class Firm(EcoAgent):

    def setup(self):
        # prices
        self.price = 0.0
        self.wage_offer = 0

        # stocks
        self.inventories = 0
        self.cash = 0
        self.loans = 0
        self.equity = 0

        # flows
        self.sales = 0
        self.wage_bill = 0
        self.loan_interest = 0
        self.rd = 0
        self.taxes = 0
        self.dividends = 0

        # indicators
        self.productivity = 0.0
        self.net_cash_flow = 0.0
        self.net_worth = 0.0

        # decisions
        self.expected_sales = 0
        self.desired_labor = 0
        self.desired_output = 0
        self.desired_loans = 0
        self.desired_rd = 0
        self.taxes_payable = 0
        self.dividends_payable = 0

        # history
        self.prev_sales = 0
        self.prev_output = 0
        self.prev_expected_sales = 0
        self.prev_inventories = 0
        self.prev_labor = 0
        self.prev_desired_labor = 0

        # other props
        self.position = 0.0
        self.country = None

    @property
    def deposits(self):
        total = 0
        for market in self.model.deposit_markets.values():
            deposits = market.get_client_deposits(self)
            total += sum([d["amount"] for d in deposits])
        return total

    @property
    def dep_interests(self):
        total = 0
        for market in self.model.deposit_markets.values():
            deposits = market.get_client_deposits(self)
            total += sum([d["interests"] for d in deposits])
        return total

    # Production planning

    def plan_production(self):
        self.calc_desired_output()
        self.calc_labor_demand()

    def calc_desired_output(self):
        theta = self.p.theta
        inv = self.inventories
        self.desired_output = max(0, self.expected_sales * (1 + theta) - inv)
        return self.desired_output

    def calc_labor_demand(self):
        self.desired_labor = self.desired_output / self.productivity
        return self.desired_labor

    # Price and quantities adaptation

    def adapt_expectations(self):
        delta = self.p.delta
        random = self.model.random
        if self.prev_sales >= self.prev_expected_sales:
            self.expected_sales *= 1 + random.uniform(0, delta)
            self.price *= 1 + random.uniform(0, delta)

        elif self.prev_output + self.prev_inventories > self.prev_sales:
            self.expected_sales *= 1 - random.uniform(0, delta)
            self.price *= 1 - random.uniform(0, delta)
            self.price = max(self.wage_bill / self.productivity, self.price)

    # Wage revision

    def revise_wage_offer(self):
        p = self.p
        random = self.model.nprandom
        prob = self.calc_revision_probability()
        if self.prev_desired_labor > self.prev_labor:
            if random.choice([0, 1], p=[1 - prob, prob]):
                self.wage_offer *= 1 + random.uniform(0, p.delta)
        else:
            if random.choice([0, 1], p=[prob, 1 - prob]):
                self.wage_offer *= 1 - random.uniform(0, p.delta)

    def calc_revision_probability(self):
        p = self.p
        role = self.roles["employer"]
        unemployment = role.get_unemployment_rate()
        return p.upsilon_f * math.exp(-p.upsilon * unemployment)

    # Innovation and imitation process

    def update_productivity(self):
        self.calc_desired_rd()
        self.execute_rd()
        if self.rd == 0:
            return self.productivity

        prob = self.calc_rd_success_probability()
        random = self.model.nprandom
        success = random.choice([0, 1], p=[1 - prob, prob])
        if success:
            delta = self.p.delta
            self.productivity *= 1 + random.uniform(0, delta)  # innovation

            producer_role = self.roles["producer"]
            avg_productivity = producer_role.get_average_productivity()
            prod_diff = avg_productivity - self.productivity
            if prod_diff > 0:
                self.productivity += random.uniform(0, prod_diff)  # imitation

    def calc_desired_rd(self):
        self.desired_wage_bill = self.wage_offer * self.desired_labor
        self.desired_rd = self.p.gamma * self.desired_wage_bill
        return self.desired_rd

    def calc_rd_success_probability(self):
        producer_role = self.roles["producer"]
        avg_price = producer_role.get_average_price()
        avg_productivity = producer_role.get_average_productivity()
        prob = 1 - math.exp(-self.p.nu * self.rd / (avg_price * avg_productivity))
        return prob

    def execute_rd(self):
        labor_constraint = self.labor < self.desired_labor
        financial_constraint = self.loans < self.desired_loans
        if labor_constraint or financial_constraint:
            self.rd = 0
        else:
            self.rd = self.desired_rd
        return self.rd

    # Credit demand

    def calc_desired_loans(self):
        wage_bill = self.wage_offer * self.desired_labor
        self.desired_loans = max(0, wage_bill + self.desired_rd - self.deposits)
        return self.desired_loans

    def request_loan(self):
        if self.desired_loans <= 0:
            return
        borrower = self.roles["borrower"]
        borrower.loan_demand = self.desired_loans
        lenders = borrower.search_lenders()
        for lender in lenders:
            borrower.request_loan(lender)

    # Profit, taxes and dividend computation

    def compute_profit_distribution(self):
        self.net_cash_flow = self.calc_net_cash_flow()
        self.profit = self.calc_profit()
        self.taxes_payable = self.calc_taxes()
        self.dividends_payable = self.calc_dividends()

    def calc_net_cash_flow(self):
        return (
            self.sales
            + self.dep_interests
            - self.wage_bill
            - self.rd
            - self.loan_interest
        )

    def calc_profit(self):
        unit_cost = self.wage_offer / self.productivity
        inv_variation = unit_cost * (self.inventories - self.prev_inventories)
        return self.net_cash_flow + inv_variation

    def calc_taxes(self):
        if self.net_cash_flow <= 0:
            return 0
        govt = self.model.governments[self.country]
        return govt.tax_rate * self.net_cash_flow

    def calc_dividends(self):
        if self.net_cash_flow <= 0:
            return 0
        return self.p.rho * (self.net_cash_flow - self.taxes_payable)

    def update_net_worth(self):
        payable = self.taxes_payable + self.dividends_payable
        self.net_worth += self.net_cash_flow - payable
        self.roles["equity_issuer"].update_equity_holdings()
        return self.net_worth

    def pay_taxes(self):
        if self.taxes_payable > 0:
            taxes = self.taxes_payable
            govt = self.model.governments[self.country]
            govt.taxes += taxes
            govt.reserves += taxes
            self.taxes += taxes
            self.cash -= taxes
            self.taxes_payable = 0

    def pay_dividends(self):
        if self.dividends_payable > 0:
            role = self.roles["equity_issuer"]
            role.distribute_dividends(self.dividends_payable)
            self.dividends_payable = 0

    def exit(self):
        role = self.roles["equity_issuer"]
        if self.net_worth < self.wage_offer:
            role.close_firm(self)

    # History

    def update_history(self):
        self.prev_sales = self.sales
        self.prev_expected_sales = self.expected_sales
        self.prev_inventories = self.inventories
        self.prev_output = self.output

