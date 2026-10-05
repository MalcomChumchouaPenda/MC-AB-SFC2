import math
from functools import partial
from model.extensions import EcoAgent
from model.agents.firm import Firm
from model.agents.bank import Bank


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
        self.deposit_bank_id = None

        # others props
        self.labor_supply = 1.0
        self.preference = 0

    def revise_reservation_wage(self):
        p = self.p
        random = self.model.nprandom
        prob = self.calc_revision_probability()
        if self.labor_supply == self.prev_labor_sold:
            if random.choice([0, 1], p=[1 - prob, prob]):
                self.reservation_wage *= 1 + random.uniform(0, p.delta)
        else:
            if random.choice([0, 1], p=[prob, 1 - prob]):
                self.reservation_wage *= 1 - random.uniform(0, p.delta)

    def calc_revision_probability(self):
        p = self.p
        role = self.roles["worker"]
        unemployment = role.get_unemployment()
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
        account = self.account
        return account["wages"] + account["dep_interests"] + account["dividends"]

    def calc_disposable_income(self):
        tax_rate = self.roles["citizen"].get_tax_rate()
        public_transfers = self.account["public_transfers"]
        return (1 - tax_rate) * self.income + public_transfers

    #
    # Consumption
    #
    def calc_consumption(self):
        p = self.p
        deposits = self.account["deposits"]
        self.desired_consumption = p.cy * self.disposable_income + p.cd * deposits
        return self.desired_consumption

    def consume(self):
        p = self.p
        roles = self.roles
        desired_cons = self.desired_consumption
        steps = [("trad_consumer", p.cT), ("non_trad_consumer", (1 - p.cT))]
        random = self.model.random
        random.shuffle(steps)
        self._fund_consumption(desired_cons)
        for name, share in steps:
            role = roles[name]
            target_cons = share * desired_cons
            self.consume_good(role, target_cons)

    def _fund_consumption(self, desired_cons):
        account = self.account
        if desired_cons > account["cash"]:
            needs = desired_cons - account["cash"]
            feasible = min(needs, account["deposits"])
            role = self.roles["depositor"]
            role.withdraw_deposits(feasible)

    def consume_good(self, role, target_cons):
        cash = self.account["cash"]
        for supplier in self._list_suppliers(role):
            if target_cons <= 0 or cash <= 0:
                break
            amount = self._buy_supplier_goods(role, supplier, target_cons, cash)
            target_cons -= amount
            cash -= amount

    def _list_suppliers(self, role):
        average_price = role.get_average_price()
        suppliers = role.find_suppliers(self.p.psi)
        return self.rank_suppliers(suppliers, average_price=average_price)

    def _buy_supplier_goods(self, role, supplier, target_cons, cash):
        price = supplier.price
        quantity = min(supplier.inventories, target_cons / price)
        quantity = min(quantity, cash / price)
        role.buy_goods(supplier, quantity)
        return price * quantity

    def rank_suppliers(self, suppliers, average_price):
        key = partial(self.calc_supplier_score, average_price=average_price)
        return sorted(suppliers, key=key, reverse=True)

    def calc_supplier_score(self, supplier, average_price):
        p = self.p
        diff = abs(self.preference - supplier.variety)
        diff = min(diff, 2 * math.pi - diff)
        distance = math.sin(diff / 2)
        return (1 / distance**p.beta) * (average_price / supplier.price)

    #
    # Equity investment
    #
    def choose_portfolio_allocation(self):
        self.calc_net_worth()
        lp = self.calc_liquidity_preference()
        print(lp, self.net_worth)
        equity = self.account["equities"]
        expected_worth = self.calc_expected_net_worth()
        self.desired_equity = max(equity, (1 - lp) * expected_worth)
        self.desired_deposits = expected_worth - (self.desired_equity - equity)
        self.roles["citizen"].resid_equity = self.desired_equity

    def calc_liquidity_preference(self):
        p = self.p
        roles = self.roles
        equity = self.account["equities"]
        dividends = self.account["dividends"]
        default_prob = roles["citizen"].get_prob_failure()
        deposit_rate = roles["depositor"].get_deposit_rate(self.deposit_bank_id)
        profit_ratio = dividends / equity if equity else 0
        if profit_ratio < deposit_rate or equity <= 0:
            return p.lambda_
        return p.lambda_ * math.exp(profit_ratio * (1 - default_prob) - deposit_rate)

    def calc_net_worth(self):
        account = self.account
        self.net_worth = account["deposits"] + account["equities"] + account["cash"]

    def calc_expected_net_worth(self):
        return self.net_worth + self.disposable_income - self.expected_consumption

    def invest_equity(self):
        if self.desired_equity > 0:
            sector = self.choose_investment_sector()
            investors = self.find_potential_investors()
            required_equity = self.calc_initial_equity(sector)
            collected_equity = self.desired_equity
            initiator = self.roles["citizen"]
            shares = [{"founder": initiator, "amount": initiator.resid_equity}]
            for investor in investors:
                shares.append({"founder": investor, "amount": investor.resid_equity})
                collected_equity += investor.resid_equity
                if collected_equity >= required_equity:
                    self.create_company(shares, sector)
                    break

    def choose_investment_sector(self):
        p = self.p
        role = self.roles["citizen"]
        ratio1 = role.get_bank_number_ratio()
        ratio2 = role.get_bank_equity_ratio()
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
        return role.find_investors()

    def calc_initial_equity(self, sector):
        role = self.roles["citizen"]
        range_ = role.get_sector_equity_range(sector)
        if range_ is None:
            return self.p.initial_equity
        minimum, maximum = range_
        random = self.model.nprandom
        return random.uniform(minimum, maximum)

    def create_company(self, shares, sector):
        if sector == "B":
            self._create_bank(shares)
        else:
            self._create_firm(shares, sector)

    def _create_bank(self, shares):
        model = self.model
        bank = Bank(model)
        model.union.add_bank(bank)
        model.banks.append(bank)
        for share in shares:
            share["founder"].fund_company(bank.id, share["amount"])

    def _create_firm(self, shares, sector):
        model = self.model
        firm = Firm(model)
        firm.tradable = sector == "FT"
        model.union.add_firm(firm)
        model.firms.append(firm)
        for share in shares:
            share["founder"].fund_company(firm.id, share["amount"])

    #
    # Deposits management
    #
    def make_deposits(self):
        account = self.account
        bank_id = self.deposit_bank_id
        role = self.roles["depositor"]
        role.make_deposits(bank_id, account["cash"])

    def choose_deposit_bank(self):
        role = self.roles["depositor"]
        banks = role.find_deposit_banks()
        if len(banks) > 0:
            bank_id = self.deposit_bank_id
            if bank_id is not None:
                role.leave_deposit_bank(bank_id)
            random = self.model.random
            new_bank = random.choice(banks)
            role.join_deposit_bank(new_bank.id)
            self.deposit_bank_id = new_bank.id
