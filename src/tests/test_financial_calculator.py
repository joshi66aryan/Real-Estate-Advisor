"""
Unit tests for Financial Calculator - ensuring financial accuracy
"""

import pytest
import json
from ..tools.financial_calculator import FinancialCalculatorTool


class TestFinancialCalculator:
    """Test suite for financial calculations"""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance"""
        # Shared fixture keeps tool initialization consistent across tests.
        return FinancialCalculatorTool()
    
    def test_cap_rate_calculation(self, calculator):
        """Test Cap Rate formula: (Annual Rent - Operating Expenses) / Purchase Price × 100"""
        result = calculator._run(
            purchase_price=500000,
            annual_rent=48000,  # $4,000/month
            annual_operating_expenses=12000,
            down_payment_percent=25,
            interest_rate=7.0
        )
        
        data = json.loads(result)
        
        # Manual calculation: (48000 - 12000) / 500000 * 100 = 7.2%
        expected_cap_rate = 7.2
        actual_cap_rate = data['core_metrics']['cap_rate']
        
        assert abs(actual_cap_rate - expected_cap_rate) < 0.01, f"Cap Rate should be {expected_cap_rate}%, got {actual_cap_rate}%"
        print(f"✓ Cap Rate test passed: {actual_cap_rate}%")
    
    def test_cash_on_cash_return(self, calculator):
        """Test Cash-on-Cash Return calculation"""
        result = calculator._run(
            purchase_price=400000,
            annual_rent=36000,
            annual_operating_expenses=10000,
            down_payment_percent=20,  # $80,000 down
            interest_rate=7.5,
            closing_costs_percent=3.0  # $12,000
        )
        
        data = json.loads(result)
        
        # Total cash invested = $80,000 + $12,000 = $92,000
        # NOI = $36,000 - $10,000 = $26,000
        # Annual debt service on $320,000 at 7.5% for 30 years ≈ $26,880
        # Cash flow = $26,000 - $26,880 = -$880 (negative)
        # CoC = -$880 / $92,000 * 100 ≈ -0.96%
        
        actual_coc = data['core_metrics']['cash_on_cash_return']
        assert actual_coc < 0, "This property should have negative cash flow"
        print(f"✓ Cash-on-Cash test passed: {actual_coc}%")
    
    def test_positive_cash_flow(self, calculator):
        """Test property with positive cash flow"""
        result = calculator._run(
            purchase_price=300000,
            annual_rent=36000,  # $3,000/month
            annual_operating_expenses=9000,
            down_payment_percent=25,
            interest_rate=6.5
        )
        
        data = json.loads(result)
        
        monthly_cf = data['cash_flow_analysis']['monthly_cash_flow']
        assert monthly_cf > 0, "This property should have positive cash flow"
        print(f"✓ Positive cash flow test passed: ${monthly_cf:.2f}/month")
    
    def test_dscr_calculation(self, calculator):
        """Test Debt Service Coverage Ratio"""
        result = calculator._run(
            purchase_price=500000,
            annual_rent=60000,
            annual_operating_expenses=15000,
            down_payment_percent=20,
            interest_rate=7.0
        )
        
        data = json.loads(result)
        
        dscr = data['core_metrics']['dscr']
        # DSCR = NOI / Annual Debt Service
        # Good DSCR is typically > 1.25
        assert dscr > 0, "DSCR should be positive"
        print(f"✓ DSCR test passed: {dscr:.2f}")
    
    def test_sensitivity_analysis(self, calculator):
        """Test sensitivity scenarios"""
        # Ensures downside scenarios move in the expected direction vs base case.
        result = calculator._run(
            purchase_price=450000,
            annual_rent=42000,
            annual_operating_expenses=11000,
            down_payment_percent=25,
            interest_rate=7.25
        )
        
        data = json.loads(result)
        
        base_cf = data['cash_flow_analysis']['monthly_cash_flow']
        rent_decrease_cf = data['sensitivity_analysis']['scenario_1_rent_decrease_10pct']['monthly_cash_flow']
        expense_increase_cf = data['sensitivity_analysis']['scenario_2_expenses_increase_15pct']['monthly_cash_flow']
        vacancy_cf = data['sensitivity_analysis']['scenario_3_vacancy_10pct']['monthly_cash_flow']
        
        # All scenarios should show lower cash flow than base
        assert rent_decrease_cf < base_cf, "Rent decrease should lower cash flow"
        assert expense_increase_cf < base_cf, "Expense increase should lower cash flow"
        assert vacancy_cf < base_cf, "Vacancy should lower cash flow"
        
        print(f"✓ Sensitivity analysis test passed")
        print(f"  Base: ${base_cf:.2f}/mo")
        print(f"  Rent -10%: ${rent_decrease_cf:.2f}/mo")
        print(f"  Expenses +15%: ${expense_increase_cf:.2f}/mo")
        print(f"  Vacancy 10%: ${vacancy_cf:.2f}/mo")
    
    def test_input_validation(self, calculator):
        """Test input validation"""
        # Test negative purchase price
        result = calculator._run(
            purchase_price=-100000,
            annual_rent=24000,
            annual_operating_expenses=6000,
            down_payment_percent=20,
            interest_rate=7.0
        )
        
        data = json.loads(result)
        assert 'error' in data, "Should return error for negative price"
        print(f"✓ Input validation test passed")
    
    def test_zero_interest_rate(self, calculator):
        """Test with zero interest rate (all cash purchase scenario)"""
        result = calculator._run(
            purchase_price=300000,
            annual_rent=30000,
            annual_operating_expenses=8000,
            down_payment_percent=100,  # All cash
            interest_rate=0.0
        )
        
        data = json.loads(result)
        
        # With no loan, cash flow should equal NOI
        noi = data['cash_flow_analysis']['net_operating_income']
        annual_cf = data['cash_flow_analysis']['annual_cash_flow']
        
        assert abs(noi - annual_cf) < 1, "With no loan, cash flow should equal NOI"
        print(f"✓ Zero interest rate test passed")
    
    def test_five_year_projection(self, calculator):
        """Test 5-year IRR projection"""
        result = calculator._run(
            purchase_price=400000,
            annual_rent=40000,
            annual_operating_expenses=12000,
            down_payment_percent=25,
            interest_rate=7.0,
            appreciation_rate=3.0,
            hold_period_years=5
        )
        
        data = json.loads(result)
        
        future_value = data['five_year_projection']['future_property_value']
        total_profit = data['five_year_projection']['total_profit']
        
        # Property should appreciate
        assert future_value > 400000, "Property should appreciate over 5 years"
        print(f"✓ Five-year projection test passed")
        print(f"  Future value: ${future_value:,.2f}")
        print(f"  Total profit: ${total_profit:,.2f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
