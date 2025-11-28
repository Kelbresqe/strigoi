# Strigoi - AI Coding Agent Instructions

## Project Overview
Strigoi is an open-source autonomous AI security agent that performs penetration testing and vulnerability discovery. It uses a multi-agent architecture where specialized agents collaborate within Docker sandboxes to conduct security assessments.

## Architecture

### Core Components
```
strigoi/
├── agents/           # Agent implementations (BaseAgent → StrigoiAgent)
├── tools/            # Security tools (browser, terminal, proxy, python, etc.)
├── llm/              # LiteLLM integration and prompt handling
├── prompts/          # Jinja2 prompt modules by category
├── runtime/          # Docker sandbox management
├── interface/        # CLI and TUI (Textual-based)
└── telemetry/        # Execution tracing
```

### Agent System
- **BaseAgent** (`strigoi/agents/base_agent.py`): Core agent loop, state management, LLM integration
- **StrigoiAgent** (`strigoi/agents/StrigoiAgent/`): Main security agent with system prompt in Jinja2
- **AgentState** (`strigoi/agents/state.py`): Pydantic model tracking iteration, messages, actions
- Root agent acts as coordinator (uses `root_agent.jinja`), spawns specialized sub-agents

### Tool Registration Pattern
Tools are registered using the `@register_tool` decorator in `strigoi/tools/registry.py`:
```python
from strigoi.tools.registry import register_tool

@register_tool  # Runs in sandbox by default
def my_tool(param: str) -> dict[str, Any]:
    ...

@register_tool(sandbox_execution=False)  # Runs on host
def host_tool(agent_state: AgentState, ...) -> dict[str, Any]:
    ...
```

Each tool category has:
- `<tool>_actions.py` - Tool implementations
- `<tool>_actions_schema.xml` - XML schema for LLM tool definitions
- Supporting modules (e.g., `terminal_manager.py`, `browser/tab_manager.py`)

### Prompt Module System
Prompt modules in `strigoi/prompts/` enhance agents with specialized knowledge:
- Categories: `vulnerabilities/`, `frameworks/`, `technologies/`, `protocols/`, `cloud/`, `coordination/`
- Format: Jinja2 templates (`.jinja`) with XML-style structure
- Loaded dynamically via `prompt_modules` in `LLMConfig` (max 5 per agent)
- Access in templates: `{{ get_module('module_name') }}`

## Development Workflow

### Setup
```bash
make setup-dev          # Install deps + pre-commit hooks
export STRIGOI_LLM="openai/gpt-5"
export LLM_API_KEY="your-key"
```

### Commands
```bash
make check-all          # Format + lint + type-check + security
make test               # Run pytest
make test-cov           # Tests with coverage report
poetry run strigoi --target ./app  # Run locally
```

### Code Quality
- Python 3.12+ with strict mypy/pyright type checking
- Ruff for formatting/linting, bandit for security
- 100-char line limit, type hints required on all functions
- Pre-commit hooks enforce standards

## Key Patterns

### Adding a New Tool
1. Create `strigoi/tools/<tool_name>/` directory
2. Add `<tool>_actions.py` with `@register_tool` functions
3. Create `<tool>_actions_schema.xml` for LLM tool definitions
4. Export in `strigoi/tools/<tool_name>/__init__.py`
5. Add renderer in `strigoi/interface/tool_components/` for TUI display

### Sandbox Execution
- Tools with `sandbox_execution=True` (default) run inside Docker container
- Container image set via `STRIGOI_IMAGE` environment variable
- Host-side tools (agent coordination, reporting) use `sandbox_execution=False`
- Sandbox communication via HTTP to tool server with bearer token auth

### LLM Configuration
```python
from strigoi.llm.config import LLMConfig

config = LLMConfig(
    model_name="openai/gpt-5",      # LiteLLM model identifier
    prompt_modules=["sql_injection", "xss"],  # Specialized knowledge
    enable_prompt_caching=True,
    timeout=600
)
```

### Agent Communication
- Sub-agents created via `create_agent` tool with task delegation
- Agents share `/workspace` directory and proxy history
- Messages passed via `send_agent_message` tool
- Sub-agents finish with `agent_finish`, root with `finish_scan`

## Environment Variables
| Variable | Purpose |
|----------|---------|
| `STRIGOI_LLM` | LiteLLM model name (required) |
| `LLM_API_KEY` | Provider API key |
| `LLM_API_BASE` | Custom API endpoint |
| `PERPLEXITY_API_KEY` | Enables web_search tool |
| `STRIGOI_IMAGE` | Custom sandbox Docker image |

## File Conventions
- Agent prompts: `strigoi/agents/<AgentName>/system_prompt.jinja`
- Tool schemas: `strigoi/tools/<tool>/<tool>_actions_schema.xml`
- TUI styles: `strigoi/interface/assets/tui_styles.tcss`
- Prompt modules: `strigoi/prompts/<category>/<module>.jinja`
- Scan results: `strigoi_runs/<run-name>/`
