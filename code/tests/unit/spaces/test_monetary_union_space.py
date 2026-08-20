import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces.monetary_union import MonetaryUnionSpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnionSpace, EcoSpace)


@pytest.fixture
def union():
    # Given
    model = Mock()
    return MonetaryUnionSpace(model)


def test_has_central_bank_role(union):
    # Assert
    assert union.central_bank_role is None


def test_contains_countries(union):
    # Assert
    assert hasattr(union, "countries")
    assert isinstance(union.countries, dict)


def test_contains_international_markets(union):
    # Assert
    assert hasattr(union, "markets")
    assert isinstance(union.markets, dict)


def test_has_default_average_inflation(union):
    # Assert
    assert union.average_inflation == 0.0


def test_has_default_discount_rate(union):
    # Assert
    assert union.discount_rate == 0.0


def test_change_discount_rate(union):
    # Given
    union.countries = {i: Mock() for i in range(5)}

    # When
    union.discount_rate = 0.06

    # Then
    for country in union.countries.values():
        assert country.discount_rate == 0.06


# ---------------------------------------------------
# ROLES MANAGEMENT
# ----------------------------------------------------


class FakeCBRole(Mock):
    pass


@pytest.fixture
def union_with_roles():
    # Given
    model = Mock()
    union = MonetaryUnionSpace(model)
    union.add_role = Mock(side_effect=lambda a, b, c: a())
    return union


def test_add_central_bank_role(union_with_roles, monkeypatch):
    # Given
    central_bank = Mock()
    union = union_with_roles
    monkeypatch.setattr(
        "mc_ab_sfc.spaces.monetary_union.UnionCentralBankRole", FakeCBRole
    )

    # When
    cb_role = union.add_central_bank(central_bank)

    # Then
    union.add_role.assert_any_call(FakeCBRole, central_bank, "central_bank")
    assert isinstance(cb_role, FakeCBRole)
    assert cb_role is union.central_bank_role


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_calc_average_inflation(union):
    # Given
    union.countries = {i: Mock(inflation=0.05, gdp=100) for i in range(5)}

    # When
    average_inflation = union.calc_average_inflation()

    # Then
    assert average_inflation == pytest.approx(0.05)


def test_update_statistics_with_country_stats_updates(union, monkeypatch):
    # Given
    union.countries = {i: Mock() for i in range(5)}
    monkeypatch.setattr(union, "calc_average_inflation", Mock(return_value=0.05))

    # When
    union.update_statistics()

    # Then
    assert union.average_inflation == pytest.approx(0.05)
    for country in union.countries.values():
        country.update_statistics.assert_called_once()
