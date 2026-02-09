# src/tools

Custom tool layer used by agents.

## Files and Logic

- `financial_calculator.py`
  - Deterministic finance engine implemented as a CrewAI `BaseTool`.
  - Validates inputs and computes:
    - NOI
    - cap rate
    - mortgage/debt service
    - annual/monthly cash flow
    - cash-on-cash return
    - DSCR
    - break-even occupancy
    - 5-year projection and IRR estimate
    - sensitivity scenarios
  - Returns structured JSON as string.

- `custom_tools.py`
  - Convenience factory for `FinancialCalculatorTool`.

- `__init__.py`
  - Re-exports tool and factory for cleaner imports.
