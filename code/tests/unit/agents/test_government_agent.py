from mcabsfc.agents import GovernmentAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mcabsfc.base import EcoAgent

    # Assert
    assert issubclass(GovernmentAgent, EcoAgent)
