import agentpy as ap


class EcoModel(ap.Model):
    """
    Classe de base du modèle économique.

    Responsable de l'orchestration de la simulation.
    """

    def __init__(self, parameters=None, _run_id=None, **kwargs):
        super().__init__(parameters, _run_id, **kwargs)
        self.agents = {}
        self.spaces = {}
"""
1.	Production and R&D investment planning: 
    [firms.plan_production]
    Firms determine their desired production, their labor demand, the price of their output, the wage offered, and  their desired R&D investment. 
2.	Credit markets matching: 
    [firms.request_loans]
    [banks.grant_loans]
    [banks.request_cash_advances]
    Firms interact with banks on the credit market and possibly receive loans. 
    Banks possibly ask cash advances to  the Central Bank to satisfy the mandatory liquidity ratio. 
3.	Labor markets matching: 
    [households.revise_reservation_wage]
    [households.search_jobs]
    Firms interact with workers on the labor market. 
4.	Production, R&D and incomes distribution: 
    [firms.pay_wages]
    [firms.produce]
    [firms.innovate]
    [firms.pay_dividends]
    [banks.update_deposit_rate (Non inclus dans l'article)]
    [banks.pay_deposit_interests (Non inclus dans l'article)]
    [banks.pay_dividends]
    Workers are paid and employed to produce firms' output and to perform R&D. 
    Dividends generated in the previous period are distributed to equity holders, summing up to their current income. 
5.	Tax collection and public expenditures: 
    [households.pay_taxes]
    [firms.pay_taxes]
    [banks.pay_taxes]
    [governments.calc_budget_balance]
    [governments.update_fiscal_policy]
    [governments.issue_bonds]    
    [governments.repay_bonds]  
    [governments.update_bond_rate]
    [governments.update_history]
    Governments calculate revenues from taxes (on past period profits and current period households' income), 
    Governments determine the level of public spending and the tax rate for the next period, 
    Governments repay bonds plus interests to bond holders, 
    Governments determine the quantity of bonds to be issued. 
6.	Bond markets matching: 
    [banks.buy_bonds]
    [central_banks.buy_remaining_bonds]
    Bonds are put on the bond market where commercial banks buy it. 
    The possible residual part is purchased by national Central Banks. 
7.	Goods consumption: 
    [households.calc_consumption]
    [households.consume]
    [governments.pay_public_transfers]
    After having paid taxes and received the tax-exempt monetary transfer from the government, 
    households compute their demand for consumption goods 
    households interact with tradable and non-tradable firms on the correspondent good markets. 
8.	Profit distribution planning: 
    [firms.repay_loans (non inclus dans l'article)]
    [firms.compute_profit_distribution (inclure mise a jour des stats)]
    [firms.update_net_worth]
    [banks.repay_cash_advances (non inclus dans l'article)]
    [banks.compute_profit_distribution (inclure mise a jour des stats)]
    [banks.update_net_worth]
    [central_banks.transfer_profit (non inclus dans l'article)]
    [central_banks.determine_discount_rate (non inclus dans l'article)]
    [central_banks.implement_discount_rate (non inclus dans l'article)]
    Firms and banks compute their profits and update their net worth and shareholders' equity accordingly. 
    Taxes and dividends to be paid in the next period to the government and to equity holders, respectively, are then computed. 
9.	Enter-exit: 
    [households.choose_portfolio_allocation]
    [households.invest_equity (exclure les depots)]
    [households.make_deposits (inclure le choix des banques)]
    [firms.exit]
    [banks.exit]  
    [governments.issue_deposit_guarantee_bonds]
    [central_banks.buy_remaining_bonds]
    [governments.reimburse_deposits]
    Defaulted firms and banks exit the market. 
    Household equity investment takes place and, if enough financial resources are collected, new firms and banks are created.
"""