import pytest
from unittest.mock import Mock
from agentpy import AgentDList
from model.spaces.deposit_market import DepositMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from model.base import EcoSpace

    # Assert
    assert issubclass(DepositMarket, EcoSpace)


@pytest.fixture
def market_before_setup():
    # Given
    model = Mock()
    market = DepositMarket(model)
    return market


# ---------------------------------------------------
# ROLES
# ----------------------------------------------------


def test_has_deposit_banks_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.deposit_banks, AgentDList)


def test_has_depositors_list(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert isinstance(market.depositors, AgentDList)


def test_has_deposit_guarantee_ref(market_before_setup):
    # Given
    market = market_before_setup

    # When
    market.setup()

    # Then
    assert market.deposit_guarantee is None


class FakeBank(Mock):
    pass


@pytest.fixture
def market_without_deposit_banks(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.deposit_market.DepositBank", FakeBank)
    market = market_before_setup
    market.add_role = Mock()
    market.deposit_banks = []
    return market


def test_add_deposit_bank_add_appropriate_role(market_without_deposit_banks):
    # Given
    agent = Mock()
    market = market_without_deposit_banks

    # When
    role = market.add_deposit_bank(agent)

    # Then
    market.add_role.assert_called_with(FakeBank, agent, "deposit_bank")
    assert role == market.add_role.return_value


def test_add_deposit_bank_registers_deposit_bank(market_without_deposit_banks):
    # Given
    agent = Mock()
    market = market_without_deposit_banks

    # When
    role = market.add_deposit_bank(agent)

    # Then
    assert market.deposit_banks == [role]


class FakeDepositor(Mock):
    pass


@pytest.fixture
def market_without_depositors(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.deposit_market.Depositor", FakeDepositor)
    market = market_before_setup
    market.add_role = Mock()
    market.depositors = []
    return market


def test_add_depositor_add_appropriate_role(market_without_depositors):
    # Given
    agent = Mock()
    market = market_without_depositors

    # When
    role = market.add_depositor(agent)

    # Then
    market.add_role.assert_called_with(FakeDepositor, agent, "depositor")
    assert role == market.add_role.return_value


def test_add_depositor_registers_depositor(market_without_depositors):
    # Given
    agent = Mock()
    market = market_without_depositors

    # When
    role = market.add_depositor(agent)

    # Then
    assert market.depositors == [role]


class FakeGuarantee(Mock):
    pass


@pytest.fixture
def market_without_dep_guarantee(monkeypatch, market_before_setup):
    # Given
    monkeypatch.setattr("model.spaces.deposit_market.DepositGuarantee", FakeGuarantee)
    market = market_before_setup
    market.add_role = Mock()
    market.deposit_guarantee = None
    return market


def test_add_deposit_guarantee_add_new_role(market_without_dep_guarantee):
    # Given
    agent = Mock()
    market = market_without_dep_guarantee

    # When
    role = market.add_deposit_guarantee(agent)

    # Then
    market.add_role.assert_called_with(FakeGuarantee, agent, "deposit_guarantee")
    assert role == market.add_role.return_value


def test_add_deposit_guarantee_registers_role(market_without_dep_guarantee):
    # Given
    agent = Mock()
    market = market_without_dep_guarantee

    # When
    role = market.add_deposit_guarantee(agent)

    # Then
    assert market.deposit_guarantee == role


# ---------------------------------------------------
# DEPOSIT MATCHING
# ----------------------------------------------------


def test_find_deposit_banks(market_before_setup, make_dlist):
    # Given
    deposit_bank = Mock()
    market = market_before_setup
    market.deposit_banks = make_dlist([deposit_bank])

    # When
    sample = market.find_deposit_banks()

    # Then
    assert sample == [deposit_bank]


@pytest.fixture
def market_with_participants(market_before_setup):
    # Given
    depositor, deposit_bank = Mock(), Mock()
    market = market_before_setup
    market.graph.add_nodes_from([depositor, deposit_bank])
    return market, depositor, deposit_bank


def test_link_depositor_creates_graph_edge(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants
    graph = market.graph

    # When
    market.link_depositor_to_bank(depositor, deposit_bank)

    # Then
    assert graph.has_edge(depositor, deposit_bank)


def test_link_depositor_with_initial_amount(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants
    graph = market.graph

    # When
    market.link_depositor_to_bank(depositor, deposit_bank, amount=500)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == 500


def test_link_depositor_updates_accounts(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants

    # When
    market.link_depositor_to_bank(depositor, deposit_bank, amount=500)

    # Then
    depositor.account.debit_stock.assert_any_call("cash", 500)
    depositor.account.credit_stock.assert_any_call("deposits", 500)
    deposit_bank.account.credit_stock.assert_any_call("cash", 500)
    deposit_bank.account.debit_stock.assert_any_call("deposits", 500)


def test_link_depositor_registers_deposit_bank_refs(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants

    # When
    market.link_depositor_to_bank(depositor, deposit_bank)

    # Then
    assert depositor.deposit_bank == deposit_bank
    assert depositor.bank_account == deposit_bank.account


@pytest.fixture
def market_with_depositor_amount(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants
    market.graph.add_edge(depositor, deposit_bank, amount=100)
    depositor.deposit_bank = deposit_bank
    depositor.bank_account = Mock()
    return market, depositor, 100


def test_unlink_depositor_remove_graph_edge(market_with_depositor_amount):
    # Given
    market, depositor, _ = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank
    graph = market.graph

    # When
    market.unlink_depositor_with_bank(depositor)

    # Then
    assert not graph.has_edge(depositor, deposit_bank)


def test_unlink_depositor_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, amount = market_with_depositor_amount
    bank_account = depositor.bank_account

    # When
    market.unlink_depositor_with_bank(depositor)

    # Then
    depositor.account.credit_stock.assert_any_call("cash", amount)
    depositor.account.debit_stock.assert_any_call("deposits", amount)
    bank_account.debit_stock.assert_any_call("cash", amount)
    bank_account.credit_stock.assert_any_call("deposits", amount)


def test_unlink_depositor_change_bank_account_ref(market_with_depositor_amount):
    # Given
    market, depositor, _ = market_with_depositor_amount

    # When
    market.unlink_depositor_with_bank(depositor)

    # Then
    assert depositor.bank_account is None
    assert depositor.deposit_bank is None


# ---------------------------------------------------
# MAKE / WITHDRAW DEPOSIT
# ----------------------------------------------------


def test_make_deposits_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, _ = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank

    # When
    market.make_deposits(depositor, 500)

    # Then
    depositor.account.debit_stock.assert_any_call("cash", 500)
    depositor.account.credit_stock.assert_any_call("deposits", 500)
    deposit_bank.credit_stock.assert_any_call("cash", 500)
    deposit_bank.debit_stock.assert_any_call("deposits", 500)


def test_make_deposits_transfers_cash(market_with_depositor_amount):
    # Given
    market, depositor, amount = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank
    graph = market.graph

    # When
    market.make_deposits(depositor, 500)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == amount + 500


def test_withdraw_deposits_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, _ = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank

    # When
    market.withdraw_deposits(depositor, 500)

    # Then
    depositor.account.credit_stock.assert_any_call("cash", 500)
    depositor.account.debit_stock.assert_any_call("deposits", 500)
    deposit_bank.debit_stock.assert_any_call("cash", 500)
    deposit_bank.credit_stock.assert_any_call("deposits", 500)


def test_withdraw_deposits_transfers_cash(market_with_depositor_amount):
    # Given
    market, depositor, amount = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank
    graph = market.graph

    # When
    market.withdraw_deposits(depositor, 500)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == amount - 500


# ---------------------------------------------------
# DEPOSIT REPAYMENT / REIMBURSEMENT
# ----------------------------------------------------


def test_find_deposit_accounts(market_with_participants):
    # Given
    other = Mock()
    market, depositor, deposit_bank = market_with_participants
    market.graph.add_edge(deposit_bank, depositor, amount=100)
    market.graph.add_edge(other, depositor, amount=200)

    # When
    deposit_accounts = market.find_deposit_accounts(deposit_bank)

    # Then
    assert deposit_accounts == [{"depositor": depositor, "amount": 100}]


def test_find_defaulted_banks(market_before_setup, make_dlist):
    # Given
    deposit_bank1 = Mock(defaulted=True)
    deposit_bank2 = Mock(defaulted=False)
    market = market_before_setup
    market.deposit_banks = make_dlist([deposit_bank1, deposit_bank2])

    # When
    sample = market.find_defaulted_banks()

    # Then
    assert sample == [deposit_bank1]


def test_pay_interests_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, _ = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank

    # When
    market.pay_interests(deposit_bank, depositor, 10.0)

    # Then
    depositor.account.credit_stock.assert_any_call("deposits", 10.0)
    depositor.account.credit_flow.assert_any_call("dep_interests", 10.0)
    deposit_bank.debit_stock.assert_any_call("deposits", 10.0)
    deposit_bank.debit_flow.assert_any_call("dep_interests", 10.0)


def test_pay_interests_updates_graph_edge(market_with_depositor_amount):
    # Given
    market, depositor, amount = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank
    graph = market.graph

    # When
    market.pay_interests(deposit_bank, depositor, 10.0)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == amount + 10.0


def test_reimburse_deposits_updates_accounts(market_with_depositor_amount):
    # Given
    guarantee = Mock()
    market, depositor, _ = market_with_depositor_amount
    deposit_bank = depositor.deposit_bank

    # When
    market.reimburse_deposits(guarantee, depositor, 50)

    # Then
    depositor.account.credit_stock.assert_any_call("cash", 50)
    depositor.account.debit_stock.assert_any_call("deposits", 50)
    deposit_bank.credit_stock.assert_any_call("deposits", 50)
    guarantee.account.debit_stock.assert_any_call("cash", 50)
