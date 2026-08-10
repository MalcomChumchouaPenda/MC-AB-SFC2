from .base import EcoRole


class TaxPayerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.government = None

    def get_tax_rate(self):
        return self.government.tax_rate

    def pay_taxes(self, amount):
        self.space.pay_taxes(self, amount)


class GovernmentRole(EcoRole):

    @property
    def tax_rate(self):
        return self.agent.tax_rate


class EmployerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.labor_demand = 0

    @property
    def wage_offer(self):
        return self.agent.wage_offer


class WorkerRole(EcoRole):

    def search_employers(self, psi):
        return self.space.search_employers(psi)

    def create_job(self, employer, quantity):
        self.space.create_job(self, employer, quantity)

    def get_labor_sold(self):
        return self.space.get_labor_sold(self)

    def get_unemployment_rate(self):
        return self.space.unemployment_rate


class ConsumerRole(EcoRole):

    @property
    def demand(self):
        if self.space.tradable:
            return self.agent.desired_trad_cons
        return self.agent.desired_non_trad_cons

    def search_suppliers(self, psi):
        return self.space.search_suppliers(psi)

    def get_average_price(self):
        return self.space.average_price

    def buy_goods(self, suppliers):
        cash = self.agent.cash
        demand = self.demand
        market = self.space
        for supplier in suppliers:
            price = supplier.price
            residual = demand / price
            affordable = cash / price
            available = supplier.available_quantity
            quantity = min(residual, available, affordable)
            market.buy_goods(self, supplier, quantity)
            demand -= quantity * price
            cash -= quantity * price
            if demand <= 0 or cash <= 0:
                break


class ProducerRole(EcoRole):

    @property
    def price(self):
        return self.agent.price

    @property
    def productivity(self):
        return self.agent.productivity

    @property
    def position(self):
        return self.agent.position

    @property
    def available_quantity(self):
        return self.agent.inventories

    def get_average_price(self):
        return self.space.average_price

    def get_average_productivity(self):
        return self.space.average_productivity


class EquityHolderRole(EcoRole):

    def get_default_probability(self):
        return self.space.default_probability


class EquityIssuerRole(EcoRole):

    @property
    def net_worth(self):
        return self.agent.net_worth

    def update_equity_holdings(self):
        self.space.update_equity_holdings(self)

    def distribute_dividends(self, amount):
        self.space.distribute_dividends(self, amount)


class DepositHolderRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.deposit_bank = None

    @property
    def deposits(self):
        return self.agent.deposits

    def get_deposit_rate(self):
        return self.deposit_bank.deposit_rate


class DepositBankRole(EcoRole):

    @property
    def deposit_rate(self):
        return self.agent.deposit_rate

    def pay_deposit_interest(self):
        self.space.pay_deposit_interest(self)


class BorrowerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.loan_demand = 0

    @property
    def target_leverage(self):
        agent = self.agent
        return agent.desired_loans / agent.equity

    def search_lenders(self):
        return self.space.search_lenders()

    def request_loan(self, lender):
        lender.receive_request(self)


class LenderRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.loan_applicants = []

    def receive_request(self, applicant):
        self.loan_applicants.append(applicant)

    def grant_loan(self, borrower, amount, rate):
        self.space.grant_loan(self, borrower, amount, rate)


class CentralBankRole(EcoRole):

    @property
    def discount_rate(self):
        return self.agent.discount_rate

    def get_average_inflation(self):
        return self.space.average_inflation


class CommercialBankRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.central_bank = None

    def get_discount_rate(self):
        return self.central_bank.discount_rate

    def request_cash_advances(self, amount):
        self.space.request_cash_advances(self, amount)


class BondIssuerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.bond_supply = 0

    @property
    def interest_rate(self):
        return self.agent.bond_interest_rate

    @property
    def bonds(self):
        return self.agent.bonds

    @property
    def gdp(self):
        return self.agent.gdp


class BondBuyerRole(EcoRole):

    def get_bond_issuers(self):
        return self.space.get_bond_issuers()

    def buy_bonds(self, issuer, amount):
        self.space.buy_bonds(self, issuer, amount)
