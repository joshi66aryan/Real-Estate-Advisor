"""
Tests for safety guardrails
Tests individual guardrail functions as they would be used in CrewAI tasks
"""

import pytest
from ..crews.guardrails import (
    InvestmentAdvisoryGuardrails,
    get_all_investment_guardrails,
    get_final_recommendation_guardrails,
)


class TestSafetyGuardrails:
    """Test suite for safety guardrails"""

    @staticmethod
    def _check(result):
        # Helper keeps tuple unpacking explicit in each assertion block.
        success, payload = result
        return success, payload
    
    def test_guaranteed_returns_rejection(self):
        """Test that guaranteed return claims are rejected"""
        
        bad_texts = [
            "This property will definitely make you $50,000 per year guaranteed.",
            "You are guaranteed to earn 15% returns on this investment.",
            "This is a risk-free investment that promises steady profits.",
            "You can't lose money on this deal, it's guaranteed."
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.no_guaranteed_returns
        
        for text in bad_texts:
            success, payload = self._check(guardrail(text))
            assert not success, f"Should reject: {text[:50]}..."
            assert "GUARDRAIL VIOLATION" in payload
            print(f"✓ Rejected guaranteed returns in: {text[:50]}...")
    
    def test_guaranteed_returns_approval(self):
        """Test that appropriate language passes"""
        
        good_texts = [
            "This property has the potential to generate approximately $50,000 per year.",
            "Based on current market conditions, estimated returns could be around 15%.",
            "The analysis suggests this property may provide steady income.",
            "Historical data indicates properties in this area have appreciated by 5-8% annually."
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.no_guaranteed_returns
        
        for text in good_texts:
            success, payload = self._check(guardrail(text))
            assert success, f"Should approve: {text[:50]}..."
            assert payload == text, f"Should approve: {text[:50]}..."
            print(f"✓ Approved safe language: {text[:50]}...")
    
    def test_absolute_certainty_rejection(self):
        """Test that absolute certainty claims are rejected"""
        
        bad_texts = [
            "Property values will definitely increase by 10% next year.",
            "This neighborhood always appreciates faster than the market.",
            "There is no way this property will lose value.",
            "This investment must become profitable within 2 years."
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.no_absolute_certainty
        
        for text in bad_texts:
            success, payload = self._check(guardrail(text))
            assert not success, f"Should reject: {text[:50]}..."
            assert "GUARDRAIL VIOLATION" in payload
            print(f"✓ Rejected certainty claim in: {text[:50]}...")
    
    def test_financial_advice_rejection(self):
        """Test that direct financial advice is rejected"""
        
        bad_texts = [
            "I recommend that you buy this property immediately.",
            "You should invest in this property right now.",
            "You must purchase this before the price goes up.",
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.provide_analysis_not_advice
        
        for text in bad_texts:
            success, payload = self._check(guardrail(text))
            assert not success, f"Should reject: {text[:50]}..."
            assert "GUARDRAIL VIOLATION" in payload
            print(f"✓ Rejected financial advice in: {text[:50]}...")
    
    def test_financial_advice_approval(self):
        """Test that analysis-based language passes"""
        
        good_texts = [
            "Based on the data, this property shows characteristics that align with your strategy.",
            "The analysis suggests this property demonstrates strong cash flow potential.",
            "Market conditions indicate this area has been experiencing growth.",
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.provide_analysis_not_advice
        
        for text in good_texts:
            success, payload = self._check(guardrail(text))
            assert success, f"Should approve: {text[:50]}..."
            assert payload == text, f"Should approve: {text[:50]}..."
            print(f"✓ Approved analysis language: {text[:50]}...")
    
    def test_manipulation_rejection(self):
        """Test that manipulation tactics are rejected"""
        
        bad_texts = [
            "Act now before it's too late! This deal won't last!",
            "Don't wait or you'll miss this once-in-a-lifetime opportunity.",
            "Buy now or you'll regret it forever.",
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.no_manipulation_tactics
        
        for text in bad_texts:
            success, payload = self._check(guardrail(text))
            assert not success, f"Should reject: {text[:50]}..."
            assert "GUARDRAIL VIOLATION" in payload
            print(f"✓ Rejected manipulation in: {text[:50]}...")
    
    def test_unrealistic_projections_rejection(self):
        """Test that unrealistic return claims are rejected"""
        
        bad_texts = [
            "This property will generate 35% returns per year.",
            "You can expect 50% annual appreciation on this investment.",
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.realistic_projections
        
        for text in bad_texts:
            success, payload = self._check(guardrail(text))
            assert not success, f"Should reject: {text[:50]}..."
            assert "GUARDRAIL VIOLATION" in payload
            print(f"✓ Rejected unrealistic projection in: {text[:50]}...")
    
    def test_realistic_projections_approval(self):
        """Test that realistic projections pass"""
        
        good_texts = [
            "Historical data suggests 8-12% annual returns are possible in this market.",
            "The property may generate 10% cash-on-cash returns based on current conditions.",
        ]
        
        guardrail = InvestmentAdvisoryGuardrails.realistic_projections
        
        for text in good_texts:
            success, payload = self._check(guardrail(text))
            assert success, f"Should approve: {text[:50]}..."
            assert payload == text, f"Should approve: {text[:50]}..."
            print(f"✓ Approved realistic projection: {text[:50]}...")
    
    def test_risk_acknowledgment_requirement(self):
        """Test that long outputs must acknowledge risk"""
        
        # Long text without risk acknowledgment
        bad_text = """This property shows excellent fundamentals with strong cash flow 
        potential. The financial metrics are favorable and the location is ideal. 
        The neighborhood is growing and appreciation trends are positive. This appears 
        to be a solid investment opportunity that aligns well with your passive income 
        strategy. The analysis indicates favorable returns and the market conditions 
        support this assessment. Consider moving forward with due diligence."""
        
        guardrail = InvestmentAdvisoryGuardrails.include_risk_acknowledgment
        
        result = guardrail(bad_text * 3)
        success, payload = self._check(result)
        assert not success, "Should reject long text without risk acknowledgment"
        assert "GUARDRAIL VIOLATION" in payload
        print("✓ Rejected output lacking risk acknowledgment")
        
        # Long text with risk acknowledgment
        good_text = """This property shows excellent fundamentals with strong cash flow 
        potential. The financial metrics are favorable and the location is ideal. 
        However, real estate investments carry inherent risks including market volatility, 
        unexpected expenses, and potential vacancy. Market conditions can change and actual 
        results may vary from projections. Consider these uncertainties in your decision."""
        
        success, payload = self._check(guardrail(good_text * 3))
        assert success, "Should approve text with risk acknowledgment"
        assert payload == good_text * 3, "Should approve text with risk acknowledgment"
        print("✓ Approved output with risk acknowledgment")
    
    def test_professional_consultation_requirement(self):
        """Test that final recommendations suggest professional consultation"""
        
        # Long recommendation without consultation guidance
        bad_text = """Based on comprehensive analysis, this property demonstrates strong 
        potential for your investment goals. The financial metrics align well with your 
        strategy and the market conditions are favorable. The risk assessment shows 
        manageable concerns and the strategy alignment is solid. This appears to be 
        a worthwhile opportunity that merits serious consideration for your portfolio."""
        
        guardrail = InvestmentAdvisoryGuardrails.require_professional_consultation
        
        success, payload = self._check(guardrail(bad_text * 3))
        assert not success, "Should reject without professional consultation guidance"
        assert "GUARDRAIL VIOLATION" in payload
        print("✓ Rejected output without consultation guidance")
        
        # Recommendation with consultation guidance
        good_text = """Based on comprehensive analysis, this property demonstrates strong 
        potential for your investment goals. The financial metrics align well with your 
        strategy. However, please conduct thorough due diligence including property 
        inspection and consult with qualified professionals including a real estate 
        attorney and CPA to review the tax implications before making your decision."""
        
        success, payload = self._check(guardrail(good_text * 3))
        assert success, "Should approve text with consultation guidance"
        assert payload == good_text * 3, "Should approve text with consultation guidance"
        print("✓ Approved output with consultation guidance")
    
    def test_guardrail_chain(self):
        """Test that multiple guardrails can be chained"""
        # Validates at least one guardrail catches obviously unsafe language.
        
        text = "You will definitely make guaranteed 40% returns! Buy now before it's too late!"
        
        # Apply all guardrails
        guardrails = get_all_investment_guardrails()
        
        payload = text
        for guardrail in guardrails:
            success, payload = self._check(guardrail(payload))
            if not success and "GUARDRAIL VIOLATION" in payload:
                print(f"✓ Guardrail caught violation: {guardrail.__name__}")
                break
        
        assert "GUARDRAIL VIOLATION" in payload, "Should catch at least one violation"

    def test_external_sources_required_when_serper_enabled(self, monkeypatch):
        """Should reject final report without URL sources when SERPER is configured."""
        monkeypatch.setenv("CREW_REQUIRE_EXTERNAL_SOURCES", "true")
        monkeypatch.setenv("SERPER_API_KEY", "dummy")
        monkeypatch.setenv("CREW_MIN_EXTERNAL_SOURCE_URLS", "1")

        text = (
            "INVESTMENT RECOMMENDATION: PASS\n\n"
            "Narrative...\n\n"
            "## Sources\n"
            "- No external sources were used for this report.\n"
        )
        success, payload = self._check(
            InvestmentAdvisoryGuardrails.require_external_sources(text)
        )
        assert not success
        assert "GUARDRAIL VIOLATION" in payload

    def test_external_sources_pass_with_two_urls(self, monkeypatch):
        """Should pass when at least two URL citations are included."""
        monkeypatch.setenv("CREW_REQUIRE_EXTERNAL_SOURCES", "true")
        monkeypatch.setenv("SERPER_API_KEY", "dummy")
        monkeypatch.setenv("CREW_MIN_EXTERNAL_SOURCE_URLS", "2")

        text = (
            "INVESTMENT RECOMMENDATION: BUY WITH CAUTION\n\n"
            "Narrative...\n\n"
            "## Sources\n"
            "- Census - https://www.census.gov/ (Accessed: 2026-02-09)\n"
            "- Freddie Mac - https://www.freddiemac.com/ (Accessed: 2026-02-09)\n"
        )
        success, payload = self._check(
            InvestmentAdvisoryGuardrails.require_external_sources(text)
        )
        assert success
        assert payload == text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
