import pytest
from unittest.mock import Mock
from model.spaces.deposit_market import DepositMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.extensions import EcoSpace

    # When
    is_derived = issubclass(DepositMarket, EcoSpace)

    # Then
    assert is_derived


def test_initializes_country_pos(fake_model):
    # Given
    model = fake_model

    # When
    market = DepositMarket(model)

    # Then
    assert market.country_pos == 0


def test_exposes_deposit_rate_as_fraction_of_discount_rate(fake_model):
    # Given
    model = fake_model
    model.p.zeta = 0.6
    market = DepositMarket(model)
    market.env = Mock(discount_rate=0.05)

    # When
    exposed = market.deposit_rate

    # Then
    assert exposed == pytest.approx(0.6 * 0.05)


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeBank = Mock()
FakeDepositor = Mock()
FakeGuarantee = Mock()


@pytest.fixture
def market_without_roles(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.deposit_market.DepositBank", FakeBank)
    monkeypatch.setattr("model.spaces.deposit_market.Depositor", FakeDepositor)
    monkeypatch.setattr("model.spaces.deposit_market.DepositGuarantee", FakeGuarantee)
    market = DepositMarket(fake_model)
    market.add_role = Mock()
    return market


def test_add_bank_add_deposit_bank_role(market_without_roles):
    # Given
    bank = Mock()
    market = market_without_roles

    # When
    market.add_bank(bank)

    # Then
    market.add_role.assert_called_with(FakeBank, bank, "deposit_bank")


def test_add_firm_add_depositor_role(market_without_roles):
    # Given
    firm = Mock()
    market = market_without_roles
    market.country_pos = 2

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(FakeDepositor, firm, "depositor_2")


def test_add_household_add_depositor_role(market_without_roles):
    # Given
    household = Mock()
    market = market_without_roles

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(FakeDepositor, household, "depositor")


def test_add_government_add_guarantee_role(market_without_roles):
    # Given
    govt = Mock()
    market = market_without_roles

    # When
    market.add_government(govt)

    # Then
    market.add_role.assert_called_with(FakeGuarantee, govt, "deposit_guarantee")


# ---------------------------------------------------
# DEPOSIT MATCHING
# ----------------------------------------------------


@pytest.fixture
def market_with_participants(market_without_roles):
    # Given
    depositor, deposit_bank = Mock(), Mock()
    market = market_without_roles
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    market.graph.add_nodes_from([depositor, deposit_bank])
    return market, depositor, deposit_bank


def test_join_deposit_bank_creates_graph_edge(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants
    graph = market.graph

    # When
    market.join_deposit_bank(depositor, deposit_bank)

    # Then
    assert graph.has_edge(depositor, deposit_bank)


def test_join_deposit_bank_with_initial_amount(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants
    graph = market.graph

    # When
    market.join_deposit_bank(depositor, deposit_bank, amount=500)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == 500


def test_join_deposit_bank_updates_accounts(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants
    bank_id = deposit_bank.id

    # When
    market.join_deposit_bank(depositor, deposit_bank, amount=500)

    # Then
    market.transfer_stock.assert_any_call("cash", depositor.id, bank_id, 500)
    market.transfer_stock.assert_any_call("deposits", bank_id, depositor.id, 500)


@pytest.fixture
def market_with_depositor_amount(market_with_participants):
    # Given
    market, depositor, deposit_bank = market_with_participants
    market.graph.add_edge(depositor, deposit_bank, amount=100)
    return market, depositor, deposit_bank, 100


def test_leave_deposit_bank_remove_graph_edge(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, _ = market_with_depositor_amount
    graph = market.graph

    # When
    market.leave_deposit_bank(depositor, deposit_bank)

    # Then
    assert not graph.has_edge(depositor, deposit_bank)


def test_leave_deposit_bank_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, amount = market_with_depositor_amount
    bank_id = deposit_bank.id

    # When
    market.leave_deposit_bank(depositor, deposit_bank)

    # Then
    market.transfer_stock.assert_any_call("cash", bank_id, depositor.id, amount)
    market.transfer_stock.assert_any_call("deposits", depositor.id, bank_id, amount)


# ---------------------------------------------------
# MAKE / WITHDRAW DEPOSIT
# ----------------------------------------------------


def test_make_deposits_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, _ = market_with_depositor_amount
    bank_id = deposit_bank.id

    # When
    market.make_deposits(depositor, deposit_bank, 500)

    # Then
    market.transfer_stock.assert_any_call("cash", depositor.id, bank_id, 500)
    market.transfer_stock.assert_any_call("deposits", bank_id, depositor.id, 500)


def test_make_deposits_transfers_cash(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, amount = market_with_depositor_amount
    graph = market.graph

    # When
    market.make_deposits(depositor, deposit_bank, 500)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == amount + 500


def test_withdraw_deposits_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, _ = market_with_depositor_amount
    bank_id = deposit_bank.id

    # When
    market.withdraw_deposits(depositor, deposit_bank, 500)

    # Then
    market.transfer_stock.assert_any_call("cash", bank_id, depositor.id, 500)
    market.transfer_stock.assert_any_call("deposits", depositor.id, bank_id, 500)


def test_withdraw_deposits_transfers_cash(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, amount = market_with_depositor_amount
    graph = market.graph

    # When
    market.withdraw_deposits(depositor, deposit_bank, 500)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == amount - 500


# ---------------------------------------------------
# DEPOSIT REPAYMENT / REIMBURSEMENT
# ----------------------------------------------------


def test_pay_interests_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, _ = market_with_depositor_amount
    source = deposit_bank.id
    target = depositor.id

    # When
    market.pay_interests(deposit_bank, depositor, 10.0)

    # Then
    market.transfer_stock.assert_any_call("deposits", source, target, 10.0)
    market.make_transaction.assert_any_call("dep_interests", source, target, 10.0)


def test_pay_interests_updates_graph_edge(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, amount = market_with_depositor_amount
    graph = market.graph

    # When
    market.pay_interests(deposit_bank, depositor, 10.0)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == amount + 10.0


def test_reimburse_deposits_updates_accounts(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, _ = market_with_depositor_amount
    bank_id = deposit_bank.id
    guarantee = Mock()

    # When
    market.reimburse_deposits(guarantee, depositor, deposit_bank, 50)

    # Then
    market.transfer_stock.assert_any_call("cash", guarantee.id, depositor.id, 50)
    market.transfer_stock.assert_any_call("deposits", depositor.id, bank_id, 50)
    market.make_transaction.assert_any_call("loan_defaults", guarantee.id, bank_id, 50)


def test_reimburse_deposits_remove_graph_edge(market_with_depositor_amount):
    # Given
    market, depositor, deposit_bank, _ = market_with_depositor_amount
    graph = market.graph
    guarantee = Mock()

    # When
    market.reimburse_deposits(guarantee, depositor, deposit_bank, 50)

    # Then
    assert not graph.has_edge(depositor, deposit_bank)
