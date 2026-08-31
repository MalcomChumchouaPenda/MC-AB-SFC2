import pytest
from unittest.mock import Mock
from mc_ab_sfc2.roles.equity_holder import EquityHolderRole

# ---------------------------------------------------
# ARCHITECTURE TESTS
# ----------------------------------------------------


def test_is_eco_role():
    # Given
    from mc_ab_sfc2.base import EcoRole

    # Assert
    assert issubclass(EquityHolderRole, EcoRole)


@pytest.fixture
def role():
    # Given
    space = Mock()
    agent = Mock(id=1)
    return EquityHolderRole(agent, space)


def test_exposes_equity(role):
    # Given
    household = role.agent
    household.equity = 100

    # Assert
    assert role.equity == 100


def test_exposes_desired_equity(role):
    # Given
    household = role.agent
    household.desired_equity = 100

    # Assert
    assert role.desired_equity == 100


def test_has_equity_issuer_ref(role):
    # Assert
    assert role.equity_issuer is None


def test_has_default_equity_share(role):
    # Assert
    assert role.share == 0.0


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_default_probability(role):
    # Given
    role.space.default_probability = 0.12

    # When
    default_probability = role.get_default_probability()

    # Then
    assert default_probability == 0.12


def test_get_potential_investors(role):
    # Given
    investors = [Mock()]
    country = role.space
    country.get_potential_investors.return_value = investors

    # When
    result = role.get_potential_investors()

    # Then
    assert result == investors


def test_get_potential_investors_exclude_itself(role):
    # Given
    country = role.space

    # When
    role.get_potential_investors()

    # Then
    country.get_potential_investors.assert_called_with(exclude=role)


def test_get_bank_firm_number_ratio(role):
    # Given
    country = role.space
    country.bank_roles = [Mock() for _ in range(2)]
    country.firm_roles = [Mock() for _ in range(10)]

    # When
    ratio = role.get_bank_firm_number_ratio()

    # Then
    assert ratio == 0.2


def test_get_bank_firm_unit_number_ratio_if_no_firms(role):
    # Given
    country = role.space
    country.bank_roles = []
    country.firm_roles = []

    # When
    ratio = role.get_bank_firm_number_ratio()

    # Then
    assert ratio == 1.0


def test_get_bank_firm_equity_ratio(role):
    # Given
    country = role.space
    country.bank_roles = [Mock(equity=100) for _ in range(2)]
    country.firm_roles = [Mock(equity=100) for _ in range(10)]

    # When
    ratio = role.get_bank_firm_equity_ratio()

    # Then
    assert ratio == 0.2


def test_get_bank_firm_unit_equity_ratio_if_no_firms(role):
    # Given
    country = role.space
    country.bank_roles = []
    country.firm_roles = []

    # When
    ratio = role.get_bank_firm_equity_ratio()

    # Then
    assert ratio == 1.0


def test_get_sector_equity_range_for_banks_sector(role):
    # Given
    country = role.space
    country.bank_roles = [Mock(equity=100 * i) for i in range(1, 10)]

    # When
    range_ = role.get_sector_equity_range("banks")

    # Then
    assert range_ == (100, 900)


@pytest.fixture
def firms():
    tradable = [Mock(tradable=True, equity=100 * i) for i in range(1, 10)]
    non_tradable = [Mock(tradable=False, equity=200 * i) for i in range(1, 5)]
    return tradable + non_tradable


def test_get_sector_equity_range_for_tradable_firms_sector(role, firms):
    # Given
    country = role.space
    country.firm_roles = [Mock(agent=f) for f in firms]

    # When
    range_ = role.get_sector_equity_range("tradable_firms")

    # Then
    assert range_ == (100, 900)


def test_get_sector_equity_range_for_non_tradable_firms_sector(role, firms):
    # Given
    country = role.space
    country.firm_roles = [Mock(agent=f) for f in firms]

    # When
    range_ = role.get_sector_equity_range("non_tradable_firms")

    # Then
    assert range_ == (200, 800)


@pytest.mark.parametrize("sector", ["non_tradable_firms", "tradable_firms", "banks"])
def test_get_sector_equity_range_returns_none_initially(role, sector):
    # Given
    country = role.space
    country.bank_roles = []
    country.firm_roles = []

    # When
    range_ = role.get_sector_equity_range(sector)

    # Then
    assert range_ is None


def test_create_firm_delegates_to_country(role):
    # Given
    country = role.space
    founders = [Mock(), Mock()]

    # When
    role.create_firm(founders, True)

    # Then
    country.create_firm.assert_called_with(founders, True)


def test_create_bank_delegates_to_country(role):
    # Given
    country = role.space
    founders = [Mock(), Mock()]

    # When
    role.create_bank(founders)

    # Then
    country.create_bank.assert_called_with(founders)
