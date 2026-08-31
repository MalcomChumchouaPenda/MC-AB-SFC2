import math
import pytest
from unittest.mock import Mock, PropertyMock
from mc_ab_sfc2.agents.private import Bank

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_agent():
    # Given
    from mc_ab_sfc2.base import EcoAgent

    # Assert
    assert issubclass(Bank, EcoAgent)


@pytest.fixture
def bank():
    # Given
    model = Mock()
    bank = Bank(model)
    bank.setup()
    return bank


def test_has_default_stocks(bank):
    # Assert
    assert bank.loans == 0
    assert bank.equity == 0
    assert bank.reserves == 0
    assert bank.cash_advances == 0


def test_has_default_flows(bank):
    # Assert
    assert bank.loan_interest == 0
    assert bank.reserve_interest == 0
    assert bank.cash_advance_interest == 0
    assert bank.dividends == 0


def test_has_default_choices(bank):
    # Assert
    assert bank.deposit_rate == 0
    assert bank.taxes_payable == 0
    assert bank.dividends_payable == 0


def test_has_default_indicators(bank):
    # Assert
    assert bank.country is None
    assert bank.credit_capacity == 0
    assert bank.net_worth == 0
    assert bank.profit == 0
    assert bank.defaulted == False


def test_has_default_refs(bank):
    # Assert
    assert bank.central_bank is None


# ---------------------------------------------------
# DERIVED STATE TESTS
# ----------------------------------------------------


@pytest.fixture
def bank_with_country():
    model, country = Mock(), Mock()
    bank = Bank(model)
    bank.setup()
    bank.country = country
    return bank, country


def test_expose_bonds_total(bank_with_country):
    # Given
    bonds = [{"issuer": object(), "principal": 500}]
    bank, country = bank_with_country
    bond_market = country.union.bond_market
    bond_market.get_buyer_bonds.return_value = bonds

    # Assert
    assert bank.bonds == 500


def test_expose_bond_interests_total(bank_with_country):
    # Given
    bonds = [{"issuer": object(), "interests": 50.0}]
    bank, country = bank_with_country
    bond_market = country.union.bond_market
    bond_market.get_buyer_bonds.return_value = bonds

    # Assert
    assert bank.bond_interests == pytest.approx(50.0)


def test_expose_deposits_total(bank):
    # Given
    deposits = [{"client": object(), "amount": 500}]
    deposit_market = Mock()
    deposit_market.get_bank_deposits.return_value = deposits
    bank.model.deposit_markets = {"any": deposit_market}

    # Assert
    assert bank.deposits == 500


def test_expose_deposit_interests_total(bank):
    # Given
    deposits = [{"client": object(), "interests": 50.0}]
    deposit_market = Mock()
    deposit_market.get_bank_deposits.return_value = deposits
    bank.model.deposit_markets = {"any": deposit_market}

    # Assert
    assert bank.dep_interests == pytest.approx(50.0)


# ---------------------------------------------------
# BEHAVIORS TESTS
# ----------------------------------------------------


def test_update_deposit_rate_as_fraction_of_discount_rate(bank):
    # Given
    cb = Mock(discount_rate=0.05)
    bank.central_bank = cb
    bank.p.zeta = 0.8

    # When
    bank.update_deposit_rate()

    # Then
    assert bank.deposit_rate == pytest.approx(0.04)


def test_pay_deposit_interests_to_all_clients(bank):
    # Given
    client = object()
    deposits = [{"client": client, "amount": 100}]
    deposit_market = Mock()
    deposit_market.get_bank_deposits.return_value = deposits
    bank.model.deposit_markets = {"any": deposit_market}
    bank.deposit_rate = 0.05

    # When
    bank.pay_deposit_interests()

    # Then
    deposit_market.get_bank_deposits.assert_called_once_with(bank)
    deposit_market.pay_interests.assert_called_once_with(client, bank, 5.0)


