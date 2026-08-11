import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import CentralBankAgent
from mc_ab_sfc.spaces import MonetaryUnionSpace, CountrySpace


@pytest.fixture
def model():
    model = Mock()
    model.p.xi = 0.5
    model.p.xi_deltap = 1.5
    model.p.long_run_rate = 0.02
    model.p.inflation_target = 0.02
    return model


@pytest.fixture
def central_bank(model):
    central_bank = CentralBankAgent(model)
    central_bank.prev_discount_rate = 0.03
    return central_bank


@pytest.fixture
def union(model):
    union = MonetaryUnionSpace(model)
    union.average_inflation = 0.04
    union.countries = {i:CountrySpace(model) for i in range(5)}
    return union


def test_central_bank_updates_discount_rate(central_bank, union):
    # Given
    union.add_central_bank(central_bank)

    # When
    central_bank.update_discount_rate()

    # Then
    assert union.discount_rate == pytest.approx(0.04)
    for country in union.countries.values():
        assert country.discount_rate == pytest.approx(0.04)

