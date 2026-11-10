import pytest
from unittest.mock import Mock, call
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


@pytest.fixture
def market(fake_model):
    # Given
    return DepositMarket(fake_model)


def test_exposes_deposit_rate_as_fraction_of_discount_rate(market):
    # Given
    market.p.zeta = 0.6
    market.env = Mock(discount_rate=0.05)

    # When
    exposed = market.deposit_rate

    # Then
    assert exposed == pytest.approx(0.6 * 0.05)


def test_exposes_country_pos_from_env(market):
    # Given
    market.env = Mock(pos=3)

    # When
    exposed = market.country_pos

    # Then
    assert exposed == 3


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


@pytest.fixture
def market_without_roles(market):
    # Given
    market.add_role = Mock()
    market.env = Mock()
    return market


def test_add_bank_add_deposit_bank_role_if_domestic(market_without_roles, monkeypatch):
    # Given
    bank = Mock(country_pos=2)
    role_cls = Mock(name="DepositBank")
    monkeypatch.setattr("model.spaces.deposit_market.DepositBank", role_cls)
    market = market_without_roles
    market.env.pos = 2

    # When
    market.add_bank(bank)

    # Then
    market.add_role.assert_called_with(role_cls, bank)


def test_add_bank_doesnt_add_role_for_foreigners(market_without_roles):
    # Given
    bank = Mock(country_pos=2)
    market = market_without_roles
    market.env.pos = 1

    # When
    market.add_bank(bank)

    # Then
    market.add_role.assert_not_called()


def test_add_firm_add_depositor_role(market_without_roles, monkeypatch):
    # Given
    firm = Mock()
    role_cls = Mock(name="Depositor")
    monkeypatch.setattr("model.spaces.deposit_market.Depositor", role_cls)
    market = market_without_roles
    market.env.pos = 2

    # When
    market.add_firm(firm)

    # Then
    market.add_role.assert_called_with(role_cls, firm, prefix="country_2")


def test_add_household_add_depositor_if_domestic(market_without_roles, monkeypatch):
    # Given
    household = Mock(country_pos=2)
    role_cls = Mock(name="Depositor")
    monkeypatch.setattr("model.spaces.deposit_market.Depositor", role_cls)
    market = market_without_roles
    market.env.pos = 2

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_called_with(role_cls, household)


def test_add_household_doesnt_add_role_for_foreigners(market_without_roles):
    # Given
    household = Mock(country_pos=2)
    market = market_without_roles
    market.env.pos = 1

    # When
    market.add_household(household)

    # Then
    market.add_role.assert_not_called()


def test_add_government_add_guarantee_if_domestic(market_without_roles, monkeypatch):
    # Given
    govt = Mock(country_pos=2)
    role_cls = Mock(name="DepositGuarantee")
    monkeypatch.setattr("model.spaces.deposit_market.DepositGuarantee", role_cls)
    market = market_without_roles
    market.env.pos = 2

    # When
    market.add_government(govt)

    # Then
    market.add_role.assert_called_with(role_cls, govt)


def test_add_government_doesnt_add_role_for_foreigners(market_without_roles):
    # Given
    govt = Mock(country_pos=2)
    market = market_without_roles
    market.env.pos = 1

    # When
    market.add_government(govt)

    # Then
    market.add_role.assert_not_called()


# ---------------------------------------------------
# DEPOSIT MATCHING
# ----------------------------------------------------


@pytest.fixture
def depositor():
    # Given
    return Mock()


@pytest.fixture
def deposit_bank():
    # Given
    return Mock()


@pytest.fixture
def market_without_deposit(market):
    # Given
    market.env = Mock()
    market.transfer_stock = Mock()
    market.make_transaction = Mock()
    return market


