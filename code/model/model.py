from agentpy import Model
from agentpy import AgentList, AgentDList, AttrIter
from model.spaces.monetary_union import MonetaryUnion
from model.agents.household import Household
from model.agents.government import Government
from model.agents.central_bank import CentralBank


class EcoModel(Model):
    """
    Classe de base du modèle économique.

    Responsable de l'orchestration de la simulation.
    """

    def setup(self):
        self._create_union()
        self._create_households()
        self._create_governments()
        self._create_central_banks()
        self.firms = AgentDList(self)
        self.banks = AgentDList(self)

    def _create_union(self):
        union = MonetaryUnion(self)
        union.create_countries(self.p.country_number)
        union.create_markets()
        self.union = union

    def _create_households(self):
        p = self.p
        c_num = p.country_number
        h_num = p.household_number
        country_pos = list(range(c_num)) * h_num
        households = AgentList(self, c_num * h_num, Household)
        households.country_pos = AttrIter(country_pos)
        self.union.add_agents(households)
        self.households = households

    def _create_governments(self):
        p = self.p
        c_num = p.country_number
        country_pos = list(range(c_num))
        govts = AgentList(self, c_num, Government)
        govts.country_pos = AttrIter(country_pos)
        self.union.add_agents(govts)
        self.governments = govts

    def _create_central_banks(self):
        self._create_national_cbs()
        self._create_union_cb()

    def _create_national_cbs(self):
        p = self.p
        c_num = p.country_number
        country_pos = list(range(c_num))
        cbs = AgentList(self, c_num, CentralBank)
        cbs.country_pos = AttrIter(country_pos)
        cbs.national = True
        self.union.add_agents(cbs)
        self.national_cbs = cbs

    def _create_union_cb(self):
        cb = CentralBank(self)
        cb.national = False
        self.union_cb = cb
        self.union.add_agents([cb])

    def step(self):
        self._clear_defaults_and_transactions()
        self._production_and_rd_planning()
        self._credit_markets_matching()
        self._labor_markets_matching()
        self._production_and_incomes_distribution()
        self._tax_collection_and_public_expenditures()
        self._bond_markets_matching()
        self._goods_consumption()
        self._profit_distribution_planning()
        self._enter_exit()
        self._update_union_state()

    def _clear_defaults_and_transactions(self):
        self.union.clear_defaults()
        self.union.clear_transactions()
        for group in (self.firms, self.banks):
            defaults = group.select(group.defaulted == True)
            for default in defaults:
                group.remove(default)

    def _production_and_rd_planning(self):
        self.firms.plan_production()
        self.firms.adapt_expectations()
        self.firms.revise_wage_offer()
        self.firms.calc_desired_rd()

    def _credit_markets_matching(self):
        self.firms.request_loans()
        self.banks.grant_loans()
        self.banks.request_cash_advances()

    def _labor_markets_matching(self):
        self.households.revise_reservation_wage()
        self.households.search_jobs()
        self.households.update_labor_history()

    def _production_and_incomes_distribution(self):
        self.firms.pay_wages()
        self.firms.produce_goods()
        self.firms.execute_rd()
        self.firms.pay_dividends()
        self.banks.update_deposit_rate()
        self.banks.pay_deposit_interests()
        self.banks.pay_dividends()

    def _tax_collection_and_public_expenditures(self):
        self.households.pay_taxes()
        self.firms.pay_taxes()
        self.banks.pay_taxes()
        self.governments.calc_budget_balance()
        self.governments.update_fiscal_policy()
        self.governments.repay_bonds()
        self.governments.issue_bonds()
        self.governments.update_bond_rate()
        self.governments.update_budget_history()

    def _bond_markets_matching(self):
        self.banks.buy_bonds()
        self.national_cbs.buy_bonds()

    def _goods_consumption(self):
        self.governments.pay_public_transfers()
        self.households.calc_consumption()
        self.households.consume()

    def _profit_distribution_planning(self):
        self.firms.repay_loans()
        self.firms.compute_profit_distribution()
        self.firms.update_net_worth()
        self.firms.update_production_history()
        self.banks.repay_cash_advances()
        self.banks.compute_profit_distribution()
        self.banks.update_net_worth()
        self.national_cbs.transfer_profit()
        self.union_cb.update_discount_rate()
        self.national_cbs.implement_discount_rate()

    def _enter_exit(self):
        self.households.choose_portfolio_allocation()
        self.households.invest_equity()
        self.households.choose_deposit_bank()
        self.households.make_deposits()
        self.firms.exit()
        self.banks.exit()
        self.governments.issue_deposit_guarantee_bonds()
        self.national_cbs.buy_bonds()
        self.governments.reimburse_deposits()

    def _update_union_state(self):
        self.union.update_state()