def test_updates_credit_capacity(bank):
    # Given
    bank.equity = 100
    bank.p.mu1 = 10

    # When
    bank.update_credit_capacity()

    # Then
    assert bank.credit_capacity == pytest.approx(1000)


def test_calc_loan_probability(bank):
    # Given
    bank.p.iota_l = 1
    borrower = Mock(loan_demand=100, target_leverage=0.5)

    # When
    probability = bank.calc_loan_probability(borrower)

    # Then
    assert probability == pytest.approx(math.exp(-0.5))


def test_calc_loan_rate(bank):
    # Given
    cb = Mock(discount_rate=0.05)
    bank.central_bank = cb
    bank.p.chi = 0.02
    borrower = Mock(target_leverage=5.0)

    # When
    rate = bank.calc_loan_rate(borrower)

    # Then
    assert rate == pytest.approx(0.02 * 5.0 + 0.05)


@pytest.fixture
def bank_as_lender():
    # Given
    borrowers = [Mock(loan_demand=100) for _ in range(5)]
    lender = Mock(loan_applicants=borrowers)
    bank = Bank(model=Mock())
    bank.roles["lender"] = lender
    bank.calc_loan_rate = Mock(return_value=0.02)
    bank.calc_loan_probability = Mock(return_value=0.4)
    bank.update_credit_capacity = Mock()
    random = bank.model.nprandom
    random.choice.return_value = 0
    return bank


