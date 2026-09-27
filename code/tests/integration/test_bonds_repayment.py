import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.agents.government import Government
from model.spaces.bond_market import BondMarket


@pytest.fixture
def market(fake_model):
    # Given
    model = fake_model
    return BondMarket(model)


@pytest.fixture
def cb(fake_model, market):
    # Given
    model = fake_model
    cb = CentralBank(model)
    cb.country_id = 0
    market.add_buyer(cb)
    return cb


@pytest.fixture
def govt(fake_model, market):
    # Given
    model = fake_model
    govt = Government(model)
    govt.country_id = 0
    market.add_issuer(govt)
    return govt


@pytest.fixture
def bank(fake_model, market):
    # Given
    model = fake_model
    bank = Bank(model)
    bank.country_id = 0
    market.add_buyer(bank)
    return bank


def test_clears_link_amount_with_bank(market, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account.stocks["bonds"] = -100
    bank.account.stocks["bonds"] = 100
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
    govt.account.stocks["bonds"] = -100
    bank.account.stocks["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.stocks["bonds"] == 0
    assert bank.account.stocks["bonds"] == 0


def test_increases_bond_interests_for_bank(market, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account.stocks["bonds"] = -100
    bank.account.stocks["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.flows["bond_interests"] == -4.2
    assert bank.account.flows["bond_interests"] == 4.2


def test_transfers_cash_to_bank(market, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account.stocks["bonds"] = -100
    bank.account.stocks["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.stocks["cash"] == -104.2
    assert bank.account.stocks["cash"] == 104.2


def test_clears_link_amount_with_central_bank(market, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account.stocks["bonds"] = -100
    cb.account.stocks["bonds"] = 100
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
    govt.account.stocks["bonds"] = -100
    cb.account.stocks["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.stocks["bonds"] == 0
    assert cb.account.stocks["bonds"] == 0


def test_increases_bond_interests_for_central_bank(market, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account.stocks["bonds"] = -100
    cb.account.stocks["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.flows["bond_interests"] == -4.2
    assert cb.account.flows["bond_interests"] == 4.2


def test_transfers_cash_to_central_bank(market, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account.stocks["bonds"] = -100
    cb.account.stocks["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)

    # When
    govt.repay_bonds()

    # Then
    assert govt.account.stocks["cash"] == -104.2
    assert cb.account.stocks["cash"] == 104.2

    