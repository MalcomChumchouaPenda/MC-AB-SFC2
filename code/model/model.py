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
        num1 = p.country_number
        num2 = p.household_number
        pos = list(range(num1)) * num2
        households = AgentList(self, num1 * num2, Household)
        households.country_pos = AttrIter(pos)
        self.union.add_agents(households)
        self.households = households

    def _create_governments(self):
        p = self.p
        num = p.country_number
        pos = list(range(num))
        govts = AgentList(self, num, Government)
        govts.country_pos = AttrIter(pos)
        self.union.add_agents(govts)
        self.governments = govts

    def _create_central_banks(self):
        p = self.p
        num = p.country_number
        pos = list(range(num))
        national_cbs = AgentList(self, num, CentralBank)
        national_cbs.country_pos = AttrIter(pos)
        national_cbs.national = True
        union_cb = CentralBank(self)
        union_cb.national = False
        self.union.add_agents(national_cbs)
        self.union.add_agents([union_cb])
        self.union_central_bank = union_cb
        self.national_central_banks = national_cbs

    def step(self):
        self._production_and_rd_planning()
        self._credit_markets_matching()
        self._labor_markets_matching()
        self._production_and_incomes_distribution()
        self._tax_collection_and_public_expenditures()
        self._bond_markets_matching()
        self._goods_consumption()
        self._profit_distribution_planning()
        self._enter_exit()

    def _production_and_rd_planning(self):
        self.firms.plan_production()
        self.firms.adapt_expectations()
        self.firms.revise_wage_offer()

    def _credit_markets_matching(self):
        self.firms.request_loans()
        self.banks.grant_loans()
        self.banks.request_cash_advances()

    def _labor_markets_matching(self):
        self.households.revise_reservation_wage()
        self.households.search_jobs()

    def _production_and_incomes_distribution(self):
        self.firms.pay_wages()
        self.firms.produce_goods()
        self.firms.update_productivity()
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
        self.governments.update_history()

    def _bond_markets_matching(self):
        self.banks.buy_bonds()
        self.national_central_banks.buy_bonds()

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
        self.national_central_banks.transfer_profit()
        self.union_central_bank.update_discount_rate()
        self.national_central_banks.implement_discount_rate()

    def _enter_exit(self):
        self.households.choose_portfolio_allocation()
        self.households.invest_equity()
        self.households.make_deposits()
        self.firms.exit()
        self.banks.exit()
        self.governments.issue_deposit_guarantee_bonds()
        self.national_central_banks.buy_remaining_bonds()
        self.governments.reimburse_deposits()
