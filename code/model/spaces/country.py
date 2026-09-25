from agentpy import AgentDList, AgentList
from model.base import EcoSpace
from model.roles.citizen import Citizen
from model.roles.company import Company
from model.roles.monetary_authority import MonetaryAuthority
from model.roles.fiscal_authority import FiscalAuthority
from model.spaces.good_market import GoodsMarket
from model.spaces.labor_market import LaborMarket
from model.spaces.deposit_market import DepositMarket


class Country(EcoSpace):

    def setup(self):
        super().setup()
        self.gdp = 0
        self.inflation = 0
        self.prob_failure = 0
        self.tax_rate = 0
        self.monetary_authority = None
        self.fiscal_authority = None
        self.add_space(GoodsMarket, "good_market", tradable=False)
        self.add_space(LaborMarket, "labor_market")
        self.add_space(DepositMarket, "deposit_market")

    #
    # Role management
    #
    def add_monetary_authority(self, agent):
        role = self.add_role(MonetaryAuthority, agent, "monetary_authority")
        self.monetary_authority = role
        return role

    def add_fiscal_authority(self, agent):
        role = self.add_role(FiscalAuthority, agent, "fiscal_authority")
        agent.cb_id = self.monetary_authority.id
        self.fiscal_authority = role
        return role

    def add_citizen(self, agent):
        role = self.add_role(Citizen, agent, "citizen")
        agent.cb_id = self.monetary_authority.id
        return role

    def add_company(self, agent, sector):
        agent.cb_id = self.monetary_authority.id
        role = self.add_role(Company, agent, "company")
        role.sector = sector
        return role

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
        firm_sector = AgentDList(self.model)
        bank_sector = AgentDList(self.model)
        for company in self.roles["company"]:
            if company.sector == "B":
                bank_sector.append(company)
            else:
                firm_sector.append(company)
        return bank_sector, firm_sector

    def calc_sector_equity_range(self, sector):
        equities = [c.equity for c in self.roles["company"] if c.sector == sector]
        if len(equities) == 0:
            return None
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
        self.record_flow("profit_transfers", company.id, founder.id, variation)
        self.graph[company][founder]["value"] += variation

    def pay_dividends(self, company, founder, amount):
        self.transfer_stock("cash", company.id, founder.id, amount)
        self.record_flow("dividends", company.id, founder.id, amount)

    def pay_taxes(self, payer, amount):
        auth_id = self.fiscal_authority.id
        self.transfer_stock("cash", payer.id, auth_id, amount)
        self.record_flow("taxes", payer.id, auth_id, amount)

    #
    # Firm creation
    #
    def create_firm(self, firm, shares, tradable):
        sector = "FT" if tradable else "FNT"
        company = self.add_company(firm, sector=sector)
        self._place_firm(firm, tradable)
        for share in shares:
            founder = share["founder"]
            amount = share["amount"]
            self.fund_company(company, founder, amount)

    def _place_firm(self, firm, tradable):
        self.env.place_firm(firm, tradable=tradable)
        self.spaces["deposit_market"].add_depositor(firm)
        self.spaces["labor_market"].add_employer(firm)
        if not tradable:
            self.spaces["good_market"].add_producer(firm)

    #
    # Bank creation
    #
    def create_bank(self, bank, shares):
        company = self.add_company(bank, sector="B")
        for share in shares:
            founder = share["founder"]
            amount = share["amount"]
            self.fund_company(company, founder, amount)
        self.env.place_bank(bank)
        self.spaces["deposit_market"].add_deposit_bank(bank)

    #
    # Profit transfers
    #
    def transfer_central_bank_profits(self, amount):
        source = self.monetary_authority.id
        target = self.fiscal_authority.id
        self.transfer_stock("cash", source, target, amount)
        self.record_flow("profit_transfers", source, target, amount)

    #
    # Public transfers
    #
    def pay_public_transfers(self, authority, citizen, amount):
        self.transfer_stock("cash", authority.id, citizen.id, amount)
        self.record_flow("public_transfers", authority.id, citizen.id, amount)

    #
    # Residual transfers
    #
    def transfer_residual_cash(self, company, founder, amount):
        self.transfer_stock("cash", company.id, founder.id, amount)
        self.transfer_stock("equities", founder.id, company.id, amount)

    #
    # Evolution
    #
    def update_state(self):
        companies = AgentList(self.model, self.roles["company"])
        defaults = companies.select(companies.defaulted == True)
        self.prob_failure = len(defaults) / max(1, len(companies))
        self.inflation = self.spaces["good_market"].calc_inflation()
        self.gdp = self.spaces["good_market"].calc_gdp()
