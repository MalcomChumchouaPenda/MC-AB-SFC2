import math
from functools import partial
from model.base import EcoAgent


class Household(EcoAgent):

    def setup(self):
        super().setup()
        self.net_worth = 0
        self.desired_consumption = 0

        # decisions
        self.reservation_wage = 0
        self.expected_consumption = 0
        self.desired_trad_cons = 0
        self.desired_non_trad_cons = 0
        self.desired_equity = 0
        self.desired_deposits = 0
        self.desired_investment_sector = None

        # memory
        self.employed_labor = 0
        self.income = 0
        self.disposable_income = 0

        # others props
        self.labor_supply = 1.0
        self.preference = 0

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
        employers = role.find_employers(p.psi)
        accepted = [e for e in employers if e.wage >= self.reservation_wage]
        accepted.sort(key=lambda employer: employer.wage, reverse=True)
        remaining = role.labor_supply
        for employer in accepted:
            if remaining <= 0:
                break
            quantity = min(remaining, employer.labor_demand)
            print(employer, quantity)
            if quantity > 0:
                role.accept_job(employer, quantity)
                remaining -= quantity

    def pay_taxes(self):
        self.income = self.calc_income()
        self.disposable_income = self.calc_disposable_income()
        role = self.roles["citizen"]
        tax_rate = role.get_tax_rate()
        taxes = tax_rate * self.income
        role.pay_taxes(taxes)

    def calc_income(self):
        flows = self.account.flows
        return flows["wages"] + flows["dep_interests"] + flows["dividends"]

    def calc_disposable_income(self):
        tax_rate = self.roles["citizen"].get_tax_rate()
        public_transfers = self.account.flows["public_transfers"]
        return (1 - tax_rate) * self.income + public_transfers

    def calc_consumption(self):
        p = self.p
        deposits = self.account.stocks["deposits"]
        self.desired_consumption = p.cy * self.disposable_income + p.cd * deposits
        # self.desired_trad_cons = p.cT * self.desired_consumption
        # self.desired_non_trad_cons = (1 - self.p.cT) * self.desired_consumption
        return self.desired_consumption

    def consume(self):
        p = self.p
        roles = self.roles
        desired_cons = self.desired_consumption
        steps = [
            (roles["consumer_tradable"], p.cT * desired_cons),
            (roles["consumer_non_tradable"], (1 - p.cT) * desired_cons),
        ]
        random = self.model.random
        random.shuffle(steps)
        self._fund_consumption(desired_cons)
        for role, target_cons in steps:
            self.consume_good(role, target_cons)

    def _fund_consumption(self, desired_cons):
        stocks = self.account.stocks
        if desired_cons > stocks["cash"]:
            needs = desired_cons - stocks["cash"]
            feasible = min(needs, stocks["deposits"])
            role = self.roles["depositor"]
            role.withdraw_deposits(feasible)

    def consume_good(self, role, target_cons):
        cash = self.account.stocks["cash"]
        average_price = role.get_average_price()
        suppliers = role.find_suppliers(self.p.psi)
        ranked = self.rank_suppliers(suppliers, average_price=average_price)
        for supplier in ranked:
            if target_cons <= 0 or cash <= 0:
                break
            amount = self._buy_supplier_goods(role, supplier, target_cons, cash)
            target_cons -= amount
            cash -= amount

    def _buy_supplier_goods(self, role, supplier, target_cons, cash):
        price = supplier.price
        quantity = min(supplier.inventories, target_cons / price)
        quantity = min(quantity, cash / price)
        role.buy_goods(supplier, quantity)
        return price * quantity

    def find_suppliers(self):
        p = self.p
        role = self.roles["consumer"]
        return role.find_suppliers(p.psi)

    def rank_suppliers(self, suppliers, average_price):
        key = partial(self.calc_supplier_score, average_price=average_price)
        return sorted(suppliers, key=key, reverse=True)

    def calc_supplier_score(self, supplier, average_price):
        p = self.p
        diff = abs(self.preference - supplier.variety)
        diff = min(diff, 2 * math.pi - diff)
        distance = math.sin(diff / 2)
        return (1 / distance**p.beta) * (average_price / supplier.price)

    def calc_portfolio_allocation(self):
        lp = self.calc_liquidity_preference()
        equity = self.account.stocks["equity"]
        expected_worth = self.calc_expected_net_worth()
        self.desired_equity = max(equity, (1 - lp) * expected_worth)
        self.desired_deposits = expected_worth - (self.desired_equity - equity)

    def calc_liquidity_preference(self):
        p = self.p
        roles = self.roles
        equity = self.account.stocks["equity"]
        dividends = self.account.flows["dividends"]
        default_prob = roles["citizen"].get_prob_failure()
        deposit_rate = roles["depositor"].get_deposit_rate()
        profit_ratio = dividends / equity if equity else 0
        if profit_ratio < deposit_rate or equity <= 0:
            return p.lambda_
        return p.lambda_ * math.exp(-(profit_ratio * (1 - default_prob)) - deposit_rate)

    def calc_expected_net_worth(self):
        return self.net_worth + self.disposable_income - self.expected_consumption

    def invest_equity(self):
        if self.desired_equity > 0:
            sector = self.choose_investment_sector()
            investors = self.find_potential_investors()
            required_equity = self.calc_initial_equity(sector)
            collected_equity = self.desired_equity
            initiator = self.roles["citizen"]
            founders = [initiator]
            for investor in investors:
                founders.append(investor)
                collected_equity += investor.desired_equity
                if collected_equity >= required_equity:
                    self.create_company(founders, sector)
                    break
        self.make_deposits()

    def choose_investment_sector(self):
        p = self.p
        role = self.roles["citizen"]
        ratio1 = role.get_bank_firm_number_ratio()
        ratio2 = role.get_bank_firm_equity_ratio()
        if ratio1 < p.eta or ratio2 < p.eta:
            sector = "B"
        else:
            sectors = ["FNT", "FT"]
            random = self.model.nprandom
            sector = random.choice(sectors, p=[1 - p.cT, p.cT])
        self.desired_investment_sector = sector
        return sector

    def find_potential_investors(self):
        role = self.roles["citizen"]
        return role.get_potential_investors()

    def calc_initial_equity(self, sector):
        role = self.roles["citizen"]
        range_ = role.get_sector_equity_range(sector)
        if range_ is None:
            return self.p.initial_equity
        minimum, maximum = range_
        random = self.model.nprandom
        return random.uniform(minimum, maximum)

    def create_company(self, founders, sector):
        role = self.roles["citizen"]
        if sector == "B":
            role.create_bank(founders)
        elif sector == "FT":
            role.create_firm(founders, tradable=True)
        else:
            role.create_firm(founders, tradable=False)

    def make_deposits(self):
        account = self.account
        role = self.roles["depositor"]
        role.make_deposits(account.stocks["cash"])

    def choose_deposit_bank(self):
        role = self.roles["depositor"]
        banks = role.find_deposit_banks()
        if len(banks) > 0:
            random = self.model.random
            new_bank = random.choice(banks)
            role.choose_bank(new_bank)
