from mcabsfc.agents import BankAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mcabsfc.base import EcoAgent

    # Assert
    assert issubclass(BankAgent, EcoAgent)
