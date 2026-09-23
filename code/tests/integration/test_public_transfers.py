import pytest
from unittest.mock import Mock
from model.spaces.monetary_union import MonetaryUnion
from model.agents.government import Government
from model.agents.central_bank import CentralBank
from model.agents.household import Household


@pytest.fixture
def model():
    # Given
    model = Mock()
    model.p.K = 1
    return model


@pytest.fixture
def govt(model):
    # Given
    govt = Government(model)
    govt.setup()
    return govt


@pytest.fixture
def cb(model):
    # Given
    cb = CentralBank(model)
    cb.setup()
    return cb



@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.setup()
    return union


@pytest.fixture
def country(union):
    # Given
    country = union.spaces["country_0"]
    country.monetary_authority = Mock()
    return country



@pytest.fixture
def country_before_profit_transfers(country, govt, cb):
    # Given
    country.add_fiscal_authority(govt)
    country.add_monetary_authority(cb)
    return country


@pytest.mark.usefixtures("country_before_profit_transfers")
def test_central_bank_transfer_profits(govt, cb):
    # Given
    cb.account.flows["adv_interests"] = 50
    cb.account.flows["cash_interests"] = 20
    cb.account.flows["bond_interests"] = 100

    # When
    cb.transfer_profit()

    # Then
    assert cb.account.flows["profit_transfers"] == -130
    assert cb.account.stocks["cash"] == -130
    assert govt.account.flows["profit_transfers"] == 130
    assert govt.account.stocks["cash"] == 130


@pytest.fixture
def households(model):
    # Given
    households = []
    for _ in range(4):
        household = Household(model)
        household.setup()
        households.append(household)
    return households


@pytest.fixture
def country_before_public_transfers(country, govt, households):
    # Given
    country.add_fiscal_authority(govt)
    for household in households:
        country.add_citizen(household)
    return country


@pytest.mark.usefixtures("country_before_public_transfers")
def test_government_pay_public_transfer_equally(govt, households):
    # Given
    govt.public_spending = 400

    # When
    govt.pay_public_transfers()

    # Then
    assert govt.account.stocks["cash"] == -400
    assert govt.account.flows["public_transfers"] == -400
    for household in households:
        assert household.account.stocks["cash"] == 100
        assert household.account.flows["public_transfers"] == 100
