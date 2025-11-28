import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_llm():
    """Mock the LLM class to prevent actual API calls."""
    with pytest.MonkeyPatch.context() as m:
        mock = MagicMock()
        m.setattr("strigoi.llm.LLM", mock)
        yield mock


@pytest.fixture
def mock_docker():
    """Mock the Docker client."""
    with pytest.MonkeyPatch.context() as m:
        mock = MagicMock()
        m.setattr("docker.from_env", mock)
        yield mock
