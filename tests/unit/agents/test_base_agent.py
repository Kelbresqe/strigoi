from unittest.mock import MagicMock, patch

import pytest

from strigoi.agents.base_agent import BaseAgent


class TestBaseAgent:
    @pytest.fixture
    def agent_config(self):
        return {
            "llm_config": MagicMock(),
            "state": MagicMock(agent_id="test-agent-id", agent_name="TestAgent"),
        }

    @patch("strigoi.agents.base_agent._agent_graph", {"nodes": {}, "edges": []})
    def test_initialization(self, agent_config):
        agent = BaseAgent(config=agent_config)
        assert agent.agent_name == "TestAgent"
        assert agent.agent_id == "test-agent-id"

    @patch("strigoi.agents.base_agent._agent_graph", {"nodes": {}, "edges": []})
    def test_add_to_agents_graph(self, agent_config):
        BaseAgent(config=agent_config)
        # The initialization calls _add_to_agents_graph automatically

        from strigoi.agents.base_agent import _agent_graph

        assert "test-agent-id" in _agent_graph["nodes"]
        assert _agent_graph["nodes"]["test-agent-id"]["name"] == "TestAgent"
