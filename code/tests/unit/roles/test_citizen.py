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
    space.citizens = AgentDList(Mock())
    space.companies = AgentDList(Mock())
    citizen = citizen_before_setup
    citizen.position = 1
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


def test_find_investors_get_potential_founders(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    eligible = Mock(resid_equity=100)
    ineligible = Mock(resid_equity=0)
    space.citizens.extend([eligible, ineligible])

    # When
    investors = citizen.find_investors()

    # Then
    assert investors == [eligible]


def test_find_investors_excludes_initiator(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    citizen.resid_equity = 90
    eligible = Mock(resid_equity=100)
    space.citizens.extend([eligible, citizen])

    # When
    investors = citizen.find_investors()

    # Then
    assert investors == [eligible]


def test_get_bank_firm_ratios(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    bank_sector = [Mock(sector="B", equity=100) for _ in range(2)]
    firm_sector = [Mock(sector="F", equity=50) for _ in range(10)]
    space.companies.extend(bank_sector + firm_sector)

    # When
    ratios = citizen.get_bank_firm_ratios()

    # Then
    assert ratios == (0.2, 0.4)


def test_get_bank_firm_unit_ratios_if_no_firms(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    space.companies.extend([Mock(sector="B", equity=100)])

    # When
    ratios = citizen.get_bank_firm_ratios()

    # Then
    assert ratios == (1.0, 1.0)


def test_get_sector_equity_range_for_any_sector(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    target_companies = [Mock(sector="X", equity=100 * i) for i in range(2, 5)]
    other_companies = [Mock(sector="Y", equity=100 * i) for i in range(1, 6)]
    space.companies.extend(target_companies + other_companies)

    # When
    range_ = citizen.get_sector_equity_range("X")

    # Then
    assert range_ == (200, 400)


def test_get_sector_equity_range_if_empty_sector(citizen_with_space):
    # Given
    citizen, space = citizen_with_space
    space.companies.extend([Mock(sector="Y", equity=100)])

    # When
    range_ = citizen.get_sector_equity_range("X")

    # Then
    assert range_ is None


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