def test_join_deposit_bank_creates_graph_edge(
    market_without_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_without_deposit
    graph = market.graph

    # When
    market.join_deposit_bank(depositor, deposit_bank)

    # Then
    assert graph.has_edge(depositor, deposit_bank)


def test_join_deposit_bank_with_initial_amount(
    market_without_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_without_deposit
    graph = market.graph

    # When
    market.join_deposit_bank(depositor, deposit_bank, amount=500)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == 500


def test_join_deposit_bank_transfers_cash(
    market_without_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_without_deposit

    # When
    market.join_deposit_bank(depositor, deposit_bank, amount=500)

    # Then
    market.transfer_stock.assert_any_call("cash", depositor.id, deposit_bank.id, 500)


def test_join_deposit_bank_updates_accounts(
    market_without_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_without_deposit
    bank_id = deposit_bank.id

    # When
    market.join_deposit_bank(depositor, deposit_bank, amount=500)

    # Then
    market.transfer_stock.assert_any_call("deposits", bank_id, depositor.id, 500)


@pytest.fixture
def market_with_deposit(market_without_deposit, depositor, deposit_bank):
    # Given
    market = market_without_deposit
    market.graph.add_edge(depositor, deposit_bank, amount=100)
    return market


def test_leave_deposit_bank_remove_graph_edge(
    market_with_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_with_deposit
    graph = market.graph

    # When
    market.leave_deposit_bank(depositor, deposit_bank)

    # Then
    assert not graph.has_edge(depositor, deposit_bank)


def test_leave_deposit_bank_transfers_cash(
    market_with_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_with_deposit

    # When
    market.leave_deposit_bank(depositor, deposit_bank)

    # Then
    market.transfer_stock.assert_any_call("cash", deposit_bank.id, depositor.id, 100)


def test_leave_deposit_bank_updates_accounts(
    market_with_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_with_deposit
    bank_id = deposit_bank.id

    # When
    market.leave_deposit_bank(depositor, deposit_bank)

    # Then
    market.transfer_stock.assert_any_call("deposits", depositor.id, bank_id, 100)


# ---------------------------------------------------
# MAKE / WITHDRAW DEPOSIT
# ----------------------------------------------------


def test_make_deposits_transfers_cash(market_with_deposit, depositor, deposit_bank):
    # Given
    market = market_with_deposit

    # When
    market.make_deposits(depositor, deposit_bank, 50)

    # Then
    market.transfer_stock.assert_any_call("cash", depositor.id, deposit_bank.id, 50)


def test_make_deposits_updates_accounts(market_with_deposit, depositor, deposit_bank):
    # Given
    market = market_with_deposit
    bank_id = deposit_bank.id

    # When
    market.make_deposits(depositor, deposit_bank, 50)

    # Then
    market.transfer_stock.assert_any_call("deposits", bank_id, depositor.id, 50)


def test_make_deposits_updates_edge(market_with_deposit, depositor, deposit_bank):
    # Given
    market = market_with_deposit
    graph = market.graph

    # When
    market.make_deposits(depositor, deposit_bank, 50)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == 150


def test_withdraw_deposits_transfers_cash(market_with_deposit, depositor, deposit_bank):
    # Given
    market = market_with_deposit

    # When
    market.withdraw_deposits(depositor, deposit_bank, 50)

    # Then
    market.transfer_stock.assert_any_call("cash", deposit_bank.id, depositor.id, 50)


def test_withdraw_deposits_updates_accounts(
    market_with_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_with_deposit
    bank_id = deposit_bank.id

    # When
    market.withdraw_deposits(depositor, deposit_bank, 50)

    # Then
    market.transfer_stock.assert_any_call("deposits", depositor.id, bank_id, 50)


def test_withdraw_deposits_updates_edge(market_with_deposit, depositor, deposit_bank):
    # Given
    market = market_with_deposit
    graph = market.graph

    # When
    market.withdraw_deposits(depositor, deposit_bank, 50)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == 50


# ---------------------------------------------------
# DEPOSIT REPAYMENT / REIMBURSEMENT
# ----------------------------------------------------


def test_pay_interests_updates_accounts(market_with_deposit, depositor, deposit_bank):
    # Given
    market = market_with_deposit
    source = deposit_bank.id
    target = depositor.id

    # When
    market.pay_interests(deposit_bank, depositor, 10.0)

    # Then
    market.transfer_stock.assert_any_call("deposits", source, target, 10.0)
    market.make_transaction.assert_any_call("dep_interests", source, target, 10.0)


def test_pay_interests_updates_graph_edge(market_with_deposit, depositor, deposit_bank):
    # Given
    market = market_with_deposit
    graph = market.graph

    # When
    market.pay_interests(deposit_bank, depositor, 10.0)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == pytest.approx(110.0)


def test_reimburse_deposits_transfers_cash(
    market_with_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_with_deposit
    guarantee = Mock()

    # When
    market.reimburse_deposits(guarantee, depositor, deposit_bank, 50)

    # Then
    market.transfer_stock.assert_any_call("cash", guarantee.id, depositor.id, 50)


def test_reimburse_deposits_updates_accounts(
    market_with_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_with_deposit
    bank_id = deposit_bank.id
    guarantee = Mock()

    # When
    market.reimburse_deposits(guarantee, depositor, deposit_bank, 50)

    # Then
    market.transfer_stock.assert_any_call("deposits", depositor.id, bank_id, 50)
    market.make_transaction.assert_any_call("loan_defaults", guarantee.id, bank_id, 50)


def test_reimburse_deposits_update_graph_edge(
    market_with_deposit,
    depositor,
    deposit_bank,
):
    # Given
    market = market_with_deposit
    graph = market.graph
    guarantee = Mock()

    # When
    market.reimburse_deposits(guarantee, depositor, deposit_bank, 50)

    # Then
    assert graph[depositor][deposit_bank]["amount"] == pytest.approx(50.0)


# ---------------------------------------------------
# EVOLUTION
# ----------------------------------------------------


@pytest.fixture
def depositors():
    # Given
    depositors = []
    for defaulted in (True, False):
        role = Mock(defaulted=defaulted)
        role.name = "depositor"
        depositors.append(role)
    return depositors


@pytest.fixture
def deposit_banks():
    # Given
    deposit_banks = []
    for defaulted in (True, False):
        role = Mock(defaulted=defaulted)
        role.name = "deposit_bank"
        deposit_banks.append(role)
    return deposit_banks


@pytest.fixture
def market_with_defaults(market, depositors, deposit_banks):
    for role in depositors + deposit_banks:
        market.roles[role.id] = role
    market.remove_role = Mock()
    return market


def test_clear_defaults_removes_defaulted_banks(market_with_defaults, deposit_banks):
    # Given
    market = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(deposit_banks[0]) in market.remove_role.call_args_list
    assert call(deposit_banks[1]) not in market.remove_role.call_args_list


def test_clear_defaults_removes_defaulted_depositors(market_with_defaults, depositors):
    # Given
    market = market_with_defaults

    # When
    market.clear_defaults()

    # Then
    assert call(depositors[0]) in market.remove_role.call_args_list
    assert call(depositors[1]) not in market.remove_role.call_args_list
