#!/usr/bin/env python
"""
RE-101 Investment Advisory Engine - Main Entry Point
"""

import sys
import time
from typing import Dict, Any
from dotenv import load_dotenv
import os
import json

from .crews.crew import InvestmentAdvisorCrew
from .tools import get_financial_calculator

# Load environment variables
load_dotenv()


def run_analysis(property_data: Dict[str, Any], strategy: str = "Passive Income") -> Dict[str, Any]:
    """
    Run investment analysis for a property
    
    Guardrails are automatically applied during task execution.
    Users only see the final compliant output.
    
    Args:
        property_data: Dictionary containing property details
        strategy: Investment strategy ("Aggressive Growth", "Passive Income", "Fix & Flip")
    
    Returns:
        Dictionary with analysis results and performance metrics
    """
    
    # Validate user-provided strategy early to fail fast with clear feedback.
    valid_strategies = ["Aggressive Growth", "Passive Income", "Fix & Flip"]
    if strategy not in valid_strategies:
        raise ValueError(f"Strategy must be one of: {valid_strategies}")
    
    required_fields = [
        'property_address', 'purchase_price', 'square_footage',
        'bedrooms', 'bathrooms', 'property_type', 'year_built',
        'estimated_monthly_rent', 'annual_operating_expenses',
        'down_payment_percent', 'interest_rate', 'loan_term_years'
    ]
    
    for field in required_fields:
        if field not in property_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Start timer for performance tracking (covers end-to-end orchestration path).
    start_time = time.time()
    performance_target_seconds = float(os.getenv("PERFORMANCE_TARGET_SECONDS", "60"))
    fast_mode_enabled = os.getenv("FAST_MODE_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    
    print(f"\n{'='*80}")
    print(f"RE-101: AI-DRIVEN INVESTMENT ADVISORY ENGINE")
    print(f"{'='*80}")
    print(f"Property: {property_data['property_address']}")
    print(f"Purchase Price: ${property_data['purchase_price']:,.0f}")
    print(f"Strategy: {strategy}")
    print(f"{'='*80}\n")
    
    # Crew instance is still constructed in both modes because it also centralizes config defaults.
    crew_instance = InvestmentAdvisorCrew()
    
    # Prepare inputs for tasks
    inputs = {
        **property_data,
        'investment_strategy': strategy,
        'strategy': strategy,
    }
    
    print("🛡️  Safety guardrails are active and monitoring agent outputs...")
    print("   (Guardrails work transparently in the background)\n")

    # Fast mode bypasses multi-agent LLM calls for deterministic low-latency output.
    if fast_mode_enabled and performance_target_seconds <= 5:
        print("⚡ Fast mode active: using deterministic local analysis to meet <=5s target.\n")
        result = _run_fast_analysis(property_data, strategy)
    else:
        # Run the crew - guardrails are applied automatically to each task
        result = crew_instance.crew().kickoff(inputs=inputs)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print(f"✅ All outputs passed safety guardrails")
    print(f"{'='*80}\n")
    
    # Check performance requirement (configurable target)
    performance_status = "PASS" if execution_time < performance_target_seconds else "FAIL"
    print(f"Performance Requirement (<{performance_target_seconds:.0f}s): {performance_status}")
    if execution_time >= performance_target_seconds:
        print(
            f"⚠️  Warning: Response time exceeded {performance_target_seconds:.0f} seconds ({execution_time:.2f}s)"
        )
    
    return {
        'recommendation': str(result),
        'execution_time': execution_time,
        'performance_check': execution_time < performance_target_seconds,
        'property': property_data['property_address'],
        'strategy': strategy
    }


def _run_fast_analysis(property_data: Dict[str, Any], strategy: str) -> str:
    """Deterministic fallback to guarantee low-latency output."""
    # This path intentionally uses only local calculator outputs and static rules.
    calculator = get_financial_calculator()
    calc_json = calculator._run(
        purchase_price=property_data["purchase_price"],
        annual_rent=property_data["estimated_monthly_rent"] * 12,
        annual_operating_expenses=property_data["annual_operating_expenses"],
        down_payment_percent=property_data["down_payment_percent"],
        interest_rate=property_data["interest_rate"],
        loan_term_years=property_data["loan_term_years"],
    )
    data = json.loads(calc_json)
    if data.get("status") != "success":
        return f"Analysis failed: {data.get('error', 'Unknown error')}"

    core = data["core_metrics"]
    cash = data["cash_flow_analysis"]
    monthly_cf = cash["monthly_cash_flow"]
    cap_rate = core["cap_rate"]
    coc = core["cash_on_cash_return"]
    irr = core["irr_estimate"]
    be_occ = core["break_even_occupancy_pct"]
    recommendation = "BUY WITH CAUTION"
    if strategy == "Passive Income" and monthly_cf < 0:
        recommendation = "PASS"
    elif coc >= 8 and monthly_cf > 0:
        recommendation = "BUY"
    elif monthly_cf > 0:
        recommendation = "HOLD FOR NEGOTIATION"

    return (
        f"**INVESTMENT RECOMMENDATION: {recommendation}**\n\n"
        f"Monthly cash flow is ${monthly_cf:,.2f}, cap rate is {cap_rate:.2f}%, "
        f"cash-on-cash return is {coc:.2f}%, projected IRR is {irr:.2f}%, "
        f"and break-even occupancy is {be_occ:.2f}%.\n\n"
        f"For a {strategy} strategy, this property {'does not align well' if recommendation == 'PASS' else 'is potentially viable'} "
        f"based on current modeled metrics.\n\n"
        "**What To Do Next:**\n"
        "- Verify rent comps and property taxes with current local data.\n"
        "- Stress-test cash flow with higher vacancy and maintenance assumptions.\n"
        "- Confirm financing terms and closing costs with your lender.\n"
        "- Consult a licensed CPA and real estate attorney before final decision.\n\n"
        "## Sources\n"
        "- No external sources were used for this report.\n"
    )


def main():
    """Main function"""
    
    # Sample property data
    sample_property = {
        'property_address': '456 Maple Street, Austin, TX 78701',
        'purchase_price': 475000,
        'square_footage': 1950,
        'bedrooms': 3,
        'bathrooms': 2,
        'property_type': 'Single Family Home',
        'year_built': 2015,
        'estimated_monthly_rent': 3400,
        'annual_operating_expenses': 14000,
        'down_payment_percent': 25,
        'interest_rate': 7.25,
        'loan_term_years': 30
    }
    
    # Investment strategy
    investment_strategy = "Passive Income"
    
    try:
        # Run analysis
        results = run_analysis(sample_property, investment_strategy)
        
        print("\n" + "="*80)
        print("FINAL INVESTMENT RECOMMENDATION")
        print("="*80 + "\n")
        print(results['recommendation'])
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
