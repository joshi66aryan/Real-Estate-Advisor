"""
Integration tests for the crew
"""

import pytest
import os
from dotenv import load_dotenv
from ..crews.crew import InvestmentAdvisorCrew

load_dotenv()


class TestCrew:
    """Test suite for crew integration"""
    
    @pytest.fixture
    def sample_property(self):
        """Sample property data for testing"""
        return {
            'property_address': '123 Test Street, Test City, TX 12345',
            'purchase_price': 350000,
            'square_footage': 1600,
            'bedrooms': 3,
            'bathrooms': 2,
            'property_type': 'Single Family Home',
            'year_built': 2010,
            'estimated_monthly_rent': 2800,
            'annual_operating_expenses': 10000,
            'down_payment_percent': 25,
            'interest_rate': 7.0,
            'loan_term_years': 30,
            'investment_strategy': 'Passive Income'
        }
    
    def test_crew_initialization(self):
        """Test that crew initializes properly"""
        # Verifies constructor-level wiring (env/config/tool setup) is valid.
        crew_instance = InvestmentAdvisorCrew()
        assert crew_instance is not None
        print("✓ Crew initialization test passed")
    
    def test_agents_created(self):
        """Test that all agents are created"""
        # Guards against accidental agent removal or registration breakage.
        crew_instance = InvestmentAdvisorCrew()
        crew = crew_instance.crew()
        
        assert len(crew.agents) == 4, "Should have 4 agents"
        print("✓ All agents created test passed")
    
    def test_tasks_created(self):
        """Test that all tasks are created"""
        # Guards against task wiring regressions in Crew configuration.
        crew_instance = InvestmentAdvisorCrew()
        crew = crew_instance.crew()
        
        assert len(crew.tasks) == 4, "Should have 4 tasks"
        print("✓ All tasks created test passed")
    
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="Requires OPENAI_API_KEY"
    )
    def test_crew_execution(self, sample_property):
        """Test full crew execution (integration test)"""
        import time
        
        crew_instance = InvestmentAdvisorCrew()
        
        start_time = time.time()
        result = crew_instance.crew().kickoff(inputs=sample_property)
        execution_time = time.time() - start_time
        
        assert result is not None, "Should return a result"
        assert execution_time < 60, "Should complete within 60 seconds"
        
        print(f"✓ Crew execution test passed")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  Result length: {len(str(result))} characters")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
