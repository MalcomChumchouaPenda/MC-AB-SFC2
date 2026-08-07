import math
from functools import partial
import agentpy as ap
from .base import EcoAgent


class HouseholdAgent(EcoAgent):

    def setup(self):
        # stocks
        self.cash = 0
        self.deposits = 0
        self.equity = 0
        self.net_worth = 0

        # flows
        self.labor_income = 0
        self.deposit_interests = 0
        self.dividends = 0
        self.rnd_income = 0
        self.public_transfer = 0
        self.tradable_cons = 0
        self.non_tradable_cons = 0

        # decisions
        self.reservation_wage = 0
        self.expected_consumption = 0
        self.desired_trad_cons = 0
        self.desired_non_trad_cons = 0

        # memory
        self.employed_labor = 0
        self.gross_income = 0
        self.disposable_income = 0

        # others props
        self.labor_supply = 1.0
        self.position = 0

    def revise_reservation_wage(self):
        p = self.p
        random = self.model.nprandom
        prob = self.calc_revision_probability()
        if self.employed_labor == self.labor_supply:
            if random.choice([0, 1], p=[1 - prob, prob]):
                self.reservation_wage *= 1 + random.uniform(0, p.delta)
        else:
            if random.choice([0, 1], p=[prob, 1 - prob]):
                self.reservation_wage *= 1 - random.uniform(0, p.delta)

    def calc_revision_probability(self):
        p = self.p
        role = self.roles["worker"]
        unemployment = role.get_unemployment_rate()
        return p.upsilon_h * math.exp(-p.upsilon * unemployment)

    def search_jobs(self):
        p = self.p
        role = self.roles["worker"]
        employers = role.search_employers(p.psi)
        print(p.psi, employers)
        accepted = [e for e in employers if e.wage_offer >= self.reservation_wage]
        accepted.sort(key=lambda employer: employer.wage_offer, reverse=True)
        remaining = self.labor_supply - role.get_labor_sold()
        print(accepted, remaining)
        for employer in accepted:
            if remaining <= 0:
                break
            quantity = min(remaining, employer.labor_demand)
            print(quantity, remaining, employer.labor_demand)
            if quantity > 0:
                role.create_job(employer, quantity)
                remaining -= quantity
                print("create job", employer, quantity)

    def calc_gross_income(self):
        self.gross_income = (
            self.labor_income
            + self.deposit_interests
            + self.dividends
            + self.rnd_income
        )
        return self.gross_income

    def calc_disposable_income(self):
        role = self.roles["citizen"]
        tax_rate = role.get_tax_rate()
        self.disposable_income = (
            1 - tax_rate
        ) * self.gross_income + self.public_transfer
        return self.disposable_income

    def calc_consumption(self):
        p = self.p
        self.desired_consumption = p.cy * self.disposable_income + p.cd * self.deposits
        self.desired_trad_cons = p.cT * self.desired_consumption
        self.desired_non_trad_cons = (1 - self.p.cT) * self.desired_consumption
        return self.desired_consumption

    def consume(self):
        p = self.p
        random = self.model.random
        consumer_roles = [
            self.roles["consumer_tradable"],
            self.roles["consumer_non_tradable"],
        ]
        random.shuffle(consumer_roles)
        for role in consumer_roles:
            average_price = role.get_average_price()
            suppliers = role.search_suppliers(p.psi)
            ranked = self.rank_suppliers(suppliers, average_price=average_price)
            role.buy_goods(ranked)

    def search_suppliers(self):
        p = self.p
        role = self.roles["consumer"]
        return role.search_suppliers(p.psi)

    def rank_suppliers(self, suppliers, average_price):
        key = partial(self.calc_supplier_score, average_price=average_price)
        return sorted(suppliers, key=key, reverse=True)

    def calc_supplier_score(self, supplier, average_price):
        p = self.p
        diff = abs(self.position - supplier.position)
        diff = min(diff, 2 * math.pi - diff)
        distance = math.sin(diff / 2)
        return (1 / distance**p.beta) * (average_price / supplier.price)

    def calc_portfolio_allocation(self):
        lp = self.calc_liquidity_preference()
        expected_worth = self.calc_expected_net_worth()
        self.desired_equity = max(self.equity, (1 - lp) * expected_worth)
        self.desired_deposits = expected_worth - (self.desired_equity - self.equity)

    def calc_liquidity_preference(self):
        p = self.p
        roles = self.roles
        equity = self.equity
        default_prob = roles["equity_holder"].get_default_probability()
        deposit_rate = roles["deposit_holder"].get_deposit_rate()
        profit_ratio = self.dividends / equity if equity else 0
        if profit_ratio < deposit_rate or self.equity <= 0:
            return p.lambda_
        return p.lambda_ * math.exp(-(profit_ratio * (1 - default_prob)) - deposit_rate)

    def calc_expected_net_worth(self):
        return self.net_worth + self.disposable_income - self.expected_consumption


class FirmAgent(EcoAgent):

    def setup(self, **kwargs):
        # prices
        self.price = 0.0
        self.wage_offer = 0

        # stocks
        self.inventories = 0
        self.cash = 0
        self.loans = 0

        # flows
        self.sales = 0
        self.wage_bill = 0

        # other props
        self.position = 0.0
        self.productivity = 0.0

        # decisions
        self.expected_sales = 0
        self.desired_labor = 0
        self.desired_output = 0
        self.desired_loans = 0
        self.desired_rd = 0

        # history
        self.prev_sales = 0
        self.prev_output = 0
        self.prev_expected_sales = 0
        self.prev_inventories = 0
        self.prev_labor = 0
        self.prev_desired_labor = 0

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

    def update_history(self):
        super().update_history()
        self.prev_sales = self.sales
        self.prev_expected_sales = self.expected_sales
        self.prev_inventories = self.inventories
        self.prev_output = self.output

    def calc_desired_loans(self):
        wage_bill = self.wage_offer * self.desired_labor
        self.desired_loans = max(0, wage_bill + self.desired_rd - self.deposits)
        return self.desired_loans


class BankAgent(EcoAgent):
    pass


class GovernmentAgent(EcoAgent):
    pass


class CentralBankAgent(EcoAgent):
    pass
