# src/crews/config

Prompt/configuration files for CrewAI agents and tasks.

## Files and Logic

- `agents.yaml`
  - Defines role, goal, and backstory for each agent.
  - Agents:
    - data integration specialist
    - financial modeling analyst
    - risk assessment expert
    - strategy alignment advisor
    - investment advisor

- `tasks.yaml`
  - Defines task descriptions, expected outputs, context chaining, and required placeholders.
  - Encodes analysis requirements for each stage.
  - Final advisory task includes required `Sources` section format.
  - Context links enforce information flow between tasks.

## Notes

- Placeholder variables (e.g., `{purchase_price}`, `{investment_strategy}`) must exist in kickoff inputs.
- If a placeholder is missing, CrewAI interpolation fails before task execution.
