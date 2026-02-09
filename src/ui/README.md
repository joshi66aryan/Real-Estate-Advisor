# src/ui

User interface and orchestration bridge for interactive analysis.

## Files and Logic

- `streamlit.py`
  - Streamlit app entrypoint.
  - Collects only required agent input fields.
  - Passes form data to orchestrator and renders recommendation + key metrics.
  - Shows response-time metric and status.

- `orchestrator.py`
  - Integrates flow manager + crew execution.
  - Runs preliminary deterministic calculations first.
  - Executes flow transitions, checks if human input is required.
  - If flow reaches final state, runs full crew and returns combined result payload.

- `__init__.py`
  - Package marker.
