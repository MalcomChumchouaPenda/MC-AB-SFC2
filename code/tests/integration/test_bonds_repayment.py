import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.agents.government import Government
from model.spaces.bond_market import BondMarket


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
    model.p.initial_bond_rate = 0.0
    return model


@pytest.fixture
def market(model):
    # Given
    return BondMarket(model)


@pytest.fixture
def cb(model, market):
    # Given
    cb = CentralBank(model)
    cb.national = True
    market.add_central_bank(cb)
    return cb


@pytest.fixture
def govt(model, market):
    # Given
    govt = Government(model)
    market.add_government(govt)
    return govt


@pytest.fixture
def bank(model, market):
    # Given
    bank = Bank(model)
    market.add_bank(bank)
    return bank


def test_clears_link_amount_with_bank(market, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    bank.account["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 0


def test_decreases_bonds_from_bank(market, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    bank.account["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bonds"] == 0
    assert bank.account["bonds"] == 0


def test_increases_bond_interests_for_bank(market, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    bank.account["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bond_interests"] == -4.2
    assert bank.account["bond_interests"] == 4.2


def test_transfers_cash_to_bank(market, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    bank.account["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account["cash"] == -104.2
    assert bank.account["cash"] == 104.2


def test_clears_link_amount_with_central_bank(market, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    cb.account["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 0


def test_decreases_bonds_from_central_bank(market, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    cb.account["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bonds"] == 0
    assert cb.account["bonds"] == 0


def test_increases_bond_interests_for_central_bank(market, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    cb.account["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bond_interests"] == -4.2
    assert cb.account["bond_interests"] == 4.2


def test_transfers_cash_to_central_bank(market, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    cb.account["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account["cash"] == -104.2
    assert cb.account["cash"] == 104.2
