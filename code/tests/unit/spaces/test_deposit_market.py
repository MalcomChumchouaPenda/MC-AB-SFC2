import pytest
from unittest.mock import Mock
from model.spaces.deposit_market import DepositMarket

# ---------------------------------------------------
# ARCHITECTURE
# ----------------------------------------------------


def test_inherits_from_eco_space():
    # Given
    from model.base import EcoSpace

    # When
    is_derived = issubclass(DepositMarket, EcoSpace)

    # Then
    assert is_derived


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


FakeBank = Mock()
FakeDepositSupplier = Mock()
FakeGuarantee = Mock()


@pytest.fixture
def market_without_roles(monkeypatch, fake_model):
    # Given
    monkeypatch.setattr("model.spaces.deposit_market.DepositDemander", FakeBank)
    monkeypatch.setattr(
        "model.spaces.deposit_market.DepositSupplier", FakeDepositSupplier
    )
    monkeypatch.setattr("model.spaces.deposit_market.DepositGuarantee", FakeGuarantee)
    market = DepositMarket(fake_model)
    market.add_role = Mock()
    return market


def test_add_demander_creates_proper_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_demander(agent)

    # Then
    market.add_role.assert_called_with(FakeBank, agent, "deposit_demander")
    assert role == market.add_role.return_value


def test_add_supplier_creates_proper_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_supplier(agent)

    # Then
    market.add_role.assert_called_with(FakeDepositSupplier, agent, "deposit_supplier")
    assert role == market.add_role.return_value


def test_add_guarantee_add_new_role(market_without_roles):
    # Given
    agent = Mock()
    market = market_without_roles

    # When
    role = market.add_guarantee(agent)

    # Then
    market.add_role.assert_called_with(FakeGuarantee, agent, "deposit_guarantee")
    assert role == market.add_role.return_value


# ---------------------------------------------------
# DEPOSIT MATCHING
# ----------------------------------------------------


@pytest.fixture
def market_with_participants(market_without_roles):
    # Given
    deposit_supplier, deposit_demander = Mock(), Mock()
    market = market_without_roles
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    market.graph.add_nodes_from([deposit_supplier, deposit_demander])
    return market, deposit_supplier, deposit_demander


def test_join_bank_creates_graph_edge(market_with_participants):
    # Given
    market, deposit_supplier, deposit_demander = market_with_participants
    graph = market.graph

    # When
    market.join_bank(deposit_supplier, deposit_demander)

    # Then
    assert graph.has_edge(deposit_supplier, deposit_demander)


def test_join_bank_with_initial_amount(market_with_participants):
    # Given
    market, deposit_supplier, deposit_demander = market_with_participants
    graph = market.graph

    # When
    market.join_bank(deposit_supplier, deposit_demander, amount=500)

    # Then
    assert graph[deposit_supplier][deposit_demander]["amount"] == 500


def test_join_bank_updates_accounts(market_with_participants):
    # Given
    market, deposit_supplier, deposit_demander = market_with_participants

    # When
    market.join_bank(deposit_supplier, deposit_demander, amount=500)

    # Then
    market.transfer_stock.assert_any_call(
        "cash", deposit_supplier.id, deposit_demander.id, 500
    )
    market.transfer_stock.assert_any_call(
        "deposits", deposit_demander.id, deposit_supplier.id, 500
    )


def test_join_bank_registers_deposit_demander_refs(market_with_participants):
    # Given
    market, deposit_supplier, deposit_demander = market_with_participants

    # When
    market.join_bank(deposit_supplier, deposit_demander)

    # Then
    assert deposit_supplier.deposit_demander == deposit_demander
    assert deposit_supplier.bank_id == deposit_demander.id


@pytest.fixture
def market_with_deposit_supplier_amount(market_with_participants):
    # Given
    market, deposit_supplier, deposit_demander = market_with_participants
    market.graph.add_edge(deposit_supplier, deposit_demander, amount=100)
    deposit_supplier.deposit_demander = deposit_demander
    deposit_supplier.bank_id = deposit_demander.id
    return market, deposit_supplier, 100


