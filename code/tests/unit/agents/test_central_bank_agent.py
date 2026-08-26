import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc.agents.central_bank import CentralBankAgent

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(CentralBankAgent, EcoAgent)


@pytest.fixture
def cb():
    # Given
    model = Mock()
    cb = CentralBankAgent(model)
    cb.setup()
    return cb


def test_expose_bonds_total(cb):
    # Given
    bonds = [{"issuer": object(), "principal": 500}]
    bond_market = cb.model.bond_market
    bond_market.get_buyer_bonds.return_value = bonds

    # Assert
    assert cb.bonds == 500


def test_expose_bond_interests_total(cb):
    # Given
    bonds = [{"issuer": object(), "interests": 50.0}]
    bond_market = cb.model.bond_market
    bond_market.get_buyer_bonds.return_value = bonds

    # Assert
    assert cb.bond_interests == pytest.approx(50.0)


def test_has_default_stocks(cb):
    # Assert
    assert cb.reserves == 0
    assert cb.cash_advances == 0


def test_has_default_flows(cb):
    # Assert
    assert cb.profit == 0
    assert cb.reserve_interest == 0
    assert cb.cash_advance_interest == 0


def test_has_default_indicators(cb):
    # Assert
    assert cb.prev_discount_rate == 0


def test_has_default_discount_rate(cb):
    # Assert
    assert cb.discount_rate == 0


def test_has_default_government_ref(cb):
    # Assert
    assert cb.government is None


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_calc_discount_rate(cb):
    # Given
    cb_role = Mock()
    cb_role.get_average_inflation.return_value = 0.04
    cb.roles["central_bank"] = cb_role
    cb.prev_discount_rate = 0.03
    cb.p.long_run_rate = 0.02
    cb.p.xi = 0.5
    cb.p.xi_deltap = 1.5
    cb.p.inflation_target = 0.02

    # When
    discount_rate = cb.calc_discount_rate()

    # Then
    assert discount_rate == pytest.approx(0.04)


def test_update_discount_rate(cb):
    # Given
    cb_role = Mock(discount_rate=0.0)
    cb.roles["central_bank"] = cb_role
    cb.calc_discount_rate = Mock(return_value=0.02)

    # When
    cb.update_discount_rate()

    # Then
    assert cb_role.discount_rate == 0.02


def test_buy_all_remaining_bonds(cb):
    # Given
    bond_market = cb.model.bond_market
    govt = Mock(bond_supply=100)
    cb.government = govt

    # When
    cb.buy_remaining_bonds()

    # Then
    bond_market.buy_bonds.assert_called_with(cb, govt, 100)


@pytest.fixture
def interest_props(monkeypatch):
    bond_interest = PropertyMock()
    monkeypatch.setattr(CentralBankAgent, "bond_interests", bond_interest)
    return bond_interest


def test_calc_profit(interest_props):
    # Given
    bond_interest = interest_props
    bond_interest.return_value = 100
    cb = CentralBankAgent(model=Mock())
    cb.cash_advance_interest = 40
    cb.reserve_interest = 20

    # When
    profit = cb.calc_profit()

    # Then
    assert profit == 120


def test_pay_profit_to_government():
    # Given
    cb_role, model = Mock(), Mock()
    cb = CentralBankAgent(model)
    cb.roles["central_bank"] = cb_role
    cb.calc_profit = Mock(return_value=100)

    # When
    cb.pay_profit()

    # Then
    cb.calc_profit.assert_called_with()
    cb_role.transfer_profit.assert_called_with(100)


def test_update_history():
    # Given
    cb_role = Mock(discount_rate=0.05)
    cb = CentralBankAgent(model=Mock())
    cb.roles["central_bank"] = cb_role
    cb.prev_discount_rate = 0.04

    # When
    cb.update_history()

    # Then
    assert cb.prev_discount_rate == 0.05
