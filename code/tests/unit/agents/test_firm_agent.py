import agentpy as ap
from mcabsfc.agents import FirmAgent


def test_is_agent():
    assert issubclass(FirmAgent, ap.Agent)
