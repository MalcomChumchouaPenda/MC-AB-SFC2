import pytest
from unittest.mock import Mock
from mc_ab_sfc.agents import CentralBankAgent
from mc_ab_sfc.spaces import MonetaryUnionSpace


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
    central_bank.discount_rate = 0.03
    return central_bank


@pytest.fixture
def union(model, central_bank):
    union = MonetaryUnionSpace(model, central_bank)
    union.average_inflation = 0.04
    return union


@pytest.mark.usefixtures("union")
def test_central_bank_updates_discount_rate(central_bank):
    # When
    central_bank.update_discount_rate()

    # Then
    assert central_bank.discount_rate == pytest.approx(0.04)
