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
        p = self.p
        self.reservation_wage = p.initial_wage
        self.expected_consumption = 0
        self.desired_trad_cons = 0
        self.desired_non_trad_cons = 0
        self.desired_equity = 0
        self.desired_deposits = 0
        self.desired_investment_sector = None

        # memory
        self.income = 0
        self.disposable_income = 0
        self.prev_labor_sold = 0

        # others props
        random = self.model.nprandom
        self.preference = random.uniform(0, math.radians(360))
        self.labor_supply = 1.0

    def revise_reservation_wage(self):
        p = self.p
        random = self.model.nprandom
        prob = self._calc_revision_probability()
        if self.labor_supply == self.prev_labor_sold:
            if random.choice([0, 1], p=[1 - prob, prob]):
                self.reservation_wage *= 1 + random.uniform(0, p.delta)
        else:
            if random.choice([0, 1], p=[prob, 1 - prob]):
                self.reservation_wage *= 1 - random.uniform(0, p.delta)

    def _calc_revision_probability(self):
        p = self.p
        role = self.roles["worker"]
        unemployment = role.get_unemployment()
        return math.exp(-p.upsilon * unemployment)

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
        self.income = self._calc_income()
        self.disposable_income = self._calc_disposable_income()
        role = self.roles["citizen"]
        tax_rate = role.get_tax_rate()
        taxes = tax_rate * self.income
        role.pay_taxes(taxes)

    def _calc_income(self):
        account = self.account
        wages = account["wages"] 
        dividends = account["dividends"]
        dep_ints = account["dep_interests"]
        return wages + dep_ints + dividends

    def _calc_disposable_income(self):
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
            self._consume_good(role, target_cons)

    def _fund_consumption(self, desired_cons):
        cash = self.account["cash"]
        if desired_cons > cash:
            needs = desired_cons - cash
            self._withdraw_deposits(needs)

    def _consume_good(self, role, target_cons):
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
        return self._rank_suppliers(suppliers, average_price=average_price)

    def _buy_supplier_goods(self, role, supplier, target_cons, cash):
        price = supplier.price
        quantity = min(supplier.inventories, target_cons / price)
        quantity = min(quantity, cash / price)
        role.buy_goods(supplier, quantity)
        return price * quantity

    def _rank_suppliers(self, suppliers, average_price):
        key = partial(self._calc_supplier_score, average_price=average_price)
        return sorted(suppliers, key=key, reverse=True)

    def _calc_supplier_score(self, supplier, average_price):
        p = self.p
        diff = abs(self.preference - supplier.variety)
        diff = min(diff, 2 * math.pi - diff)
        distance = math.sin(diff / 2)
        return (1 / distance**p.beta) * (average_price / supplier.price)

    #
    # Equity investment
    #
    def choose_portfolio_allocation(self):
        self._calc_net_worth()
        equities = self.account["equities"]
        lp = self._calc_liquidity_preference()
        expected_worth = self._calc_expected_net_worth()
        self.desired_equity = max(equities, (1 - lp) * expected_worth)
        self.desired_deposits = expected_worth - (self.desired_equity - equities)
        self.roles["citizen"].resid_equity = self.desired_equity

    def _calc_liquidity_preference(self):
        p = self.p
        roles = self.roles
        equities = self.account["equities"]
        dividends = self.account["dividends"]
        default_prob = roles["citizen"].get_prob_failure()
        deposit_rate = roles["depositor"].get_deposit_rate()
        profit_ratio = dividends / equities if equities else 0
        if profit_ratio < deposit_rate or equities <= 0:
            return p.lambda_
        return p.lambda_ * math.exp(profit_ratio * (1 - default_prob) - deposit_rate)

    def _calc_net_worth(self):
        account = self.account
        cash = account["cash"]
        deposits = account["deposits"] 
        equities = account["equities"] 
        self.net_worth = deposits + equities + cash

    def _calc_expected_net_worth(self):
        return self.net_worth + self.disposable_income - self.expected_consumption

    #
    # Firm and Bank creation
    #
    def invest_equity(self):
        if self.desired_equity > 0:
            sector = self._choose_investment_sector()
            target = self._calc_initial_equity(sector)
            shares = self._collect_equity_shares(target)
            if shares is not None:
                equity_size = sum([share["amount"] for share in shares])
                agent_id = self._create_company(sector, equity_size)
                self._fund_company(agent_id, shares)
        bank_id = self._choose_deposit_bank()
        if bank_id is not None:
            self._make_deposits(bank_id)

    def _choose_investment_sector(self):
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

    def _calc_initial_equity(self, sector):
        p = self.p
        random = self.model.nprandom
        role = self.roles["citizen"]
        range_ = role.get_equity_range(sector)
        if sector == "B":
            median_size = role.get_median_firm_size()
            if range_ is None:
                minimum = p.sigma * median_size
                maximum = max(minimum, p.initial_equity)
            else:
                minimum, maximum = range_
                minimum = max(p.sigma * median_size, minimum)
                maximum = max(minimum, maximum)
        else:
            if range_ is None:
                return p.initial_equity
            minimum, maximum = range_
        return random.uniform(minimum, maximum)

    def _collect_equity_shares(self, target):
        p = self.p
        initiator = self.roles["citizen"]
        collected_equity = initiator.resid_equity
        min_equity = p.omega * initiator.get_average_wage()
        shares = [{"citizen": initiator, "amount": initiator.resid_equity}]
        for investor in initiator.find_investors():
            if investor.resid_equity < min_equity or investor.company_number >= p.psi:
                continue
            shares.append({"citizen": investor, "amount": investor.resid_equity})
            collected_equity += investor.resid_equity
            if collected_equity > target:
                break
        if collected_equity < target:
            return None
        return shares

    def _create_company(self, sector, equity_size):
        model = self.model
        if sector == "B":
            bank = Bank(model)
            bank.country_pos = self.country_pos
            model.union.add_agents([bank])
            model.banks.append(bank)
            return bank.id
        else:
            firm = Firm(model)
            firm.tradable = sector == "FT"
            firm.country_pos = self.country_pos
            model.union.add_agents([firm])
            model.firms.append(firm)
            self._resize_new_firm(firm, sector, equity_size)
            return firm.id

    def _resize_new_firm(self, firm, sector, equity_size):
        citizen_role = self.roles["citizen"]
        producer_role, employer_role = firm.roles["producer"], firm.roles["employer"]
        producer_role.variety = self.model.nprandom.uniform(0, math.radians(360))
        if citizen_role.get_sector_size(sector) <= 1:
            p = self.p
            employer_role.wage = p.initial_wage
            producer_role.phi = p.initial_phi
            producer_role.price = p.initial_wage / p.initial_phi
            firm.expected_sales = p.initial_phi * equity_size / p.initial_wage
        else:
            uniform = self.model.nprandom.uniform
            employer_role.wage = uniform(*citizen_role.get_wage_range(sector))
            producer_role.phi = uniform(*citizen_role.get_phi_range(sector))
            producer_role.price = uniform(*citizen_role.get_price_range(sector))
            firm.expected_sales = uniform(*citizen_role.get_sales_range(sector))

    def _fund_company(self, agent_id, shares):
        for share in shares:
            founder = share["citizen"]
            founder.fund_company(agent_id, share["amount"])

    #
    # Deposits management
    #
    def _choose_deposit_bank(self):
        role = self.roles["depositor"]
        deposits = role.find_deposits()
        for deposit in deposits:
            bank_id = deposit["deposit_bank"].id
            role.leave_deposit_bank(bank_id)
        banks = role.find_deposit_banks()
        selected = banks.select(banks.defaulted == False)
        if len(selected) > 0:
            random = self.model.random
            new_bank = random.choice(selected)
            role.join_deposit_bank(new_bank.id)
            return new_bank.id

    def _make_deposits(self, bank_id):
        cash = self.account["cash"]
        role = self.roles["depositor"]
        role.make_deposits(bank_id, cash)

    def _withdraw_deposits(self, target):
        role = self.roles["depositor"]
        deposits = role.find_deposits()
        for deposit in deposits:
            if target <= 0:
                break
            bank_id = deposit["deposit_bank"].id
            amount = min(target, deposit["amount"])
            role.withdraw_deposits(bank_id, amount)
            target -= amount

    #
    # History
    #
    def update_labor_history(self):
        self.prev_labor_sold = self.roles["worker"].labor_sold
