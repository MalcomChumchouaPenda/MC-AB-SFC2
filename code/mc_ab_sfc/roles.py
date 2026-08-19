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

    def get_gdp(self):
        return self.space.gdp

    def get_average_price(self):
        return self.space.average_price

    def get_average_productivity(self):
        return self.space.average_productivity

    def get_discount_rate(self):
        return self.space.discount_rate

    def get_households(self):
        return self.space.get_households()

    def pay_public_transfers(self, household, transfers):
        self.space.pay_public_transfers(self, household, transfers)


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

    @property
    def equity(self):
        return self.agent.equity

    @property
    def desired_equity(self):
        return self.agent.desired_equity

    def get_default_probability(self):
        return self.space.default_probability

    def get_potential_investors(self):
        return self.space.get_potential_investors(exclude=self)

    def get_bank_firm_number_ratio(self):
        country = self.space
        return len(country.bank_roles) / max(1, len(country.firm_roles))

    def get_bank_firm_equity_ratio(self):
        country = self.space
        firm_equities = sum([r.equity for r in country.firm_roles])
        bank_equities = sum([r.equity for r in country.bank_roles])
        return bank_equities / max(1, firm_equities)

    def get_sector_equity_range(self, sector):
        country = self.space
        if sector == "banks" and len(country.bank_roles) > 0:
            equities = [r.equity for r in country.bank_roles]
            return min(equities), max(equities)
        elif len(country.firm_roles) > 0:
            firms = [r.agent for r in country.firm_roles]
            if sector == "tradable_firms":
                equities = [f.equity for f in firms if f.tradable]
            else:
                equities = [f.equity for f in firms if not f.tradable]
            return min(equities), max(equities)


class EquityIssuerRole(EcoRole):

    @property
    def equity(self):
        return self.agent.equity

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

    @property
    def defaulted(self):
        return self.agent.defaulted

    @property
    def defaulted_deposits(self):
        if not self.agent.defaulted:
            return 0
        return self.agent.deposits

    def pay_deposit_interest(self):
        self.space.pay_deposit_interest(self)


class DepositGuaranteeRole(EcoRole):

    def get_defaulted_banks(self):
        return self.space.get_defaulted_banks()

    def reimburse_deposits(self, bank):
        self.space.reimburse_deposits(self, bank)


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


class UnionCentralBankRole(EcoRole):

    @property
    def discount_rate(self):
        return self.space.discount_rate

    @discount_rate.setter
    def discount_rate(self, rate):
        self.space.discount_rate = rate

    def get_average_inflation(self):
        return self.space.average_inflation


class NationalCentralBankRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.government = None

    @property
    def discount_rate(self):
        return self.space.discount_rate

    def get_average_inflation(self):
        return self.space.average_inflation

    def transfer_profit(self, amount):
        self.space.transfer_profit(self, amount)


class CommercialBankRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.central_bank = None

    def get_discount_rate(self):
        return self.space.discount_rate

    def request_cash_advances(self, amount):
        self.space.request_cash_advances(self, amount)


class BondIssuerRole(EcoRole):

    def __init__(self, agent, space):
        super().__init__(agent, space)
        self.bond_supply = 0

    @property
    def bond_rate(self):
        return self.agent.bond_rate

    @property
    def bonds(self):
        return self.agent.bonds

    @property
    def gdp(self):
        return self.agent.gdp

    def issue_bonds(self, amount):
        self.bond_supply = amount

    def pay_bond_debt(self):
        self.space.pay_bond_debt(self)


class BondBuyerRole(EcoRole):

    def get_bond_issuers(self):
        return self.space.get_bond_issuers()

    def buy_bonds(self, issuer, amount):
        self.space.buy_bonds(self, issuer, amount)
