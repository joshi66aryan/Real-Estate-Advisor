# src/crews/guardrails

Safety/compliance guardrails applied to task outputs.

## Files and Logic

- `safety_guardrails.py`
  - Implements `InvestmentAdvisoryGuardrails` static methods.
  - Normalizes TaskOutput/string input to text.
  - Returns CrewAI-compatible guardrail tuples: `(success: bool, payload)`.
  - Guardrails include:
    - no guaranteed returns
    - no absolute certainty
    - analysis-not-advice framing
    - no manipulation tactics
    - realistic projections
    - risk acknowledgment requirement
    - professional consultation requirement
  - Exposes helper functions returning guardrail sets per task type.

- `__init__.py`
  - Re-exports guardrail classes/functions for clean imports from `crews.crew`.