def test_grant_loans_and_processes_all_loan_applicants(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 500
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.random

    # When
    bank.grant_loans()

    # Then
    random.shuffle.assert_called_with(applicants)
    for borrower in applicants:
        bank.calc_loan_rate.assert_any_call(borrower)
        bank.calc_loan_probability.assert_any_call(borrower)


def test_grant_loans_with_computed_probability(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 500
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.nprandom
    random.choice.side_effect = iter([1, 0, 0, 0, 0])

    # When
    bank.grant_loans()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    lender.grant_loan.assert_called_with(applicants[0], 100, 0.02)
    assert lender.grant_loan.call_count == 1


def test_grant_loans_in_regards_of_credit_capacity(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 200
    lender = bank.roles["lender"]
    applicants = lender.loan_applicants
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    lender.grant_loan.assert_any_call(applicants[0], 100, 0.02)
    lender.grant_loan.assert_any_call(applicants[1], 100, 0.02)
    assert lender.grant_loan.call_count == 2


def test_grant_loans_cleans_loan_applicants_list(bank_as_lender):
    # Given
    bank = bank_as_lender
    bank.credit_capacity = 200
    lender = bank.roles["lender"]
    random = bank.model.nprandom
    random.choice.return_value = 1

    # When
    bank.grant_loans()

    # Then
    assert len(lender.loan_applicants) == 0


@pytest.fixture
def bank_with_cb(monkeypatch):
    model = Mock()
    model.p.mu2 = 0.1
    deposits_prop = PropertyMock(return_value=1000)
    monkeypatch.setattr(Bank, "deposits", deposits_prop)
    cb = Mock(cash_advances=0, reserves=0)
    bank = Bank(model)
    bank.reserves = 0
    bank.cash_advances = 0
    bank.central_bank = cb
    return bank, cb


def test_doesnot_request_cash_advance_when_sufficient_reserves(bank_with_cb):
    # Given
    bank, cb = bank_with_cb
    bank.reserves = 200

    # When
    bank.request_cash_advances()

    # Then
    assert bank.cash_advances == 0
    assert cb.cash_advances == 0


def test_request_cash_advance_when_insufficient_reserves(bank_with_cb):
    # Given
    bank, cb = bank_with_cb
    bank.reserves = 50

    # When
    bank.request_cash_advances()

    # Then
    assert bank.cash_advances == 50
    assert cb.cash_advances == 50


def test_calc_bond_purchases_probability():
    # Given
    model = Mock()
    model.p.iota_b = 2
    bank = Bank(model)
    issuer = Mock(bonds=500, gdp=1000)

    # When
    probability = bank.calc_bond_purchases_probability(issuer)

    # Then
    assert probability == math.exp(-1)


@pytest.mark.parametrize("reserves, expected", [(150, 50), (100, 0)])
def test_calc_excess_reserves(monkeypatch, reserves, expected):
    # Given
    monkeypatch.setattr(Bank, "deposits", PropertyMock(return_value=1000))
    bank = Bank(model=Mock())
    bank.p.mu2 = 0.1
    bank.reserves = reserves

    # When
    excess_reserves = bank.calc_excess_reserves()

    # Then
    assert excess_reserves == expected


def test_find_bond_suppliers_gets_and_shuffles_issuers(bank_with_country):
    # Given
    bond_issuers = [Mock() for _ in range(3)]
    bank, country = bank_with_country
    bond_market = country.union.bond_market
    bond_market.get_issuers.return_value = bond_issuers
    random = bank.model.random

    # When
    result = bank.find_bond_issuers()

    # Then
    bond_market.get_issuers.assert_called_with()
    random.shuffle.assert_called_with(bond_issuers)
    assert result == bond_issuers


@pytest.fixture
def bond_issuers():
    return [
        Mock(bond_supply=100, bonds=100, gdp=100),
        Mock(bond_supply=100, bonds=100, gdp=100),
    ]


@pytest.fixture
def bank_as_bond_buyer(bond_issuers):
    model = Mock()
    bank = Bank(model)
    bank.country = Mock()
    bank.calc_bond_purchases_probability = Mock(return_value=0)
    bank.calc_excess_reserves = Mock(return_value=0)
    bank.find_bond_issuers = Mock(return_value=bond_issuers)
    bank.model.nprandom.choice.return_value = 1
    return bank


def test_buy_bonds_with_purchases_probability(bank_as_bond_buyer, bond_issuers):
    # Given
    bank = bank_as_bond_buyer
    bank.calc_excess_reserves.return_value = 1000
    calc_prob = bank.calc_bond_purchases_probability
    calc_prob.return_value = 0.4
    random = bank.model.nprandom

    # When
    bank.buy_bonds()

    # Then
    random.choice.assert_called_with([0, 1], p=[0.6, 0.4])
    assert random.choice.call_count == 2
    for bond_issuer in bond_issuers:
        calc_prob.assert_any_call(bond_issuer)


def test_buy_bonds_with_excess_reserves(bank_as_bond_buyer, bond_issuers):
    # Given
    bank = bank_as_bond_buyer
    bank.calc_excess_reserves.return_value = 50
    bond_market = bank.country.union.bond_market

    # When
    bank.buy_bonds()

    # Then
    bond_market.buy_bonds.assert_called_once_with(bank, bond_issuers[0], 50)


def test_dont_buy_bonds_with_insufficient_reserves(bank_as_bond_buyer, bond_issuers):
    # Given
    bank = bank_as_bond_buyer
    bank.calc_excess_reserves.return_value = 50
    bond_market = bank.country.union.bond_market

    # When
    bank.buy_bonds()

    # Then
    bond_market.buy_bonds.assert_called_once_with(bank, bond_issuers[0], 50)


@pytest.fixture
def mock_dep_interests(monkeypatch):
    dep_interests = PropertyMock()
    monkeypatch.setattr(Bank, "dep_interests", dep_interests)
    return dep_interests


@pytest.fixture
def mock_bond_interests(monkeypatch):
    bond_interests = PropertyMock()
    monkeypatch.setattr(Bank, "bond_interests", bond_interests)
    return bond_interests


def test_calc_profit(bank, mock_dep_interests, mock_bond_interests):
    # Given
    bank.loan_interest = 100
    bank.reserve_interest = 10
    bank.bad_debt = 20
    bank.cash_advance_interest = 10
    mock_dep_interests.return_value = 40
    mock_bond_interests.return_value = 30

    # When
    profit = bank.calc_profit()

    # Then
    assert profit == 70


@pytest.fixture
def model_with_govt():
    # Given
    govt = Mock(tax_rate=0.0, reserves=0, taxes=0)
    model = Mock()
    model.governments = {"any": govt}
    return model, govt


@pytest.fixture
def bank_with_govt(model_with_govt):
    # Given
    model, govt = model_with_govt
    bank = Bank(model)
    bank.country = "any"
    bank.taxes = 0
    bank.reserves = 0
    return bank, govt


@pytest.mark.parametrize("profit, expected", [(100, 20), (0, 0), (-50, 0)])
def test_calc_taxes(bank_with_govt, profit, expected):
    # Given
    bank, govt = bank_with_govt
    bank.profit = profit
    govt.tax_rate = 0.20

    # When
    taxes = bank.calc_taxes()

    # Then
    assert taxes == expected


def test_calc_dividends():
    # Given
    model = Mock()
    model.p.rho = 0.5
    bank = Bank(model)
    bank.profit = 100
    bank.taxes_payable = 20

    # When
    dividends = bank.calc_dividends()

    # Then
    assert dividends == 40


def test_compute_profit_distribution(bank):
    # Given
    bank.calc_profit = Mock(return_value=100)
    bank.calc_taxes = Mock(return_value=20)
    bank.calc_dividends = Mock(return_value=30)

    # When
    bank.compute_profit_distribution()

    # Then
    assert bank.profit == 100
    assert bank.taxes_payable == 20
    assert bank.dividends_payable == 30


def test_update_net_worth(bank):
    # Given
    issuer = Mock()
    bank.profit = 500
    bank.net_worth = 500
    bank.taxes_payable = 50
    bank.dividends_payable = 100
    bank.roles["equity_issuer"] = issuer

    # When
    bank.update_net_worth()

    # Then
    issuer.update_equity_holdings.assert_called_once_with()
    assert bank.net_worth == pytest.approx(850)


def test_pay_taxes(bank_with_govt):
    # Given
    bank, govt = bank_with_govt
    bank.taxes_payable = 50

    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.taxes == 50
    assert bank.reserves == -50
    assert govt.taxes == 50
    assert govt.reserves == 50


def test_pay_no_taxes(bank_with_govt):
    # Given
    bank, govt = bank_with_govt
    bank.taxes_payable = 0

    # When
    bank.pay_taxes()

    # Then
    assert bank.taxes_payable == 0
    assert bank.taxes == 0
    assert bank.reserves == 0
    assert govt.taxes == 0
    assert govt.reserves == 0


def test_pay_dividends(bank):
    # Given
    issuer = Mock()
    bank.dividends_payable = 100
    bank.roles["equity_issuer"] = issuer

    # When
    bank.pay_dividends()

    # Then
    issuer.distribute_dividends.assert_called_once_with(100)
    assert bank.dividends_payable == 0


def test_pay_no_dividends(bank):
    # Given
    issuer = Mock()
    bank.dividends_payable = 0
    bank.roles["equity_issuer"] = issuer

    # When
    bank.pay_dividends()

    # Then
    issuer.distribute_dividends.assert_not_called()


# ---------------------------------------------------
# ENDOGENEOUS EXIT TESTS
# ----------------------------------------------------


@pytest.fixture
def bank_before_exit():
    issuer = Mock()
    issuer.get_average_wage.return_value = 100
    model = Mock()
    bank = Bank(model)
    bank.roles = {"equity_issuer": issuer}
    return bank


def test_exit_when_bankrupt(bank_before_exit):
    # Given
    bank = bank_before_exit
    bank.net_worth = 90
    issuer = bank.roles["equity_issuer"]

    # When
    bank.exit()

    # Then
    issuer.close_bank.assert_called_once_with(bank)


def test_does_not_exit_when_not_bankrupt(bank_before_exit):
    # Given
    bank = bank_before_exit
    bank.net_worth = 150
    issuer = bank.roles["equity_issuer"]

    # When
    bank.exit()

    # Then
    issuer.close_bank.assert_not_called()
