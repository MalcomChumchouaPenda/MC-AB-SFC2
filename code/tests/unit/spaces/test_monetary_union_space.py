import pytest
from unittest.mock import Mock
from mc_ab_sfc.spaces import MonetaryUnionSpace

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_space():
    # Given
    from mc_ab_sfc.base import EcoSpace

    # Assert
    assert issubclass(MonetaryUnionSpace, EcoSpace)


def test_requires_model_and_central_bank():
    # Assert
    expected = "missing 2 required positional arguments: "
    expected += "'model' and 'central_bank'"
    with pytest.raises(TypeError, match=expected):
        MonetaryUnionSpace()


class FakeCBRole(Mock):
    pass


@pytest.fixture
def init_args(monkeypatch):
    method = Mock(side_effect=lambda a, b, c: a())
    monkeypatch.setattr(MonetaryUnionSpace, "add_role", method)
    monkeypatch.setattr("mc_ab_sfc.spaces.UnionCentralBankRole", FakeCBRole)
    model, union_cb = Mock(), Mock()
    return model, union_cb


def test_init_and_create_union_central_bank_role(init_args):
    # Given
    model, cb = init_args

    # When
    union = MonetaryUnionSpace(model, cb)

    # Then
    union.add_role.assert_any_call(FakeCBRole, cb, "central_bank")
    assert isinstance(union.central_bank_role, FakeCBRole)


@pytest.fixture
def union(init_args):
    # Given
    model, cb = init_args
    return MonetaryUnionSpace(model, cb)


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
