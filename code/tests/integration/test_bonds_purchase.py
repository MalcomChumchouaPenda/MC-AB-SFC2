import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.agents.government import Government
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.mu2 = 0.1
    model.p.iota_b = 0
    model.p.country_number = 1
    model.p.household_number = 0
    model.p.initial_public_transfer = 0.0
    model.p.initial_tax_rate = 0.0
    model.p.initial_discount_rate = 0.0
    model.p.initial_bond_rate = 0.0
    return model


@pytest.fixture
def union(model):
    # Given
    union = MonetaryUnion(model)
    union.create_markets()
    union.create_countries()
    return union


@pytest.fixture
def cb(model, union):
    # Given
    cb = CentralBank(model)
    cb.national = True
    cb.country_pos = 0
    union.add_agents([cb])
    return cb


@pytest.fixture
def govt(model, union):
    # Given
    govt = Government(model)
    govt.country_pos = 0
    union.add_agents([govt])
    return govt


@pytest.fixture
def bank(model, union):
    # Given
    bank = Bank(model)
    bank.country_pos = 0
    union.add_agents([bank])
    bank.account["cash"] = 150
    return bank


@pytest.fixture
def before_bonds_purchase(govt, bank):
    # Given
    bank.account["cash"] = 150
    bank.account["deposits"] = -1000
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100


@pytest.mark.usefixtures("before_bonds_purchase")
def test_decreases_bond_number_with_bank_purchase(govt, bank):
    # Given
    issuer_role = govt.roles["bond_issuer"]

    # When
    bank.buy_bonds()

    # Then
    assert issuer_role.bond_number == 90


@pytest.mark.usefixtures("before_bonds_purchase")
def test_creates_link_with_bank_purchase(govt, bank, union):
    # Given
    issuer_role = govt.roles["bond_issuer"]
    buyer_role = bank.roles["bond_buyer"]
    market = union.spaces["bond_market"]

    # When
    bank.buy_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 50


@pytest.mark.usefixtures("before_bonds_purchase")
def test_increases_bonds_with_bank_purchase(govt, bank):
    # When
    bank.buy_bonds()

    # Then
    assert govt.account["bonds"] == -50
    assert bank.account["bonds"] == 50


@pytest.mark.usefixtures("before_bonds_purchase")
def test_transfers_cash_from_bank(govt, bank):
    # When
    bank.buy_bonds()

    # Then
    assert govt.account["cash"] == 50
    assert bank.account["cash"] == 100


@pytest.mark.usefixtures("before_bonds_purchase")
def test_clears_bond_number_with_central_bank_purchase(govt, cb):
    # Given
    issuer_role = govt.roles["bond_issuer"]

    # When
    cb.buy_bonds()

    # Then
    assert issuer_role.bond_number == 0


@pytest.mark.usefixtures("before_bonds_purchase")
def test_creates_link_with_central_bank_purchase(govt, cb, union):
    # Given
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market = union.spaces["bond_market"]

    # When
    cb.buy_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 500


@pytest.mark.usefixtures("before_bonds_purchase")
def test_increases_bonds_with_central_bank_purchase(govt, cb):
    # When
    cb.buy_bonds()

    # Then
    assert cb.account["bonds"] == 500
    assert govt.account["bonds"] == -500


@pytest.mark.usefixtures("before_bonds_purchase")
def test_transfers_cash_from_central_bank(govt, cb):
    # When
    cb.buy_bonds()

    # Then
    assert govt.account["cash"] == 500
