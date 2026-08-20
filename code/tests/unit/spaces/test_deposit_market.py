import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces.deposit_market import DepositMarket

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(DepositMarket, EcoSpace)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


class FakeRole:
    pass


@pytest.fixture
def market():
    # Given
    model = Mock()
    market = DepositMarket(model)
    return market


def test_add_deposit_holder_creates_deposit_holder_role(market, monkeypatch):
    # Given
    household = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.deposit_market.DepositHolderRole", FakeRole)

    # When
    deposit_holder = market.add_deposit_holder(household)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, household, "deposit_holder")
    assert deposit_holder is action.return_value


def test_add_deposit_bank_creates_deposit_bank(market, monkeypatch):
    # Given
    bank = Mock()
    market.add_role = Mock()
    monkeypatch.setattr("mc_ab_sfc.spaces.deposit_market.DepositBankRole", FakeRole)

    # When
    deposit_bank = market.add_deposit_bank(bank)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, bank, "deposit_bank")
    assert deposit_bank is action.return_value


def test_add_deposit_guarantee_creates_deposit_guarantee(market, monkeypatch):
    # Given
    bank = Mock()
    market.add_role = Mock()
    monkeypatch.setattr(
        "mc_ab_sfc.spaces.deposit_market.DepositGuaranteeRole", FakeRole
    )

    # When
    deposit_guarantee = market.add_deposit_guarantee(bank)

    # Then
    action = market.add_role
    action.assert_called_with(FakeRole, bank, "deposit_guarantee")
    assert deposit_guarantee is action.return_value


def test_assign_deposit_bank_add_edge(market):
    # Given
    deposit_holder = Mock()
    deposit_bank = Mock()
    graph = market.graph
    graph.add_nodes_from([deposit_holder, deposit_bank])

    # When
    market.assign_deposit_bank(deposit_holder, deposit_bank)

    # Then
    assert len(graph.edges) == 1
    assert graph.has_edge(deposit_bank, deposit_holder)
    assert deposit_holder.deposit_bank is deposit_bank


def test_pays_interest_to_all_clients(market):
    # Given
    bank = Mock(deposit_rate=0.04)
    graph = market.graph
    graph.add_node(bank)
    holders = [Mock(deposits=1000 * (i + 1)) for i in range(3)]
    for holder in holders:
        graph.add_node(holder)
        graph.add_edge(bank, holder)

    # When
    market.pay_deposit_interest(bank)

    # Then
    for i, holder in enumerate(holders):
        amount = pytest.approx(40.0 * (i + 1))
        bank.increase_stock.assert_any_call("deposits", amount)
        bank.increase_flow.assert_any_call("deposit_interest", amount)
        holder.increase_stock.assert_called_with("deposits", amount)
        holder.increase_flow.assert_called_with("deposit_interest", amount)


class FakeBankRole(Mock):
    pass


def test_get_defaulted_banks(market, monkeypatch):
    # Given
    others = [Mock() for _ in range(5)]
    banks = [FakeBankRole(defaulted=False) for _ in range(2)]
    defaults = [FakeBankRole(defaulted=True) for _ in range(5)]
    market.graph.add_nodes_from(others + banks + defaults)
    monkeypatch.setattr("mc_ab_sfc.spaces.deposit_market.DepositBankRole", FakeBankRole)

    # When
    sample = market.get_defaulted_banks()

    # Then
    assert sample == defaults


def test_reimburse_deposits_to_all_clients(market):
    # Given
    guarantee = Mock()
    bank = Mock()
    graph = market.graph
    graph.add_node(bank)
    holders = [Mock(deposits=100 * i) for i in range(3)]
    for holder in holders:
        graph.add_node(holder)
        graph.add_edge(bank, holder)

    # When
    market.reimburse_deposits(guarantee, bank)

    # Then
    for i, holder in enumerate(holders):
        amount = pytest.approx(100 * i)
        bank.decrease_stock.assert_any_call("deposits", amount)
        guarantee.decrease_stock.assert_any_call("reserves", amount)
        holder.decrease_stock.assert_called_with("deposits", amount)
        holder.increase_stock.assert_called_with("cash", amount)


def test_make_deposits(market):
    # Given
    bank = Mock()
    holder = Mock()

    # When
    market.make_deposits(holder, bank, 500)

    # Then
    bank.increase_stock.assert_any_call("deposits", 500)
    bank.increase_stock.assert_any_call("reserves", 500)
    holder.increase_stock.assert_called_with("deposits", 500)
    holder.decrease_stock.assert_called_with("cash", 500)
