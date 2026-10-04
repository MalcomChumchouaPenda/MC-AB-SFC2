import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.agents.government import Government
from model.spaces.bond_market import BondMarket


@pytest.fixture
def market(fake_model):
    # Given
    model = fake_model
    model.p.mu2 = 0.1
    model.p.iota_b = 0
    return BondMarket(model)


@pytest.fixture
def cb(fake_model, market):
    # Given
    model = fake_model
    cb = CentralBank(model)
    cb.national = True
    market.add_central_bank(cb)
    return cb


@pytest.fixture
def govt(fake_model, market):
    # Given
    model = fake_model
    govt = Government(model)
    market.add_government(govt)
    return govt


@pytest.fixture
def bank(fake_model, market):
    # Given
    model = fake_model
    bank = Bank(model)
    market.add_central_bank(bank)
    return bank


def test_decreases_bond_number_with_bank_purchase(govt, bank):
    # Given
    bank.account["cash"] = 150
    bank.account["deposits"] = 1000
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    bank.buy_bonds()

    # Then
    assert issuer_role.bond_number == 90


def test_creates_link_with_bank_purchase(market, govt, bank):
    # Given
    bank.account["cash"] = 150
    bank.account["deposits"] = 1000
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    bank.buy_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 50


def test_increases_bonds_with_bank_purchase(govt, bank):
    # Given
    bank.account["cash"] = 150
    bank.account["deposits"] = 1000
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    bank.buy_bonds()

    # Then
    assert govt.account["bonds"] == -50
    assert bank.account["bonds"] == 50


def test_transfers_cash_from_bank(govt, bank):
    # Given
    bank.account["cash"] = 150
    bank.account["deposits"] = 1000
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    bank.buy_bonds()

    # Then
    assert govt.account["cash"] == 50
    assert bank.account["cash"] == 100


def test_clears_bond_number_with_central_bank_purchase(govt, cb):
    # Given
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    cb.buy_remaining_bonds()

    # Then
    assert issuer_role.bond_number == 0


def test_creates_link_with_central_bank_purchase(market, govt, cb):
    # Given
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    cb.buy_remaining_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 500


def test_increases_bonds_with_central_bank_purchase(govt, cb):
    # Given
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    cb.buy_remaining_bonds()

    # Then
    assert cb.account["bonds"] == 500
    assert govt.account["bonds"] == -500


def test_transfers_cash_from_central_bank(govt, cb):
    # Given
    issuer_role = govt.roles["bond_issuer"]
    issuer_role.bond_value = 5.0
    issuer_role.bond_number = 100

    # When
    cb.buy_remaining_bonds()

    # Then
    assert cb.account["cash"] == -500
    assert govt.account["cash"] == 500
