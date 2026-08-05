from mcabsfc.agents import CentralBankAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mcabsfc.base import EcoAgent

    # Assert
    assert issubclass(CentralBankAgent, EcoAgent)
