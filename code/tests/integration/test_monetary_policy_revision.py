import pytest
from model.agents.central_bank import CentralBank
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.xi = 0.5
    model.p.xi_deltap = 1.5
    model.p.long_run_rate = 0.02
    model.p.inflation_target = 0.02
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_markets()
    union.create_countries(1)
    return union


@pytest.fixture
def union_cb(model, union):
    cb = CentralBank(model)
    cb.national = False
    union.add_central_bank(cb)
    return cb


def test_updates_discount_rate_via_union_central_bank_action(union, union_cb):
    # Given
    union_cb.prev_discount_rate = 0.03
    union.average_inflation = 0.04

    # When
    union_cb.update_discount_rate()

    # Then
    assert union.discount_rate == pytest.approx(0.04)


@pytest.fixture
def national_cb(model, union):
    cb = CentralBank(model)
    cb.national = True
    union.add_central_bank(cb)
    return cb


def test_implements_discount_rate_via_national_central_banks_action(union, national_cb):
    # Given
    union.discount_rate = 0.05
    country = union.spaces["country_0"]

    # When
    national_cb.implement_discount_rate()

    # Then
    assert country.discount_rate == pytest.approx(0.05)
