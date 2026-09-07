import pytest
from unittest.mock import Mock
from model.base import EcoAccount
from model.agents.central_bank import CentralBank
from model.spaces.monetary_union import MonetaryUnion
from model.spaces.country import Country


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.xi = 0.5
    model.p.xi_deltap = 1.5
    model.p.long_run_rate = 0.02
    model.p.inflation_target = 0.02
    return model


@pytest.fixture
def country(model):
    # Given
    country = Country(model)
    country.setup()
    return country


@pytest.fixture
def union(model, country):
    # Given
    union = MonetaryUnion(model)
    union.setup()
    country.union = union
    return union


@pytest.fixture
def national_cb(model, country):
    cb = CentralBank(model)
    cb.setup()
    country.add_monetary_authority(cb)
    return cb


@pytest.fixture
def union_cb(model, union):
    cb = CentralBank(model)
    cb.setup()
    union.add_monetary_authority(cb)
    return cb



def test_central_banks_determines_discount_rate(union, union_cb):
    # Given
    union_cb.prev_discount_rate = 0.03
    union.average_inflation = 0.04

    # When
    union_cb.determine_discount_rate()

    # Then
    assert union_cb.discount_rate == pytest.approx(0.04)



def test_central_banks_implements_discount_rate(union_cb, national_cb):
    # Given
    union_cb.discount_rate = 0.05

    # When
    national_cb.implement_discount_rate()

    # Then
    assert national_cb.discount_rate == pytest.approx(0.05)

