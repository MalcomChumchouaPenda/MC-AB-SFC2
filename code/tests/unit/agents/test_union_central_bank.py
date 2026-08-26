import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents.central_bank import CentralBank, UnionCentralBank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_central_bank():
    # Assert
    assert issubclass(UnionCentralBank, CentralBank)


@pytest.fixture
def cb():
    # Given
    model = Mock()
    cb = UnionCentralBank(model)
    cb.setup()
    return cb


def test_has_default_average_inflation(cb):
    # Assert
    assert cb.average_inflation == 0.0


def test_has_default_previous_discount_rate(cb):
    # Assert
    assert cb.prev_discount_rate == 0


def test_has_default_discount_rate(cb):
    # Assert
    assert cb.discount_rate == 0


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_calc_average_inflation(cb):
    # Given
    model = cb.model
    model.national_goods_markets = {i: Mock(inflation=0.05, gdp=100) for i in range(5)}

    # When
    average_inflation = cb.calc_average_inflation()

    # Then
    assert average_inflation == pytest.approx(0.05)


def test_calc_discount_rate(cb):
    # Given
    cb.average_inflation = 0.04
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
    cb.prev_discount_rate = 0.0
    cb.discount_rate = 0.0
    cb.calc_average_inflation = Mock(return_value=0.05)
    cb.calc_discount_rate = Mock(return_value=0.02)

    # When
    cb.update_discount_rate()

    # Then
    assert cb.average_inflation == 0.05
    assert cb.discount_rate == 0.02


def test_update_discount_rate_changes_lag_values(cb):
    # Given
    cb.prev_discount_rate = 0.01
    cb.discount_rate = 0.02
    cb.calc_average_inflation = Mock(return_value=0.0)
    cb.calc_discount_rate = Mock(return_value=0.03)

    # When
    cb.update_discount_rate()

    # Then
    assert cb.prev_discount_rate == 0.02
    assert cb.discount_rate == 0.03
