# src/crews

CrewAI orchestration layer: agents, tasks, guardrails, and runtime crew assembly.

## Files and Logic

- `crew.py`
  - Defines `InvestmentAdvisorCrew` via `@CrewBase`.
  - Creates shared LLM config and feature flags (memory, tool toggles, iteration limits, output token caps).
  - Builds research tools list based on env toggles.
  - Defines 5 agents and 5 tasks.
  - Applies task-level guardrails.
  - Creates sequential `Crew` instance.

- `__init__.py`
  - Package marker (currently placeholder text).

## Subdirectories

- `config/`: YAML agent/task prompts.
- `guardrails/`: programmatic guardrail functions used by tasks.
