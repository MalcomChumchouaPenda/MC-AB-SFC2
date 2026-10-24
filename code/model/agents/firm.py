import math
from model.extensions import EcoAgent


class Firm(EcoAgent):

    def setup(self):
        super().setup()
        self.tradable = False

        # indicators
        self.net_cash_flow = 0.0

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
        self.defaulted = False

    #
    # Production planning
    #
    def plan_production(self):
        self._calc_desired_output()
        self._calc_labor_demand()

    def _calc_desired_output(self):
        theta = self.p.theta
        inv = self.roles["producer"].inventories
        self.desired_output = max(0, self.expected_sales * (1 + theta) - inv)
        return self.desired_output

    def _calc_labor_demand(self):
        role = self.roles["producer"]
        self.desired_labor = self.desired_output / role.phi
        return self.desired_labor

    #
    # Price and quantities adaptation
    #
    def adapt_expectations(self):
        delta = self.p.delta
        random = self.model.random
        role = self.roles["producer"]
        if self.prev_sales >= self.prev_expected_sales:
            self.expected_sales *= 1 + random.uniform(0, delta)
            role.price *= 1 + random.uniform(0, delta)

        elif self.prev_output + self.prev_inventories > self.prev_sales:
            role = self.roles["producer"]
            wage_bill = -self.account["wages"]
            self.expected_sales *= 1 - random.uniform(0, delta)
            role.price *= 1 - random.uniform(0, delta)
            role.price = max(wage_bill / role.phi, role.price)

    #
    # Wage revision
    #
    def revise_wage_offer(self):
        p = self.p
        random = self.model.nprandom
        role = self.roles["employer"]
        prob = self._calc_revision_probability()
        if self.prev_desired_labor > self.prev_labor:
            if random.choice([0, 1], p=[1 - prob, prob]):
                role.wage *= 1 + random.uniform(0, p.delta)
        else:
            if random.choice([0, 1], p=[prob, 1 - prob]):
                role.wage *= 1 - random.uniform(0, p.delta)

    def _calc_revision_probability(self):
        p = self.p
        role = self.roles["employer"]
        unemployment = role.get_unemployment()
        return math.exp(-p.upsilon * unemployment)

    #
    # Innovation and imitation process
    #
    def calc_desired_rd(self):
        role = self.roles["employer"]
        self.desired_wage_bill = role.wage * self.desired_labor
        self.desired_rd = self.p.gamma * self.desired_wage_bill
        return self.desired_rd

    def execute_rd(self):
        if self.desired_rd <= 0:
            return
        roles = self.roles
        account = self.account
        labor_constraint = roles["employer"].labor < self.desired_labor
        financial_constraint = -account["loans"] < self.desired_loans
        if labor_constraint or financial_constraint:
            return
        roles["producer"].execute_rd(self.desired_rd)

    #
    # Credit transaction
    #
    def request_loans(self):
        self.desired_loans = self._calc_desired_loans()
        if self.desired_loans <= 0:
            return
        role = self.roles["borrower"]
        role.loan_demand = self.desired_loans
        lenders = role.find_lenders()
        for lender in lenders:
            role.request_loans(lender)

    def _calc_desired_loans(self):
        role = self.roles["employer"]
        deposits = self.account["deposits"]
        wage_bill = role.wage * self.desired_labor
        return max(0, wage_bill + self.desired_rd - deposits)

    def repay_loans(self):
        role = self.roles["borrower"]
        account = self.account
        self._fund_repayments()
        for loan in role.find_loans():
            deposits = account["deposits"]
            self._pay_lender(role, loan, deposits)

    def _fund_repayments(self):
        account = self.account
        loans = -account["loans"]
        deposits = account["deposits"]
        needs = max(0, loans - deposits)
        if needs > 0:
            cash = account["cash"]
            feasible = min(cash, needs)
            role = self.roles["depositor"]
            role.make_deposits(feasible)

    def _pay_lender(self, role, loan, deposits):
        lender = loan["lender"]
        principal = loan["amount"]
        interests = principal * loan["rate"]
        total = principal + interests
        if total <= deposits:
            role.repay_loans(lender, principal, interests)
        else:
            amount = min(principal, deposits)
            default = principal - amount
            role.make_defaults(lender, default)
            role.repay_loans(lender, amount, 0.0)

    #
    # Production
    #
    def produce_goods(self):
        employer_role = self.roles["employer"]
        producer_role = self.roles["producer"]
        producer_role.produce_goods(employer_role.labor)

    #
    # Wages
    #
    def pay_wages(self):
        role = self.roles["employer"]
        for job in role.get_jobs():
            worker = job["worker"]
            labor = job["quantity"]
            wages = labor * role.wage
            role.pay_wages(worker, wages)

    #
    # Profit, taxes and dividend computation
    #
    def compute_profit_distribution(self):
        self.net_cash_flow = self._calc_net_cash_flow()
        self.profit = self._calc_profit()
        self.taxes_payable = self._calc_taxes()
        self.dividends_payable = self._calc_dividends()

    def _calc_net_cash_flow(self):
        account = self.account
        return (
            account["consumption"]
            + account["dep_interests"]
            + account["wages"]
            + account["loan_interests"]
        )

    def _calc_profit(self):
        employer_role = self.roles["employer"]
        producer_role = self.roles["producer"]
        unit_cost = employer_role.wage / producer_role.phi
        inv_variation = unit_cost * (producer_role.inventories - self.prev_inventories)
        return self.net_cash_flow + inv_variation

    def _calc_taxes(self):
        if self.net_cash_flow <= 0:
            return 0
        tax_rate = self.roles["company"].get_tax_rate()
        return tax_rate * self.net_cash_flow

    def _calc_dividends(self):
        if self.net_cash_flow <= 0:
            return 0
        return self.p.rho * (self.net_cash_flow - self.taxes_payable)

    def update_net_worth(self):
        payable = self.taxes_payable + self.dividends_payable
        self.roles["company"].update_equity_shares(self.net_cash_flow - payable)

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
                founder = share["citizen"]
                dividend = share["value"] * total_dividend / total_shares
                role.pay_dividends(founder, dividend)
            self.dividends_payable = 0

    #
    # Exit process
    #
    def exit(self):
        roles = self.roles
        equity = -self.account["equities"]
        if equity < roles["employer"].wage:
            self.defaulted = True
            for role in roles.values():
                role.defaulted = True
            self._make_loan_defaults()
            self._withdraw_residual_deposits()
            self._transfer_residual_cash()

    def _withdraw_residual_deposits(self):
        amount = self.account["deposits"]
        if amount > 0:
            role = self.roles["depositor"]
            role.withdraw_deposits(amount)

    def _make_loan_defaults(self):
        role = self.roles["borrower"]
        for loan in role.find_loans():
            lender = loan["lender"]
            principal = loan["amount"]
            role.make_defaults(lender, principal)

    def _transfer_residual_cash(self):
        cash = self.account["cash"]
        if cash > 0:
            role = self.roles["company"]
            shares = role.get_equity_shares()
            total_shares = sum(share["value"] for share in shares)
            for share in shares:
                founder = share["citizen"]
                amount = share["value"] * cash / total_shares
                role.transfer_residual_cash(founder, amount)

    #
    # History
    #
    def update_production_history(self):
        role = self.roles["producer"]
        self.prev_sales = role.sales
        self.prev_expected_sales = self.expected_sales
        self.prev_inventories = role.inventories
        self.prev_output = role.output
