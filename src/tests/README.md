# src/tests

Automated tests for financial logic, guardrails, and crew wiring.

## Files and Logic

- `test_financial_calculator.py`
  - Validates core finance formulas and scenarios.
  - Covers cap rate, cash flow behavior, DSCR, sensitivity, and input validation.

- `test_guardrails.py`
  - Validates each guardrail function for pass/fail behavior.
  - Confirms CrewAI-compatible tuple-based outputs.

- `test_crew.py`
  - Validates crew construction and basic agent/task counts.
  - Includes optional integration execution test path.

- `conftest.py`
  - Shared pytest fixtures/test setup.

- `__init__.py`
  - Test package marker.
