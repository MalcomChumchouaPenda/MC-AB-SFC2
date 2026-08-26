import math
from functools import partial
from ..base import EcoAgent


class Household(EcoAgent):

    def setup(self):
        # stocks
        self.cash = 0
        self.equity = 0
        self.net_worth = 0

        # flows
        self.labor_income = 0
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
        self.desired_equity = 0
        self.desired_deposits = 0
        self.desired_investment_sector = None

        # memory
        self.employed_labor = 0
        self.income = 0
        self.disposable_income = 0

        # others props
        self.labor_supply = 1.0
        self.position = 0
        self.country = None

        # accointances
        self.deposit_bank = None

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
        govt = self.model.governments[self.country]
        self.income = self.calc_income()
        self.disposable_income = self.calc_disposable_income()
        taxes = govt.tax_rate * self.income
        govt.reserves += taxes
        govt.taxes += taxes
        self.cash -= taxes
        self.taxes += taxes

    def calc_income(self):
        return self.labor_income + self.dep_interests + self.dividends + self.rd_income

    def calc_disposable_income(self):
        govt = self.model.governments[self.country]
        return (1 - govt.tax_rate) * self.income + self.public_transfers

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
        deposit_rate = self.deposit_bank.deposit_rate
        profit_ratio = self.dividends / equity if equity else 0
        if profit_ratio < deposit_rate or self.equity <= 0:
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
            initiator = self.roles["equity_holder"]
            founders = [initiator]
            for investor in investors:
                founders.append(investor)
                collected_equity += investor.desired_equity
                if collected_equity >= required_equity:
                    self.create_enterprise(founders, sector)
                    break
        self.make_deposits()

    def choose_investment_sector(self):
        p = self.p
        role = self.roles["equity_holder"]
        ratio1 = role.get_bank_firm_number_ratio()
        ratio2 = role.get_bank_firm_equity_ratio()
        if ratio1 < p.eta or ratio2 < p.eta:
            sector = "banks"
        else:
            sectors = ["non_tradable_firms", "tradable_firms"]
            random = self.model.nprandom
            sector = random.choice(sectors, p=[1 - p.cT, p.cT])
        self.desired_investment_sector = sector
        return sector

    def find_potential_investors(self):
        role = self.roles["equity_holder"]
        return role.get_potential_investors()

    def calc_initial_equity(self, sector):
        role = self.roles["equity_holder"]
        range_ = role.get_sector_equity_range(sector)
        if range_ is None:
            return self.p.initial_equity
        minimum, maximum = range_
        random = self.model.nprandom
        return random.uniform(minimum, maximum)

    def create_enterprise(self, founders, sector):
        role = self.roles["equity_holder"]
        if sector == "banks":
            role.create_bank(founders)
        elif sector == "tradable_firms":
            role.create_firm(founders, tradable=True)
        else:
            role.create_firm(founders, tradable=False)

    def make_deposits(self):
        bank = self.deposit_bank
        market = self.model.deposit_markets[self.country]
        market.make_deposits(self, bank, self.cash)

    def choose_deposit_bank(self):
        old_bank = self.deposit_bank
        country = self.country
        deposit_market = self.model.deposit_markets[country]
        banks = deposit_market.get_banks()
        if len(banks) > 0:
            random = self.model.random
            new_bank = random.choice(banks)
            if old_bank is None:
                deposit_market.open_account(self, new_bank)
            else:
                amount = deposit_market.close_account(self, old_bank)
                deposit_market.open_account(self, new_bank, amount=amount)
            self.deposit_bank = new_bank
