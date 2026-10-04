from unittest.mock import Mock
import pytest
from model.spaces.monetary_union import MonetaryUnion
from model.agents.household import Household
from model.agents.firm import Firm
from model.agents.bank import Bank


@pytest.fixture
def model(fake_model, make_dlist):
    # Given
    model = fake_model
    model.p.cT = 0.6
    model.p.eta = 0.3
    model.p.initial_equity = 400
    model.firms = make_dlist()
    model.banks = make_dlist()
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_markets()
    union.create_countries(1)
    model.union = union
    return union


@pytest.fixture
def country(union):
    country = union.spaces["country_0"]
    return country


@pytest.fixture
def bank(model, union):
    # Given
    bank = Bank(model)
    union.place_bank(bank)
    return bank


@pytest.fixture
def founders(model, union, bank):
    # Given
    founders = []
    for i in range(2):
        household = Household(model)
        household.deposit_bank_id = bank.id
        household.desired_equity = 300 - i * 100
        union.place_household(household)
        founders.append(household)
    return founders


@pytest.fixture
def before_firm_creation(founders, bank):
    # Given
    for household in founders:
        household.account["cash"] = 400
        citizen_role = household.roles["citizen"]
        citizen_role.resid_equity = household.desired_equity
        depositor_role = household.roles["depositor"]
        depositor_role.join_deposit_bank(bank.id)


@pytest.mark.usefixtures("before_firm_creation")
def test_creates_new_firm(founders, model):
    # Given
    initiator = founders[0]
    firms = model.firms

    # When
    initiator.invest_equity()

    # Then
    assert len(firms) == 1
    assert isinstance(firms[0], Firm)


@pytest.mark.usefixtures("before_firm_creation")
def test_increases_new_firm_equities(founders, model):
    # Given
    initiator, partner = founders
    firms = model.firms

    # When
    initiator.invest_equity()

    # Then
    assert initiator.account["equities"] == 300
    assert partner.account["equities"] == 200
    assert firms[0].account["equities"] == -500


@pytest.mark.usefixtures("before_firm_creation")
def test_transfers_cash_from_households_to_firm(founders, model):
    # Given
    initiator, partner = founders
    firms = model.firms

    # When
    initiator.invest_equity()

    # Then
    assert initiator.account["cash"] == 100
    assert partner.account["cash"] == 200
    assert firms[0].account["cash"] == 500


@pytest.mark.usefixtures("before_firm_creation")
def test_creates_new_firm_equity_links(country, founders, model):
    # Given
    initiator, partner = founders
    citizen1 = initiator.roles["citizen"]
    citizen2 = partner.roles["citizen"]
    firms = model.firms
    positions = country.positions

    # When
    initiator.invest_equity()

    # Then
    assert country.graph[citizen1][positions[firms[0]]]["value"] == 300
    assert country.graph[citizen2][positions[firms[0]]]["value"] == 200


@pytest.fixture
def before_bank_creation(before_firm_creation, country):
    # Given
    _ = before_firm_creation
    roles = country.roles
    for i in range(5):
        company_role = Mock(equity=100, sector="F")
        company_role.name = "company"
        roles[i] = company_role


@pytest.mark.usefixtures("before_bank_creation")
def test_creates_new_bank(founders, model):
    # Given
    initiator = founders[0]
    banks = model.banks

    # # When
    initiator.invest_equity()

    # Then
    assert len(banks) == 1
    assert isinstance(banks[0], Bank)


@pytest.mark.usefixtures("before_bank_creation")
def test_increases_new_bank_equities(founders, model):
    # Given
    initiator, partner = founders
    banks = model.banks

    # # When
    initiator.invest_equity()

    # Then
    assert initiator.account["equities"] == 300
    assert partner.account["equities"] == 200
    assert banks[0].account["equities"] == -500


@pytest.mark.usefixtures("before_bank_creation")
def test_transfers_cash_from_household_to_new_bank(founders, model):
    # Given
    initiator, partner = founders
    banks = model.banks

    # # When
    initiator.invest_equity()

    # Then
    assert initiator.account["cash"] == 100
    assert partner.account["cash"] == 200
    assert banks[0].account["cash"] == 500


@pytest.mark.usefixtures("before_bank_creation")
def test_creates_new_bank_equity_links(country, founders, model):
    # Given
    initiator, partner = founders
    citizen1 = initiator.roles["citizen"]
    citizen2 = partner.roles["citizen"]
    positions = country.positions
    banks = model.banks

    # # When
    initiator.invest_equity()

    # Then
    assert country.graph[citizen1][positions[banks[0]]]["value"] == 300
    assert country.graph[citizen2][positions[banks[0]]]["value"] == 200
