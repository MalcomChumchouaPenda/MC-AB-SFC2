import pytest
from model.agents.bank import Bank
from model.agents.central_bank import CentralBank
from model.agents.government import Government
from model.spaces.monetary_union import MonetaryUnion


@pytest.fixture
def model(fake_model):
    # Given
    model = fake_model
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
    return bank


@pytest.fixture
def before_bank_repayment(union, govt, bank):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    bank.account["bonds"] = 100
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market = union.spaces["bond_market"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)


@pytest.mark.usefixtures("before_bank_repayment")
def test_clears_link_amount_with_bank(union, govt, bank):
    # Given
    buyer_role = bank.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market = union.spaces["bond_market"]

    # When
    govt.repay_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 0


@pytest.mark.usefixtures("before_bank_repayment")
def test_decreases_bonds_from_bank(govt, bank):
    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bonds"] == 0
    assert bank.account["bonds"] == 0


@pytest.mark.usefixtures("before_bank_repayment")
def test_increases_bond_interests_for_bank(govt, bank):
    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bond_interests"] == -4.2
    assert bank.account["bond_interests"] == 4.2


@pytest.mark.usefixtures("before_bank_repayment")
def test_transfers_cash_to_bank(govt, bank):
    # When
    govt.repay_bonds()

    # Then
    assert govt.account["cash"] == -104.2
    assert bank.account["cash"] == 104.2


@pytest.fixture
def before_cb_repayment(union, govt, cb):
    # Given
    govt.bond_rate = 0.042
    govt.account["bonds"] = -100
    cb.account["bonds"] = 100
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market = union.spaces["bond_market"]
    market.graph.add_edge(issuer_role, buyer_role, amount=100)


@pytest.mark.usefixtures("before_cb_repayment")
def test_clears_link_amount_with_central_bank(union, govt, cb):
    # Given
    buyer_role = cb.roles["bond_buyer"]
    issuer_role = govt.roles["bond_issuer"]
    market = union.spaces["bond_market"]

    # When
    govt.repay_bonds()

    # Then
    assert market.graph[issuer_role][buyer_role]["amount"] == 0


@pytest.mark.usefixtures("before_cb_repayment")
def test_decreases_bonds_from_central_bank(govt, cb):
    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bonds"] == 0
    assert cb.account["bonds"] == 0


@pytest.mark.usefixtures("before_cb_repayment")
def test_increases_bond_interests_for_central_bank(govt, cb):
    # When
    govt.repay_bonds()

    # Then
    assert govt.account["bond_interests"] == -4.2
    assert cb.account["bond_interests"] == 4.2


@pytest.mark.usefixtures("before_cb_repayment")
def test_transfers_cash_to_central_bank(govt):
    # When
    govt.repay_bonds()

    # Then
    assert govt.account["cash"] == -104.2
