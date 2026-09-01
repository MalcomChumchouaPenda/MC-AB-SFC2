import pytest
from unittest.mock import Mock, PropertyMock
from model.agents.central_bank import CentralBank, NationalCentralBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_central_bank():
    # Assert
    assert issubclass(NationalCentralBank, CentralBank)


@pytest.fixture
def cb():
    # Given
    model = Mock()
    cb = NationalCentralBank(model)
    cb.setup()
    return cb


def test_has_default_space_refs(cb):
    # Assert
    assert cb.country is None


def test_has_default_profits_value(cb):
    # Assert
    assert cb.profits == 0


def test_has_default_reserves_value(cb):
    # Assert
    assert cb.reserves == 0


def test_has_default_cash_avances_value(cb):
    # Assert
    assert cb.cash_advances == 0


def test_has_default_reserve_interests_value(cb):
    # Assert
    assert cb.reserve_interest == 0


def test_has_default_advance_interests_value(cb):
    # Assert
    assert cb.cash_advance_interest == 0


def test_has_default_government_ref(cb):
    # Assert
    assert cb.government is None


def test_has_default_union_bank_ref(cb):
    # Assert
    assert cb.union_bank is None


def test_exposes_default_discount_rate(cb):
    # Assert
    assert cb.discount_rate == 0.0


def test_exposes_union_bank_discount_rate(cb):
    # Given
    union_cb = Mock(discount_rate=0.05)
    cb.union_bank = union_cb

    # Assert
    assert cb.discount_rate == 0.05


@pytest.fixture
def cb_with_country():
    model, country = Mock(), Mock()
    cb = NationalCentralBank(model)
    cb.setup()
    cb.country = country
    return cb, country


def test_expose_bonds_total(cb_with_country):
    # Given
    bonds = [{"issuer": object(), "principal": 500}]
    cb, country = cb_with_country
    bond_market = country.union.bond_market
    bond_market.get_buyer_bonds.return_value = bonds

    # Assert
    assert cb.bonds == 500


def test_expose_bond_interests_total(cb_with_country):
    # Given
    bonds = [{"issuer": object(), "interests": 50.0}]
    cb, country = cb_with_country
    bond_market = country.union.bond_market
    bond_market.get_buyer_bonds.return_value = bonds

    # Assert
    assert cb.bond_interests == pytest.approx(50.0)


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_buy_all_remaining_bonds(cb_with_country):
    # Given
    cb, country = cb_with_country
    bond_market = country.union.bond_market
    govt = Mock(bond_supply=100)
    cb.government = govt

    # When
    cb.buy_remaining_bonds()

    # Then
    bond_market.buy_bonds.assert_called_with(cb, govt, 100)


@pytest.fixture
def mock_bond_interests(monkeypatch):
    bond_interests = PropertyMock()
    monkeypatch.setattr(NationalCentralBank, "bond_interests", bond_interests)
    return bond_interests


def test_calc_profit(cb, mock_bond_interests):
    # Given
    mock_bond_interests.return_value = 100
    cb = NationalCentralBank(model=Mock())
    cb.cash_advance_interest = 40
    cb.reserve_interest = 20

    # When
    profit = cb.calc_profit()

    # Then
    assert profit == 120


@pytest.fixture
def cb_with_govt():
    # Givent
    govt = Mock(profits=0, reserves=0)
    cb = NationalCentralBank(model=Mock())
    cb.government = govt
    cb.reserves = 0
    cb.profits = 0
    return cb, govt


def test_transfer_profit_to_government(cb_with_govt):
    # Given
    cb, govt = cb_with_govt
    cb.calc_profit = Mock(return_value=100)

    # When
    cb.transfer_profit()

    # Then
    assert cb.profits == 100
    assert cb.reserves == 100
    assert govt.profits == 100
    assert govt.reserves == 100
