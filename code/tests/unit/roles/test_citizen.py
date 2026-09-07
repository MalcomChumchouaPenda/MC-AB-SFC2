import pytest
from unittest.mock import Mock
from agentpy import AgentDList
from model.roles.citizen import Citizen

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from model.base import EcoRole

    # Assert
    assert issubclass(Citizen, EcoRole)


@pytest.fixture
def citizen_before_setup():
    # Given
    model = Mock()
    citizen = Citizen(model)
    return citizen


def test_has_residual_equity_prop(citizen_before_setup):
    # Given
    citizen = citizen_before_setup

    # When
    citizen.setup()

    # Then
    assert citizen.resid_equity == 0


# ---------------------------------------------------
# PERCEPTION TESTS
# ----------------------------------------------------


@pytest.fixture
def citizen_with_space(citizen_before_setup):
    # Given
    space = Mock()
    citizen = citizen_before_setup
    citizen.space = space
    return citizen, space


def test_get_prob_failure(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    space.prob_failure = 0.12

    # When
    perceived = citizen.get_prob_failure()

    # Then
    assert perceived == 0.12


def test_find_investors_use_space_method(citizen_with_space):
    # Given
    expected = [Mock() for _ in range(10)]
    citizen, space = citizen_with_space
    space.find_investors.return_value = expected

    # When
    investors = citizen.find_investors()

    # Then
    space.find_investors.assert_called_with(initiator=citizen)
    assert investors == expected


def test_get_bank_number_ratio_from_space(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    space.calc_bank_number_ratio.return_value = 0.5

    # When
    ratio = citizen.get_bank_number_ratio()

    # Then
    assert ratio == 0.5


def test_get_bank_equity_ratio_from_space(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    space.calc_bank_equity_ratio.return_value = 0.6

    # When
    ratio = citizen.get_bank_equity_ratio()

    # Then
    assert ratio == 0.6


def test_get_sector_equity_range_from_space(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    space.calc_sector_equity_range.return_value = (100, 200)

    # When
    range_ = citizen.get_sector_equity_range("X")

    # Then
    assert range_ == (100, 200)


def test_get_tax_rate(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    space.fiscal_authority.tax_rate = 0.2

    # When
    perceived = citizen.get_tax_rate()

    # Assert
    assert perceived == 0.2


# ---------------------------------------------------
# ACTION TESTS
# ----------------------------------------------------


@pytest.mark.parametrize("tradable", [True, False])
def test_create_firm_uses_space_method(citizen_with_space, tradable):
    # Given
    citizen, space = citizen_with_space
    firm, share = Mock(), Mock()

    # When
    citizen.create_firm(firm, [share], tradable=tradable)

    # Then
    space.create_firm.assert_called_with(firm, [share], tradable)


def test_create_bank_uses_space_method(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    bank, share = Mock(), Mock()

    # When
    citizen.create_bank(bank, [share])

    # Then
    space.create_bank.assert_called_with(bank, [share])


def test_pay_taxes_uses_space_method(citizen_with_space):
    # Given
    citizen, space = citizen_with_space

    # When
    citizen.pay_taxes(100)

    # Then
    space.pay_taxes.assert_called_with(citizen, 100)
