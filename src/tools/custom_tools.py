"""
Custom tool initialization
"""

from .financial_calculator import FinancialCalculatorTool

def get_financial_calculator():
    """Get instance of Financial Calculator tool"""
    # Factory function keeps tool construction in one place for easy swapping/mocking.
    return FinancialCalculatorTool()
