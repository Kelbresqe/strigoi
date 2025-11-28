from unittest.mock import MagicMock, patch

import pytest

from strigoi.llm.llm import LLM, LLMConfig


class TestLLM:
    @pytest.fixture
    def llm_config(self):
        return LLMConfig(model="openai/gpt-4", api_key="test-key", timeout=30)

    def test_initialization(self, llm_config):
        llm = LLM(config=llm_config, agent_name="TestAgent", agent_id="test-id")
        assert llm.config == llm_config
        assert llm.agent_name == "TestAgent"
        assert llm.agent_id == "test-id"

    def test_build_identity_message(self, llm_config):
        llm = LLM(config=llm_config, agent_name="TestAgent", agent_id="test-id")
        identity_msg = llm._build_identity_message()
        assert identity_msg["role"] == "system"
        assert "TestAgent" in identity_msg["content"]
        assert "test-id" in identity_msg["content"]

    @patch("strigoi.llm.llm.litellm.completion")
    def test_generate_success(self, mock_completion, llm_config):
        # Mock the completion response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        mock_completion.return_value = mock_response

        llm = LLM(config=llm_config)
        history = [{"role": "user", "content": "Hello"}]

        response = llm.generate(conversation_history=history)

        assert response.content == "Test response"
        assert llm.usage_stats().input_tokens == 10
        assert llm.usage_stats().output_tokens == 5
