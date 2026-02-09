"""
Financial Calculator Tool - Deterministic microservice for accurate calculations
Implements the required financial formulas with validation
"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import json


class FinancialCalculatorInput(BaseModel):
    """Input schema for Financial Calculator"""
    purchase_price: float = Field(..., description="Property purchase price")
    annual_rent: float = Field(..., description="Annual rental income")
    annual_operating_expenses: float = Field(..., description="Annual operating expenses (tax, insurance, maintenance, vacancy, management)")
    down_payment_percent: float = Field(..., description="Down payment percentage (e.g., 25 for 25%)")
    interest_rate: float = Field(..., description="Annual interest rate percentage (e.g., 7.5 for 7.5%)")
    loan_term_years: int = Field(default=30, description="Loan term in years")
    appreciation_rate: float = Field(default=3.0, description="Expected annual appreciation rate percentage")
    hold_period_years: int = Field(default=5, description="Expected hold period in years")
    closing_costs_percent: float = Field(default=3.0, description="Closing costs as percentage of purchase price")
    selling_costs_percent: float = Field(default=6.0, description="Selling costs as percentage of sale price")


class FinancialCalculatorTool(BaseTool):
    # Tool metadata is used by CrewAI when deciding which tool to invoke.
    name: str = "Financial Calculator"
    description: str = (
        "Calculates key real estate investment metrics with validated formulas. "
        "Returns Cap Rate, Cash-on-Cash Return, IRR, monthly cash flow, DSCR, "
        "break-even occupancy, and sensitivity analysis. "
        "Input must be a JSON string with property financial details."
    )
    args_schema: Type[BaseModel] = FinancialCalculatorInput
    
    def _run(
        self,
        purchase_price: float,
        annual_rent: float,
        annual_operating_expenses: float,
        down_payment_percent: float,
        interest_rate: float,
        loan_term_years: int = 30,
        appreciation_rate: float = 3.0,
        hold_period_years: int = 5,
        closing_costs_percent: float = 3.0,
        selling_costs_percent: float = 6.0
    ) -> str:
        """
        Execute financial calculations
        
        Returns:
            JSON string with all calculated metrics
        """
        try:
            # Input validation
            if purchase_price <= 0:
                return json.dumps({"error": "Purchase price must be positive"})
            if annual_rent < 0:
                return json.dumps({"error": "Annual rent cannot be negative"})
            if annual_operating_expenses < 0:
                return json.dumps({"error": "Operating expenses cannot be negative"})
            if not 0 <= down_payment_percent <= 100:
                return json.dumps({"error": "Down payment percent must be between 0 and 100"})
            if interest_rate < 0:
                return json.dumps({"error": "Interest rate cannot be negative"})
            
            # === CORE CALCULATIONS ===
            # Sequence is ordered so intermediate values (NOI, debt service) can be reused.
            
            # 1. Net Operating Income (NOI)
            noi = annual_rent - annual_operating_expenses
            
            # 2. Cap Rate
            # Formula: (Annual Rent - Operating Expenses) / Purchase Price × 100
            cap_rate = (noi / purchase_price) * 100 if purchase_price > 0 else 0
            
            # 3. Loan Calculations
            down_payment_decimal = down_payment_percent / 100
            down_payment = purchase_price * down_payment_decimal
            loan_amount = purchase_price - down_payment
            
            # Monthly mortgage payment (Principal & Interest)
            monthly_interest_rate = (interest_rate / 100) / 12
            num_payments = loan_term_years * 12
            
            if monthly_interest_rate > 0:
                monthly_payment = loan_amount * (
                    monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments
                ) / ((1 + monthly_interest_rate) ** num_payments - 1)
            else:
                monthly_payment = loan_amount / num_payments if num_payments > 0 else 0
            
            annual_debt_service = monthly_payment * 12
            
            # 4. Cash Flow
            annual_cash_flow = noi - annual_debt_service
            monthly_cash_flow = annual_cash_flow / 12
            
            # 5. Cash-on-Cash Return
            closing_costs = purchase_price * (closing_costs_percent / 100)
            total_cash_invested = down_payment + closing_costs
            
            cash_on_cash_return = (annual_cash_flow / total_cash_invested) * 100 if total_cash_invested > 0 else 0
            
            # 6. Debt Service Coverage Ratio (DSCR)
            dscr = noi / annual_debt_service if annual_debt_service > 0 else 0
            
            # 7. Break-Even Occupancy Rate
            total_monthly_expenses = (annual_debt_service + annual_operating_expenses) / 12
            monthly_rent = annual_rent / 12
            break_even_occupancy = (total_monthly_expenses / monthly_rent) * 100 if monthly_rent > 0 else 0
            
            # 8. IRR Calculation (5-year projection)
            # Calculate future property value
            future_value = purchase_price * ((1 + appreciation_rate / 100) ** hold_period_years)
            
            # Calculate remaining loan balance
            payments_made = hold_period_years * 12
            remaining_payments = num_payments - payments_made
            
            if monthly_interest_rate > 0 and remaining_payments > 0:
                remaining_balance = loan_amount * (
                    ((1 + monthly_interest_rate) ** num_payments - (1 + monthly_interest_rate) ** payments_made) /
                    ((1 + monthly_interest_rate) ** num_payments - 1)
                )
            else:
                remaining_balance = max(0, loan_amount * (remaining_payments / num_payments)) if num_payments > 0 else 0
            
            # Equity at sale
            equity_at_sale = future_value - remaining_balance
            
            # Net sale proceeds
            selling_costs = future_value * (selling_costs_percent / 100)
            net_sale_proceeds = equity_at_sale - selling_costs
            
            # Total returns
            total_cash_flows = annual_cash_flow * hold_period_years
            total_profit = total_cash_flows + net_sale_proceeds - total_cash_invested
            total_return_pct = (total_profit / total_cash_invested) * 100 if total_cash_invested > 0 else 0
            
            # Approximate IRR (annualized)
            irr_estimate = total_return_pct / hold_period_years
            
            # === SENSITIVITY ANALYSIS ===
            
            # Scenario 1: 10% rent decrease
            reduced_rent = annual_rent * 0.9
            reduced_noi = reduced_rent - annual_operating_expenses
            reduced_cash_flow = reduced_noi - annual_debt_service
            reduced_monthly_cf = reduced_cash_flow / 12
            
            # Scenario 2: 15% expense increase
            increased_expenses = annual_operating_expenses * 1.15
            increased_exp_noi = annual_rent - increased_expenses
            increased_exp_cash_flow = increased_exp_noi - annual_debt_service
            increased_exp_monthly_cf = increased_exp_cash_flow / 12
            
            # Scenario 3: 10% vacancy impact (10% reduction in effective rent)
            vacancy_rent = annual_rent * 0.9
            vacancy_noi = vacancy_rent - annual_operating_expenses
            vacancy_cash_flow = vacancy_noi - annual_debt_service
            vacancy_monthly_cf = vacancy_cash_flow / 12
            
            # === COMPILE RESULTS ===
            # Response is normalized into JSON so agents can parse/use it reliably.
            
            results = {
                "status": "success",
                "core_metrics": {
                    "cap_rate": round(cap_rate, 2),
                    "cash_on_cash_return": round(cash_on_cash_return, 2),
                    "irr_estimate": round(irr_estimate, 2),
                    "dscr": round(dscr, 2),
                    "break_even_occupancy_pct": round(break_even_occupancy, 2)
                },
                "cash_flow_analysis": {
                    "annual_gross_rent": round(annual_rent, 2),
                    "annual_operating_expenses": round(annual_operating_expenses, 2),
                    "net_operating_income": round(noi, 2),
                    "annual_debt_service": round(annual_debt_service, 2),
                    "annual_cash_flow": round(annual_cash_flow, 2),
                    "monthly_cash_flow": round(monthly_cash_flow, 2)
                },
                "investment_summary": {
                    "purchase_price": round(purchase_price, 2),
                    "down_payment": round(down_payment, 2),
                    "closing_costs": round(closing_costs, 2),
                    "total_cash_invested": round(total_cash_invested, 2),
                    "loan_amount": round(loan_amount, 2),
                    "monthly_mortgage_payment": round(monthly_payment, 2)
                },
                "five_year_projection": {
                    "total_cash_flows": round(total_cash_flows, 2),
                    "future_property_value": round(future_value, 2),
                    "remaining_loan_balance": round(remaining_balance, 2),
                    "equity_at_sale": round(equity_at_sale, 2),
                    "selling_costs": round(selling_costs, 2),
                    "net_sale_proceeds": round(net_sale_proceeds, 2),
                    "total_profit": round(total_profit, 2),
                    "total_return_pct": round(total_return_pct, 2)
                },
                "sensitivity_analysis": {
                    "scenario_1_rent_decrease_10pct": {
                        "annual_cash_flow": round(reduced_cash_flow, 2),
                        "monthly_cash_flow": round(reduced_monthly_cf, 2)
                    },
                    "scenario_2_expenses_increase_15pct": {
                        "annual_cash_flow": round(increased_exp_cash_flow, 2),
                        "monthly_cash_flow": round(increased_exp_monthly_cf, 2)
                    },
                    "scenario_3_vacancy_10pct": {
                        "annual_cash_flow": round(vacancy_cash_flow, 2),
                        "monthly_cash_flow": round(vacancy_monthly_cf, 2)
                    }
                },
                "formulas_used": {
                    "cap_rate": "(Annual Rent - Operating Expenses) / Purchase Price × 100",
                    "cash_on_cash": "Annual Cash Flow / Total Cash Invested × 100",
                    "noi": "Annual Rent - Operating Expenses",
                    "dscr": "NOI / Annual Debt Service"
                }
            }
            
            return json.dumps(results, indent=2)
            
        except Exception as e:
            # Guarded error payload prevents raw stack traces from leaking to agent output.
            return json.dumps({
                "status": "error",
                "error": f"Calculation error: {str(e)}"
            })