def test_leave_bank_remove_graph_edge(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, _ = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander
    graph = market.graph

    # When
    market.leave_bank(deposit_supplier)

    # Then
    assert not graph.has_edge(deposit_supplier, deposit_demander)


def test_leave_bank_updates_accounts(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, amount = market_with_deposit_supplier_amount
    bank_id = deposit_supplier.bank_id

    # When
    market.leave_bank(deposit_supplier)

    # Then
    market.transfer_stock.assert_any_call("cash", bank_id, deposit_supplier.id, amount)
    market.transfer_stock.assert_any_call(
        "deposits", deposit_supplier.id, bank_id, amount
    )


def test_leave_bank_change_bank_id(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, _ = market_with_deposit_supplier_amount

    # When
    market.leave_bank(deposit_supplier)

    # Then
    assert deposit_supplier.bank_id is None
    assert deposit_supplier.deposit_demander is None


# ---------------------------------------------------
# MAKE / WITHDRAW DEPOSIT
# ----------------------------------------------------


def test_make_deposits_updates_accounts(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, _ = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander

    # When
    market.make_deposits(deposit_supplier, 500)

    # Then
    market.transfer_stock.assert_any_call(
        "cash", deposit_supplier.id, deposit_demander.id, 500
    )
    market.transfer_stock.assert_any_call(
        "deposits", deposit_demander.id, deposit_supplier.id, 500
    )


def test_make_deposits_transfers_cash(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, amount = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander
    graph = market.graph

    # When
    market.make_deposits(deposit_supplier, 500)

    # Then
    assert graph[deposit_supplier][deposit_demander]["amount"] == amount + 500


def test_withdraw_deposits_updates_accounts(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, _ = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander

    # When
    market.withdraw_deposits(deposit_supplier, 500)

    # Then
    market.transfer_stock.assert_any_call(
        "cash", deposit_demander.id, deposit_supplier.id, 500
    )
    market.transfer_stock.assert_any_call(
        "deposits", deposit_supplier.id, deposit_demander.id, 500
    )


def test_withdraw_deposits_transfers_cash(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, amount = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander
    graph = market.graph

    # When
    market.withdraw_deposits(deposit_supplier, 500)

    # Then
    assert graph[deposit_supplier][deposit_demander]["amount"] == amount - 500


# ---------------------------------------------------
# DEPOSIT REPAYMENT / REIMBURSEMENT
# ----------------------------------------------------


def test_pay_interests_updates_accounts(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, _ = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander

    # When
    market.pay_interests(deposit_demander, deposit_supplier, 10.0)

    # Then
    market.transfer_stock.assert_any_call(
        "deposits", deposit_demander.id, deposit_supplier.id, 10.0
    )
    market.make_transaction.assert_any_call(
        "dep_interests", deposit_demander.id, deposit_supplier.id, 10.0
    )


def test_pay_interests_updates_graph_edge(market_with_deposit_supplier_amount):
    # Given
    market, deposit_supplier, amount = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander
    graph = market.graph

    # When
    market.pay_interests(deposit_demander, deposit_supplier, 10.0)

    # Then
    assert graph[deposit_supplier][deposit_demander]["amount"] == amount + 10.0


def test_reimburse_deposits_updates_accounts(market_with_deposit_supplier_amount):
    # Given
    guarantee = Mock()
    market, deposit_supplier, _ = market_with_deposit_supplier_amount
    deposit_demander = deposit_supplier.deposit_demander

    # When
    market.reimburse_deposits(guarantee, deposit_supplier, 50)

    # Then
    market.transfer_stock.assert_any_call("cash", guarantee.id, deposit_supplier.id, 50)
    market.transfer_stock.assert_any_call(
        "deposits", deposit_supplier.id, deposit_demander.id, 50
    )
