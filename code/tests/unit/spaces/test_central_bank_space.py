# def test_pay_deposit_interest():

#     bank = BankAgent()
#     bank.deposit_rate = 0.04

#     holder_agent = Mock()
#     holder_agent.deposits = 1000

#     holder_role = Mock()
#     holder_role.agent = holder_agent

#     bank_role = DepositBankRole(bank)

#     bank_role.pay_deposit_interest(holder_role)

#     holder_agent.increase_stocks.assert_called_once_with("deposits", 40)

#     holder_agent.increase_flows.assert_called_once_with("deposit_interest", 40)

#     bank.decrease_stocks.assert_called_once_with("deposits", 40)

#     bank.increase_flows.assert_called_once_with("deposit_interest_paid", 40)
