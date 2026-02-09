# Real Estate Advisor

AI-powered real estate investment analysis system built with CrewAI. It combines deterministic financial calculations, multi-agent reasoning, safety guardrails, a CLI entrypoint, and a Streamlit UI.

## What This Project Does

- Analyzes a property using financial metrics (cap rate, cash flow, cash-on-cash, DSCR, break-even occupancy, 5-year projection).
- Runs a multi-agent workflow (data integration, financial modeling, strategy+risk alignment, final recommendation).
- Applies safety guardrails on the final recommendation task.
- Supports active web search via `SerperDevTool` (when `SERPER_API_KEY` is configured) to generate external citations.
- Supports a fast deterministic mode for strict low-latency responses (<= 5s target).

## Repository Structure

- `src/`: application code.
- `src/crews/`: CrewAI agent/task orchestration and guardrails wiring.
- `src/tools/`: custom deterministic tools (financial calculator).
- `src/ui/`: Streamlit UI and orchestrator layer.
- `src/tests/`: test suite.

## Architecture Overview

The system uses a layered architecture with deterministic finance logic plus optional multi-agent reasoning:

1. Entry Layer
- CLI: `src/main.py`
- UI: `src/ui/streamlit.py` -> `src/ui/orchestrator.py`

2. Orchestration Layer
- `src/ui/orchestrator.py` coordinates:
  - flow-state tracking (`src/flow_manager.py`)
  - preliminary deterministic metrics from the financial calculator
  - full CrewAI execution when applicable

3. Crew Layer
- `src/crews/crew.py` wires:
  - 4 agents (data, financial, strategy+risk, advisor)
  - 4 sequential tasks
  - guardrails on the final advisory task only
  - runtime controls (memory/tools/max iterations/token caps)

4. Prompt/Config Layer
- `src/crews/config/agents.yaml`: agent personas and role goals
- `src/crews/config/tasks.yaml`: task instructions, expected outputs, context chaining, source-citation format

5. Deterministic Tool Layer
- `src/tools/financial_calculator.py`: formula-based computation engine
- Produces cap rate, cash flow, CoC, DSCR, break-even occupancy, projection metrics, and sensitivity outputs

6. Safety Layer
- `src/crews/guardrails/safety_guardrails.py`
- Guardrails validate/reject unsafe claims and enforce risk/professional-consultation language

7. Test Layer
- `src/tests/` validates calculator accuracy, guardrails, and crew wiring

### Runtime Paths

- Fast deterministic path:
  - Triggered when `FAST_MODE_ENABLED=true` and `PERFORMANCE_TARGET_SECONDS<=5`
  - Uses calculator + rule-based recommendation from `src/main.py`
  - Designed for strict low-latency use

- Full multi-agent path:
  - CrewAI sequential execution with context passing across tasks
  - Better narrative depth, higher latency

## Download and Setup

1. Clone repository:
```bash
git clone <your-repo-url>
cd Real-Estate-Advisor
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables in `.env` (minimum):
```env
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL_NAME=gpt-4o-mini
PERFORMANCE_TARGET_SECONDS=60
FAST_MODE_ENABLED=true
SERPER_API_KEY=your_serper_key
```

Optional runtime flags:
```env
CREW_MEMORY_ENABLED=false
CREW_WEB_TOOLS_ENABLED=true
CREW_SCRAPE_TOOL_ENABLED=false
CREW_AGENT_MAX_ITER=4
OPENAI_MAX_OUTPUT_TOKENS=600
CREW_REQUIRE_EXTERNAL_SOURCES=true
CREW_MIN_EXTERNAL_SOURCE_URLS=1
FINAL_GUARDRAIL_MAX_RETRIES=5
```

Notes:
- `SERPER_API_KEY` enables active web search for research agents and the final advisor.
- `CREW_SCRAPE_TOOL_ENABLED=true` is optional; it adds page scraping in addition to search.
- If source enforcement is enabled, final output must include at least `CREW_MIN_EXTERNAL_SOURCE_URLS` URLs in `## Sources`.

## Run in CLI

```bash
source venv/bin/activate
python -m src.main
```

Notes:
- If `PERFORMANCE_TARGET_SECONDS<=5` and `FAST_MODE_ENABLED=true`, the app uses deterministic fast mode.
- Otherwise, it uses full CrewAI multi-agent execution.

## Run in Streamlit

