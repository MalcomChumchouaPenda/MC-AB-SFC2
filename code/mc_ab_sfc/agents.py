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
        self.deposit_interest = 0
        self.dividends = 0
        self.rd_income = 0
        self.taxes = 0
        self.public_transfers = 0
        self.tradable_cons = 0
        self.non_tradable_cons = 0

        # decisions
        self.reservation_wage = 0
        self.expected_consumption = 0
        self.desired_trad_cons = 0
        self.desired_non_trad_cons = 0

        # memory
        self.employed_labor = 0
        self.income = 0
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
        accepted = [e for e in employers if e.wage_offer >= self.reservation_wage]
        accepted.sort(key=lambda employer: employer.wage_offer, reverse=True)
        remaining = self.labor_supply - role.get_labor_sold()
        for employer in accepted:
            if remaining <= 0:
                break
            quantity = min(remaining, employer.labor_demand)
            if quantity > 0:
                role.create_job(employer, quantity)
                remaining -= quantity

    def pay_taxes(self):
        self.income = self.calc_income()
        self.disposable_income = self.calc_disposable_income()
        role = self.roles["tax_payer"]
        tax_rate = role.get_tax_rate()
        taxes = tax_rate * self.income
        role.pay_taxes(taxes)

    def calc_income(self):
        return (
            self.labor_income + self.deposit_interest + self.dividends + self.rd_income
        )

    def calc_disposable_income(self):
        role = self.roles["tax_payer"]
        tax_rate = role.get_tax_rate()
        return (1 - tax_rate) * self.income + self.public_transfers

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

    def setup(self):
        # prices
        self.price = 0.0
        self.wage_offer = 0

        # stocks
        self.inventories = 0
        self.cash = 0
        self.loans = 0
        self.deposits = 0
        self.equity = 0

        # flows
        self.sales = 0
        self.wage_bill = 0
        self.loan_interest = 0
        self.deposit_interest = 0
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
            + self.deposit_interest
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
        role = self.roles["tax_payer"]
        tax_rate = role.get_tax_rate()
        return tax_rate * self.net_cash_flow

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
            role = self.roles["tax_payer"]
            role.pay_taxes(self.taxes_payable)
            self.taxes_payable = 0

    def pay_dividends(self):
        if self.dividends_payable > 0:
            role = self.roles["equity_issuer"]
            role.distribute_dividends(self.dividends_payable)
            self.dividends_payable = 0

    # History

    def update_history(self):
        self.prev_sales = self.sales
        self.prev_expected_sales = self.expected_sales
        self.prev_inventories = self.inventories
        self.prev_output = self.output


class BankAgent(EcoAgent):

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

    def invest_excess_reserves(self):
        role = self.roles["bond_buyer"]
        bond_issuers = role.get_bond_issuers()
        random = self.model.random
        random.shuffle(bond_issuers)

        required = self.p.mu2 * self.deposits
        excess = max(self.reserves - required, 0)
        choice = self.model.nprandom.choice
        for issuer in bond_issuers:
            prob = self.calc_bond_purchases_probability(issuer)
            if choice([0, 1], p=[1 - prob, prob]):
                purchase = min(excess, issuer.bond_supply)
                role.buy_bonds(issuer, purchase)
                excess -= purchase
                if excess <= 0:
                    break

    def calc_bond_purchases_probability(self, issuer):
        return math.exp(-self.p.iota_b * issuer.bonds / issuer.gdp)

    def compute_profit_distribution(self):
        self.profit = self.calc_profit()
        self.taxes_payable = self.calc_taxes()
        self.dividends_payable = self.calc_dividends()

    def calc_profit(self):
        return (
            self.loan_interest
            + self.bond_interest
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


class GovernmentAgent(EcoAgent):

    def setup(self):
        # stocks
        self.reserves = 0
        self.bonds = 0

        # flows
        self.taxes = 0
        self.profit = 0
        self.public_transfers = 0

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
        self.desired_public_spending =  desired_spending
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
        print(self.bonds, self.budget_deficit, self.prev_budget_surplus)
        role = self.roles['bond_issuer']
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
        bond_rate =  self.p.chi * (self.bonds / self.gdp) + discount_rate
        self.bond_rate = bond_rate
        return bond_rate

    def update_history(self):
        role = self.roles["government"]
        self.gdp = role.get_gdp()
        self.prev_budget_surplus = self.budget_surplus
        self.prev_public_spending = self.public_spending


class CentralBankAgent(EcoAgent):

    def setup(self):
        # stocks
        self.bonds = 0
        self.reserves = 0
        self.cash_advances = 0

        # flows
        self.profit = 0
        self.bond_interest = 0
        self.reserve_interest = 0
        self.cash_advance_interest = 0

        # history
        self.prev_discount_rate = 0

    def update_discount_rate(self):
        role = self.roles["central_bank"]
        role.discount_rate = self.calc_discount_rate()

    def calc_discount_rate(self):
        p = self.model.p
        role = self.roles["central_bank"]
        average_inflation = role.get_average_inflation()
        inflation_gap = average_inflation - p.inflation_target
        return (
            (1 - p.xi) * p.long_run_rate
            + p.xi * self.prev_discount_rate
            + (1 - p.xi) * p.xi_deltap * inflation_gap
        )

    def buy_remaining_bonds(self):
        role = self.roles["bond_buyer"]
        bond_issuers = role.get_bond_issuers()
        for issuer in bond_issuers:
            purchase = issuer.bond_supply
            print(issuer, purchase)
            role.buy_bonds(issuer, purchase)

    def pay_profit(self):
        profit = self.calc_profit()
        role = self.roles["central_bank"]
        role.transfer_profit(profit)

    def calc_profit(self):
        return self.bond_interest + self.cash_advance_interest - self.reserve_interest

    def update_history(self):
        role = self.roles["central_bank"]
        self.prev_discount_rate = role.discount_rate
