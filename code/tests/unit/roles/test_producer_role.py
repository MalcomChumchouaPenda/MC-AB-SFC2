import pytest
from unittest.mock import Mock
from mc_ab_sfc.roles import ProducerRole

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecorole():
    # Given
    from mc_ab_sfc.base import EcoRole

    # Assert
    assert issubclass(ProducerRole, EcoRole)


@pytest.fixture
def producer():
    # Given
    market = Mock()
    owner = Mock(id=1)
    return ProducerRole(owner, market)

def test_has_price(producer):
    # Assert
    assert producer.price == 0


def test_exposes_position(producer):
    # Given
    firm = producer.owner
    firm.position = 0.9

    # Assert
    assert producer.position == 0.9


def test_exposes_productivity(producer):
    # Given
    firm = producer.owner
    firm.productivity = 0.9

    # Assert
    assert producer.productivity == 0.9


def test_exposes_available_quantity(producer):
    # Given
    firm = producer.owner
    firm.inventories = 100

    # Assert
    assert producer.available_quantity == 100


# ---------------------------------------------------
# BEHAVIORAL TESTS
# ----------------------------------------------------


def test_get_average_price(producer):
    # Given
    market = producer.space
    market.calc_average_price.return_value = 15

    # When
    average_price = producer.get_average_price()

    # Then
    assert average_price == 15


def test_get_average_productivity(producer):
    # Given
    market = producer.space
    market.calc_average_productivity.return_value = 2.5

    # When
    average_productiviy = producer.get_average_productivity()

    # Then
    assert average_productiviy == 2.5
