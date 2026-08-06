from mc_ab_sfc.agents import FirmAgent

# ---------------------------------------------------
# ARCHITECTURAL TESTS
# ----------------------------------------------------


def test_is_ecoagent():
    # Given
    from mc_ab_sfc.base import EcoAgent

    # Assert
    assert issubclass(FirmAgent, EcoAgent)
