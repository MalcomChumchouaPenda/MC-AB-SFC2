from .base import EcoRole


class CitizenRole(EcoRole):
    pass


class TaxPayerRole(EcoRole):

    def get_tax_rate(self):
        return self.space.tax_rate


class EmployerRole(EcoRole):

    def __init__(self, owner, space):
        super().__init__(owner, space)
        self.labor_demand = 0

    @property
    def wage_offer(self):
        return self.owner.wage_offer


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
            return self.owner.desired_trad_cons
        return self.owner.desired_non_trad_cons

    def search_suppliers(self, psi):
        return self.space.search_suppliers(psi)

    def get_average_price(self):
        return self.space.average_price

    def buy_goods(self, suppliers):
        cash = self.owner.cash
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
        return self.owner.price

    @property
    def productivity(self):
        return self.owner.productivity

    @property
    def position(self):
        return self.owner.position

    @property
    def available_quantity(self):
        return self.owner.inventories

    def get_average_price(self):
        return self.space.average_price

    def get_average_productivity(self):
        return self.space.average_productivity


class EquityHolderRole(EcoRole):

    def get_default_probability(self):
        return self.space.default_probability


class EquityIssuerRole:
    pass


class DepositHolderRole(EcoRole):

    def get_deposit_rate(self):
        return self.deposit_bank.get_deposit_rate()


class DepositBankRole(EcoRole):

    def get_deposit_rate(self):
        return self.owner.deposit_rate


class BorrowerRole(EcoRole):

    def __init__(self, owner, space):
        super().__init__(owner, space)
        self.loan_demand = 0

    def search_lenders(self):
        return self.space.search_lenders()

    def request_loan(self, lender):
        lender.receive_request(self)


class LenderRole(EcoRole):

    def __init__(self, owner, space):
        super().__init__(owner, space)
        self.loan_applicants = []

    def receive_request(self, applicant):
        self.loan_applicants.append(applicant)
