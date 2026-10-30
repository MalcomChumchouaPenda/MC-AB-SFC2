import numpy as np
from model.extensions import EcoSpace
from model.roles.citizen import Citizen
from model.roles.company import Company
from model.roles.monetary_authority import MonetaryAuthority
from model.roles.fiscal_authority import FiscalAuthority
from model.spaces.goods_market import GoodsMarket
from model.spaces.labor_market import LaborMarket
from model.spaces.deposit_market import DepositMarket
from model.items import Cash


class Country(EcoSpace):

    def setup(self):
        super().setup()
        p = self.p
        self.pos = 0
        self.gdp = 0
        self.inflation = 0
        self.prob_failure = 0
        self.tax_rate = p.initial_tax_rate
        self.discount_rate = p.initial_discount_rate
        self.monetary_authority = None
        self.fiscal_authority = None
        self.cash = {}

    @property
    def average_wage(self):
        return self.spaces["labor_market"].average_wage

    # Spaces management
    def create_markets(self):
        self.add_space(GoodsMarket, "goods_market", tradable=False)
        self.add_space(LaborMarket, "labor_market")
        market = self.add_space(DepositMarket, "deposit_market")
        market.country_pos = self.pos

    #
    # Role management
    #

    def add_central_bank(self, cb):
        if cb.country_pos == self.pos:
            role = self.add_role(MonetaryAuthority, cb)
            self.monetary_authority = role

    def add_government(self, govt):
        if govt.country_pos == self.pos:
            role = self.add_role(FiscalAuthority, govt)
            self.fiscal_authority = role
            self.cash[govt.id] = Cash()

    def add_household(self, household):
        if household.country_pos == self.pos:
            self.add_role(Citizen, household)
            self.cash[household.id] = Cash()

    def add_firm(self, firm):
        if firm.country_pos == self.pos:
            sector = "FT" if firm.tradable else "FNT"
            role = self.add_role(Company, firm)
            role.sector = sector
            self.cash[firm.id] = Cash()

    def add_bank(self, bank):
        if bank.country_pos == self.pos:
            role = self.add_role(Company, bank)
            role.sector = "B"
            self.cash[bank.id] = Cash()

    #
    # Current indicators
    #
    def calc_bank_number_ratio(self):
        bank_sector, firm_sector = self._split_bank_firm_sectors()
        if len(firm_sector) == 0:
            return 1.0
        return len(bank_sector) / len(firm_sector)

    def calc_bank_equity_ratio(self):
        bank_sector, firm_sector = self._split_bank_firm_sectors()
        if len(firm_sector) == 0:
            return 1.0
        return sum(bank_sector.equity) / sum(firm_sector.equity)

    def _split_bank_firm_sectors(self):
        companies = self.find_all_roles("company")
        firm_sector = companies.select(companies.sector != "B")
        bank_sector = companies.select(companies.sector == "B")
        return bank_sector, firm_sector

    def calc_median_firm_size(self):
        companies = self.find_all_roles("company")
        firm_sector = companies.select(companies.sector != "B")
        return float(np.median(firm_sector.equity))

    def calc_sector_size(self, sector):
        companies = self.find_all_roles("company")
        selected = companies.select(companies.sector == sector)
        return len(selected)

    def calc_equity_range(self, sector):
        companies = self.find_all_roles("company")
        selected = companies.select(companies.sector == sector)
        if len(selected) == 0:
            return None
        equities = selected.equity
        return min(equities), max(equities)

    def calc_phi_range(self, sector):
        if sector == "FNT":
            return self.spaces["goods_market"].calc_phi_range()
        return self.env.calc_phi_range()

    def calc_price_range(self, sector):
        if sector == "FNT":
            return self.spaces["goods_market"].calc_price_range()
        return self.env.calc_price_range()

    def calc_sales_range(self, sector):
        if sector == "FNT":
            return self.spaces["goods_market"].calc_sales_range()
        return self.env.calc_sales_range()

    def calc_wage_range(self, sector):
        return self.spaces["labor_market"].calc_wage_range()

    #
    # Cash operations
    #

    def decrease_cash(self, role, amount):
        auth = self.monetary_authority
        if auth is not None and role.id is auth.id:
            return
        if role.country_pos == self.pos:
            self.cash[role.id].amount -= amount
        else:
            self.env.decrease_cash(role, amount)

    def increase_cash(self, role, amount):
        auth = self.monetary_authority
        if auth is not None and role.id is auth.id:
            return
        if role.country_pos == self.pos:
            self.cash[role.id].amount += amount
        else:
            self.env.increase_cash(role, amount)

    #
    # Equity investment
    #

    def fund_company(self, company, founder, amount):
        founder.resid_equity -= amount
        founder.company_number += 1
        if self.graph.has_edge(company, founder):
            self.graph[company][founder]["value"] += amount
        else:
            self.graph.add_edge(company, founder, value=amount)
        self.decrease_cash(founder, amount)
        self.increase_cash(company, amount)
        self.transfer_stock("equities", company.id, founder.id, amount)

    #
    # Dividends and losses
    #

    def update_equity_share(self, company, founder, variation):
        self.transfer_stock("equities", company.id, founder.id, variation)
        self.make_transaction("profit_transfers", company.id, founder.id, variation)
        self.graph[company][founder]["value"] += variation

    def pay_dividends(self, company, founder, amount):
        self.decrease_cash(company, amount)
        self.increase_cash(founder, amount)
        self.make_transaction("dividends", company.id, founder.id, amount)

    def pay_taxes(self, payer, amount):
        auth = self.fiscal_authority
        self.increase_cash(auth, amount)
        self.decrease_cash(payer, amount)
        self.make_transaction("taxes", payer.id, auth.id, amount)

    #
    # Profit transfers
    #
    def transfer_central_bank_profits(self, amount):
        source = self.monetary_authority
        target = self.fiscal_authority
        self.increase_cash(target, amount)
        self.make_transaction("profit_transfers", source.id, target.id, amount)

    #
    # Public transfers
    #
    def pay_public_transfers(self, authority, citizen, amount):
        self.increase_cash(citizen, amount)
        self.decrease_cash(authority, amount)
        self.make_transaction("public_transfers", authority.id, citizen.id, amount)

    #
    # Residual transfers
    #
    def transfer_residual_cash(self, company, founder, amount):
        self.decrease_cash(company, amount)
        self.increase_cash(founder, amount)
        self.transfer_stock("equities", founder.id, company.id, amount)

    #
    # Cash advances
    #
    def request_advances(self, lender, amount):
        cb_id = self.monetary_authority.id
        self.increase_cash(lender, amount)
        self.transfer_stock("advances", lender.id, cb_id, amount)

    def repay_advances(self, lender, principal, interests):
        cb_id = self.monetary_authority.id
        total = principal + interests
        self.decrease_cash(lender, total)
        self.transfer_stock("advances", cb_id, lender.id, principal)
        self.make_transaction("adv_interests", lender.id, cb_id, interests)

    #
    # Evolution
    #
    def update_state(self):
        super().update_state()
        companies = self.find_all_roles("company")
        defaults = companies.select(companies.defaulted == True)
        self.prob_failure = len(defaults) / max(1, len(companies))
        self.inflation = self.spaces["goods_market"].calc_inflation()
        self.gdp = self.spaces["goods_market"].calc_gdp()

    def clear_defaults(self):
        super().clear_defaults()
        companies = self.find_all_roles("company")
        for company in companies.select(companies.defaulted == True):
            for founder in self.neighbors(company):
                founder.company_number -= 1
            self.remove_role(company)
            self.cash.pop(company.id)
