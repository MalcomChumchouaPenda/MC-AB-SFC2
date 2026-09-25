from unittest.mock import Mock
import pytest
from agentpy import Model
from model.agents.central_bank import CentralBank
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model():
    # Given
    model = Model()
    model.p.K = 1
    model.p.xi = 0.5
    model.p.xi_deltap = 1.5
    model.p.long_run_rate = 0.02
    model.p.inflation_target = 0.02
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    return union


@pytest.fixture
def union_cb(model, union):
    cb = CentralBank(model)
    union.add_policy_maker(cb)
    return cb


def test_union_central_bank_determines_discount_rate(union, union_cb):
    # Given
    union_cb.prev_discount_rate = 0.03
    union.average_inflation = 0.04

    # When
    union_cb.determine_discount_rate()

    # Then
    assert union.discount_rate == pytest.approx(0.04)


@pytest.fixture
def national_cb(model, union):
    cb = CentralBank(model)
    union.add_policy_maker(cb)
    country = union.spaces["country_0"]
    country.add_monetary_authority(cb)
    return cb


def test_national_central_banks_implements_discount_rate(union, national_cb):
    # Given
    union.discount_rate = 0.05
    role = national_cb.roles["monetary_authority"]

    # When
    national_cb.implement_discount_rate()

    # Then
    assert role.discount_rate == pytest.approx(0.05)