```bash
source venv/bin/activate
./venv/bin/streamlit run src/ui/streamlit.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Try All Cases (Manual Testing)

Use the following complete input sets in Streamlit. Select the listed strategy in the sidebar for each run.

### Case 1: PASS (Passive Income)

- `property_address`: `456 Maple Street, Austin, TX 78701`
- `purchase_price`: `475000`
- `square_footage`: `1950`
- `bedrooms`: `3`
- `bathrooms`: `2.0`
- `property_type`: `Single Family Home`
- `year_built`: `2015`
- `estimated_monthly_rent`: `3400`
- `annual_operating_expenses`: `14000`
- `down_payment_percent`: `25`
- `interest_rate`: `7.25`
- `loan_term_years`: `30`
- Strategy: `Passive Income`

### Case 2: BUY (Aggressive Growth)

- `property_address`: `2201 East Ridge Dr, Austin, TX 78723`
- `purchase_price`: `300000`
- `square_footage`: `1650`
- `bedrooms`: `3`
- `bathrooms`: `2.0`
- `property_type`: `Single Family Home`
- `year_built`: `2012`
- `estimated_monthly_rent`: `3600`
- `annual_operating_expenses`: `9000`
- `down_payment_percent`: `30`
- `interest_rate`: `6.5`
- `loan_term_years`: `30`
- Strategy: `Aggressive Growth`

### Case 3: HOLD FOR NEGOTIATION (Fix & Flip)

- `property_address`: `118 Cedar Park Ln, Austin, TX 78741`
- `purchase_price`: `500000`
- `square_footage`: `2100`
- `bedrooms`: `4`
- `bathrooms`: `2.5`
- `property_type`: `Single Family Home`
- `year_built`: `2008`
- `estimated_monthly_rent`: `3400`
- `annual_operating_expenses`: `14000`
- `down_payment_percent`: `50`
- `interest_rate`: `6.5`
- `loan_term_years`: `30`
- Strategy: `Fix & Flip`

### Recommended Test Matrix

1. Run each case with its matching strategy above.
2. Re-run each case with a different strategy to observe alignment/recommendation changes.
3. Compare fast mode vs full crew mode:
   - Fast mode: `PERFORMANCE_TARGET_SECONDS=5`, `FAST_MODE_ENABLED=true`
   - Full mode: `PERFORMANCE_TARGET_SECONDS=60`, `FAST_MODE_ENABLED=false`

## Testing

Run all tests:
```bash
./venv/bin/python -m pytest -q
```

Targeted examples:
```bash
./venv/bin/python -m pytest -q src/tests/test_financial_calculator.py
./venv/bin/python -m pytest -q src/tests/test_guardrails.py
./venv/bin/python -m pytest -q src/tests/test_crew.py
```

### Test Scope Explained

- `src/tests/test_financial_calculator.py`
  - Verifies deterministic finance formulas and validation behavior.
  - Use when changing `src/tools/financial_calculator.py`.

- `src/tests/test_guardrails.py`
  - Verifies guardrail pass/fail contract and policy checks.
  - Use when changing `src/crews/guardrails/safety_guardrails.py`.

- `src/tests/test_crew.py`
  - Verifies crew wiring (agents/tasks initialization) and integration path.
  - Use when changing `src/crews/crew.py` or task/agent config.

### Useful Test Commands

Run with verbose output:
```bash
./venv/bin/python -m pytest -v
```

Run a single test function:
```bash
./venv/bin/python -m pytest -q src/tests/test_financial_calculator.py::TestFinancialCalculator::test_cap_rate_calculation
```

Run only tests matching a keyword:
```bash
./venv/bin/python -m pytest -q -k \"guardrail\"
```

Run marker-filtered tests (if you use markers):
```bash
./venv/bin/python -m pytest -q -m \"not slow\"
```

## Pros and Cons

### Pros

- Deterministic financial core (`FinancialCalculatorTool`) for reproducible metrics.
- Multi-agent design separates responsibilities (data, finance, risk, strategy, synthesis).
- Final-task guardrails enforce safer, compliance-oriented language.
- Active web search support enables external source citation in reports.
- Fast mode provides practical SLA path for strict latency requirements.
- Streamlit interface makes manual testing and demos straightforward.

### Cons

- Full multi-agent sequential flow is naturally slower than single-model deterministic pipelines.
- Output quality can vary in full LLM mode due to prompt/runtime variability.
- Prompt/task templates are large and can increase token usage and latency.
- External research tool reliability depends on network/API availability.
- Several modules still include template/placeholder remnants and can be further cleaned.
