from model.base import EcoSpace
from model.roles.citizen import Citizen
from model.roles.company import Company
from model.roles.monetary_authority import MonetaryAuthority
from model.roles.fiscal_authority import FiscalAuthority
from model.spaces.goods_market import GoodsMarket
from model.spaces.labor_market import LaborMarket
from model.spaces.deposit_market import DepositMarket


class Country(EcoSpace):

    def setup(self):
        super().setup()
        self.pos = 0
        self.gdp = 0
        self.inflation = 0
        self.prob_failure = 0
        self.tax_rate = 0
        self.monetary_authority = None
        self.fiscal_authority = None

    # Spaces management
    def create_markets(self):
        self.add_space(GoodsMarket, "goods_market", tradable=False)
        self.add_space(LaborMarket, "labor_market")
        market = self.add_space(DepositMarket, "deposit_market")
        market.country_pos = self.pos

    #
    # Role management
    #
    def place_household(self, household):
        self.add_role(Citizen, household, "citizen")
        self.spaces["goods_market"].place_household(household)
        self.spaces["labor_market"].place_household(household)
        self.spaces["deposit_market"].place_household(household)

    def place_firm(self, firm):
        if firm.country_pos == self.id:
            self.spaces["labor_market"].place_firm(firm)
        if firm.tradable:
            self._add_company(firm, "FT")
        else:
            self._add_company(firm, "FNT")
            self.spaces["goods_market"].place_firm(firm)
        self.spaces["deposit_market"].place_firm(firm)

    def place_bank(self, bank):
        self._add_company(bank, "B")
        self.spaces["deposit_market"].place_bank(bank)

    def _add_company(self, agent, sector):
        role = self.add_role(Company, agent, "company")
        role.sector = sector

    def place_government(self, govt):
        role = self.add_role(FiscalAuthority, govt, "fiscal_authority")
        self.fiscal_authority = role
        self.spaces["deposit_market"].place_government(govt)

    def place_central_bank(self, cb):
        role = self.add_role(MonetaryAuthority, cb, "monetary_authority")
        self.monetary_authority = role

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

    def calc_sector_equity_range(self, sector):
        companies = self.find_all_roles("company")
        selected = companies.select(companies.sector == sector)
        if len(selected) == 0:
            return None
        equities = selected.equity
        return min(equities), max(equities)

    #
    # Equity investment
    #

    def fund_company(self, company, founder, amount):
        founder.resid_equity -= amount
        if self.graph.has_edge(company, founder):
            self.graph[company][founder]["value"] += amount
        else:
            self.graph.add_edge(company, founder, value=amount)

        self.transfer_stock("cash", founder.id, company.id, amount)
        self.transfer_stock("equities", company.id, founder.id, amount)

    #
    # Dividends and losses
    #

    def update_equity_share(self, company, founder, variation):
        self.transfer_stock("equities", company.id, founder.id, variation)
        self.make_transaction("profit_transfers", company.id, founder.id, variation)
        self.graph[company][founder]["value"] += variation

    def pay_dividends(self, company, founder, amount):
        self.transfer_stock("cash", company.id, founder.id, amount)
        self.make_transaction("dividends", company.id, founder.id, amount)

    def pay_taxes(self, payer, amount):
        auth_id = self.fiscal_authority.id
        self.transfer_stock("cash", payer.id, auth_id, amount)
        self.make_transaction("taxes", payer.id, auth_id, amount)

    #
    # Profit transfers
    #
    def transfer_central_bank_profits(self, amount):
        source = self.monetary_authority.id
        target = self.fiscal_authority.id
        self.transfer_stock("cash", source, target, amount)
        self.make_transaction("profit_transfers", source, target, amount)

    #
    # Public transfers
    #
    def pay_public_transfers(self, authority, citizen, amount):
        self.transfer_stock("cash", authority.id, citizen.id, amount)
        self.make_transaction("public_transfers", authority.id, citizen.id, amount)

    #
    # Residual transfers
    #
    def transfer_residual_cash(self, company, founder, amount):
        self.transfer_stock("cash", company.id, founder.id, amount)
        self.transfer_stock("equities", founder.id, company.id, amount)

    #
    # Cash advances
    #
    def request_advances(self, lender, amount):
        cb_id = self.monetary_authority.id
        self.transfer_stock("cash", cb_id, lender.id, amount)
        self.transfer_stock("advances", lender.id, cb_id, amount)

    def repay_advances(self, lender, principal, interests):
        cb_id = self.monetary_authority.id
        total = principal + interests
        self.transfer_stock("cash", lender.id, cb_id, total)
        self.transfer_stock("advances", cb_id, lender.id, principal)
        self.make_transaction("adv_interests", lender.id, cb_id, interests)

    #
    # Evolution
    #
    def update_state(self):
        companies = self.find_all_roles("company")
        defaults = companies.select(companies.defaulted == True)
        self.prob_failure = len(defaults) / max(1, len(companies))
        self.inflation = self.spaces["goods_market"].calc_inflation()
        self.gdp = self.spaces["goods_market"].calc_gdp()
