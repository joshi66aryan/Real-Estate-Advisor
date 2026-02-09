# src

Core application package for the Real Estate Advisor.

## Files and Logic

- `main.py`
  - CLI entrypoint.
  - Validates required property fields and selected strategy.
  - Runs either:
    - full CrewAI pipeline, or
    - deterministic fast mode (when `FAST_MODE_ENABLED=true` and performance target <= 5s).
  - Prints final recommendation and execution metrics.

- `flow_manager.py`
  - Event-driven state machine for orchestration state tracking.
  - Defines states (`INITIALIZED`, `DATA_COLLECTION`, `FINANCIAL_ANALYSIS`, etc.) and decision points.
  - Provides branching metadata and audit-style flow event logs.

- `settings.py`
  - Central strategy thresholds and risk/recommendation constants.
  - Reads env vars for model keys (legacy fields still present).

- `__init__.py`
  - Package marker (currently minimal).

## Subdirectories

- `crews/`: Crew and task definitions.
- `tools/`: custom tools.
- `ui/`: Streamlit UI and orchestrator.
- `tests/`: test suite.
- `knowledge/`: text knowledge artifacts.
