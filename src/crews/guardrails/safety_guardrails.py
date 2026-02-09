"""
Safety Guardrails for CrewAI Tasks
Implements guardrails to be used directly in task definitions
"""

from typing import List, Callable, Any
import re
import os


class InvestmentAdvisoryGuardrails:
    """Guardrail functions for investment advisory tasks"""

    @staticmethod
    def _to_text(output: Any) -> str:
        """
        Normalize CrewAI guardrail input to text.

        CrewAI may pass either a raw string or a TaskOutput-like object.
        This helper keeps individual guardrails focused on policy checks only.
        """
        if isinstance(output, str):
            return output
        if hasattr(output, "raw") and isinstance(output.raw, str):
            return output.raw
        if hasattr(output, "output") and isinstance(output.output, str):
            return output.output
        return str(output)
    
    @staticmethod
    def no_guaranteed_returns(output: Any) -> tuple[bool, str]:
        """
        Guardrail: Prevent guaranteed return claims
        
        This guardrail checks for and rejects outputs that make guaranteed
        return or profit claims, which violate investment advisory regulations.
        Contract: return (False, reason) to trigger retry; (True, output_text) to pass.
        """
        
        text = InvestmentAdvisoryGuardrails._to_text(output)

        # Patterns that indicate guaranteed returns
        violation_patterns = [
            r'\b(guaranteed|guarantee[sd]?|promise[sd]?)\s+(?:return|profit|gain|income)',
            r'\b(?:guaranteed|guarantee[sd]?)\s+to\s+(?:make|earn|generate|return)\b',
            r'\b(?:promise[sd]?|promising)\s+(?:steady\s+)?(?:profit|profits|returns?)\b',
            r'\bit(?:\'s| is)\s+guaranteed\b',
            r'\b(will definitely|will certainly|absolutely will)\s+(?:make|earn|generate)',
            r'\b(?:risk-?free|no risk|zero risk)\s+(?:profit|return|investment)',
            r'\b(?:can\'t lose|cannot lose|guaranteed to make)',
            r'\bguaranteed\s+(?:\d+%?|\$[\d,]+)',
            r'\byou\s+(?:will|are going to)\s+(?:definitely|certainly)\s+(?:make|earn|profit)',
        ]
        
        for pattern in violation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return (
                    False,
                    "GUARDRAIL VIOLATION: Output contains guaranteed return claims. "
                    "Investment returns cannot be guaranteed. "
                    "Please rewrite using probabilistic language such as 'potential', "
                    "'estimated', 'projected', 'may generate', or 'could provide'. "
                    "Example: Instead of 'will definitely earn 10%', use 'has potential "
                    "to generate approximately 10% based on current market conditions'."
                )
        
        return True, text
    
    @staticmethod
    def no_absolute_certainty(output: Any) -> tuple[bool, str]:
        """
        Guardrail: Prevent absolute certainty claims about future outcomes
        
        Real estate markets are unpredictable. This guardrail prevents
        claims of certainty about future property values or market conditions.
        """
        
        text = InvestmentAdvisoryGuardrails._to_text(output)

        violation_patterns = [
            r'\b(?:will|must)\s+(?:definitely\s+|certainly\s+|absolutely\s+)?(?:increase|rise|grow|appreciate|go up|become profitable)\b',
            r'\b(?:always|never|every time|without exception)\b',
            r'\b(?:impossible|zero chance)\s+(?:that|for)',
            r'\bno\s+way\b.*\bwill\b',
            r'\bthis\s+(?:will|must)\s+be\s+a\s+(?:great|excellent|perfect)\s+investment\b',
            r'\b(?:definitely|absolutely|certainly)\s+(?:recommend|suggest)\s+buying',
        ]
        
        for pattern in violation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return (
                    False,
                    "GUARDRAIL VIOLATION: Output uses absolute certainty language. "
                    "Real estate markets are unpredictable and outcomes are uncertain. "
                    "Please rewrite using conditional language: 'likely to', 'could', "
                    "'may', 'suggests potential for', 'historically has shown'. "
                    "Acknowledge market uncertainty and variability in your analysis."
                )
        
        return True, text
    
    @staticmethod
    def provide_analysis_not_advice(output: Any) -> tuple[bool, str]:
        """
        Guardrail: Ensure output provides analysis, not direct financial advice
        
        We provide data-driven analysis, not personalized financial advice.
        This guardrail prevents direct recommendations to buy/sell.
        """
        
        text = InvestmentAdvisoryGuardrails._to_text(output)

        violation_patterns = [
            r'\b(?:I|we)\s+(?:recommend|advise|suggest)\s+(?:that\s+)?you\s+(?:buy|purchase|invest)',
            r'\byou\s+(?:should|must|need to)\s+(?:buy|purchase|invest|sell)',
            r'\bthis\s+is\s+(?:the|a)\s+(?:best|perfect|ideal)\s+(?:time|opportunity)\s+to\s+buy',
            r'\byou\s+(?:should not|shouldn\'t|must not)\s+(?:pass|miss)\s+(?:this|on this)',
        ]
        
        for pattern in violation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return (
                    False,
                    "GUARDRAIL VIOLATION: Output provides direct financial advice. "
                    "You should frame your output as analysis and information, not advice. "
                    "Instead of 'You should buy this property', use 'Based on the data, "
                    "this property shows characteristics that align with [strategy]' or "
                    "'The analysis suggests this property demonstrates [qualities]'. "
                    "Let the investor make their own decision based on your analysis."
                )
        
        return True, text
    
    @staticmethod
    def no_manipulation_tactics(output: Any) -> tuple[bool, str]:
        """
        Guardrail: Prevent manipulative urgency or pressure tactics
        
        Investment decisions should be thoughtful, not rushed.
        This guardrail prevents FOMO and urgency tactics.
        """
        
        text = InvestmentAdvisoryGuardrails._to_text(output)

        violation_patterns = [
            r'\b(?:act now|buy now|don\'t wait|limited time|hurry|rush)',
            r'\b(?:once in a lifetime|rare opportunity|won\'t last)',
            r'\bif\s+you\s+don\'t\s+(?:buy|act|move)\s+(?:now|today|immediately)',
            r'\b(?:miss out|FOMO|you\'ll regret)',
            r'\bonly\s+\d+\s+(?:days|hours|minutes)\s+(?:left|remaining)',
        ]
        
        for pattern in violation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return (
                    False,
                    "GUARDRAIL VIOLATION: Output uses manipulative urgency tactics. "
                    "Investment decisions should be made thoughtfully, not under pressure. "
                    "Remove urgency language and time pressure. Instead, encourage thorough "
                    "due diligence: 'Take time to review all aspects', 'Conduct comprehensive "
                    "property inspection', 'Consult with qualified professionals'. "
                    "Present objective analysis without artificial urgency."
                )
        
        return True, text
    
    @staticmethod
    def realistic_projections(output: Any) -> tuple[bool, str]:
        """
        Guardrail: Ensure financial projections are realistic
        
        Prevents claims of unrealistically high returns that could
        mislead investors.
        """
        
        text = InvestmentAdvisoryGuardrails._to_text(output)

        # Check for percentage claims above reasonable thresholds
        percentage_pattern = r'(\d+)%\s+(?:annual\s+|yearly\s+|per\s+year\s+)?(?:return|returns|profit|gain|appreciation|ROI)'
        matches = re.finditer(percentage_pattern, text, re.IGNORECASE)
        
        for match in matches:
            percentage = int(match.group(1))
            if percentage > 25:  # Returns >25% are very rare in real estate
                return (
                    False,
                    f"GUARDRAIL VIOLATION: Output claims {percentage}% returns, which is "
                    "unrealistically high for typical real estate investments. "
                    "Standard real estate returns typically range from 6-15% for passive "
                    "investments, and 15-20% for more aggressive strategies. "
                    "Please revise projections to realistic ranges and clearly note that "
                    "these are estimates based on assumptions that may not materialize. "
                    "Include sensitivity analysis showing downside scenarios."
                )
        
        return True, text
    
    @staticmethod
    def include_risk_acknowledgment(output: Any) -> tuple[bool, str]:
        """
        Guardrail: Ensure risks are acknowledged in final recommendations
        
        Any investment recommendation must acknowledge associated risks.
        """
        
        text = InvestmentAdvisoryGuardrails._to_text(output)

        # Check if output is a final recommendation (long-form output)
        if len(text) > 500:  # Only check substantial outputs
            
            risk_indicators = [
                r'\brisk[s]?\b',
                r'\buncertain(?:ty)?\b',
                r'\bvariab(?:le|ility)\b',
                r'\bmay\s+(?:not|fluctuate|change|vary)\b',
                r'\bcould\s+(?:decrease|decline|fall)\b',
                r'\bno\s+guarantee[s]?\b',
            ]
            
            has_risk_acknowledgment = any(
                re.search(pattern, text, re.IGNORECASE) 
                for pattern in risk_indicators
            )
            
            if not has_risk_acknowledgment:
                return (
                    False,
                    "GUARDRAIL VIOLATION: Output lacks risk acknowledgment. "
                    "Investment recommendations must acknowledge associated risks. "
                    "Please include discussion of: market risks, property-specific risks, "
                    "economic uncertainty, and the possibility of loss. "
                    "Example: 'While the analysis is positive, consider risks such as "
                    "[specific risks]. Market conditions can change, and actual results "
                    "may differ from projections.'"
                )
        
        return True, text
    
    @staticmethod
    def require_professional_consultation(output: Any) -> tuple[bool, str]:
        """
        Guardrail: Ensure output recommends professional consultation
        
        Final recommendations should encourage consulting with qualified professionals.
        """
        
        text = InvestmentAdvisoryGuardrails._to_text(output)

        # Check if output is a final recommendation
        if len(text) > 500:
            
            consultation_indicators = [
                r'\bconsult\s+(?:with\s+)?(?:a\s+)?(?:qualified|licensed|professional)',
                r'\bseek\s+(?:advice|guidance|counsel)\s+from',
                r'\bspeak\s+with\s+(?:a\s+)?(?:professional|expert|advisor)',
                r'\b(?:attorney|lawyer|CPA|accountant|financial\s+advisor)',
                r'\bdue\s+diligence\b',
            ]
            
            has_consultation = any(
                re.search(pattern, text, re.IGNORECASE)
                for pattern in consultation_indicators
            )
            
            if not has_consultation:
                return (
                    False,
                    "GUARDRAIL VIOLATION: Output does not recommend professional consultation. "
                    "Investment recommendations should encourage consulting qualified professionals. "
                    "Please add guidance to: 'Conduct thorough due diligence', "
                    "'Consult with a qualified real estate attorney', "
                    "'Work with a licensed CPA for tax implications', or "
                    "'Engage a professional inspector to assess property condition'. "
                    "Include at least one recommendation to seek professional guidance."
                )
        
        return True, text

    @staticmethod
    def require_external_sources(output: Any) -> tuple[bool, str]:
        """
        Guardrail: enforce real external URL citations in final report when web search is configured.
        """
        text = InvestmentAdvisoryGuardrails._to_text(output)

        enforce_sources = os.getenv("CREW_REQUIRE_EXTERNAL_SOURCES", "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        search_configured = bool(os.getenv("SERPER_API_KEY"))
        if not (enforce_sources and search_configured):
            return True, text

        has_sources_header = re.search(r"(?im)^##\s*Sources\s*$", text) is not None
        if not has_sources_header:
            return (
                False,
                "GUARDRAIL VIOLATION: Missing `## Sources` section. Include real external URLs used in analysis."
            )

        parts = re.split(r"(?im)^##\s*Sources\s*$", text, maxsplit=1)
        sources_section = parts[1] if len(parts) > 1 else ""
        urls = re.findall(r"https?://[^\s)\]]+", sources_section)
        min_urls = int(os.getenv("CREW_MIN_EXTERNAL_SOURCE_URLS", "1"))
        if len(urls) < min_urls:
            return (
                False,
                "GUARDRAIL VIOLATION: Missing external source URLs in `## Sources`. "
                f"At least {min_urls} URL(s) required. "
                "Format each as: `- Source Name - https://example.com (Accessed: YYYY-MM-DD)`."
            )

        if re.search(r"(?i)no external sources were used for this report", sources_section):
            return (
                False,
                "GUARDRAIL VIOLATION: Web search is enabled, so `No external sources were used` is not allowed."
            )

        return True, text

# Convenience function to get all guardrails
def get_all_investment_guardrails() -> List[Callable]:
    """
    Get all investment advisory guardrails
    
    Returns:
        List of guardrail functions
    """
    # Order matters: broad high-severity policy checks run first.
    return [
        InvestmentAdvisoryGuardrails.no_guaranteed_returns,
        InvestmentAdvisoryGuardrails.no_absolute_certainty,
        InvestmentAdvisoryGuardrails.provide_analysis_not_advice,
        InvestmentAdvisoryGuardrails.no_manipulation_tactics,
        InvestmentAdvisoryGuardrails.realistic_projections,
        InvestmentAdvisoryGuardrails.include_risk_acknowledgment,
        InvestmentAdvisoryGuardrails.require_professional_consultation,
        InvestmentAdvisoryGuardrails.require_external_sources,
    ]


# Specific guardrail sets for different task types
def get_data_analysis_guardrails() -> List[Callable]:
    """Guardrails for data analysis tasks"""
    return [
        InvestmentAdvisoryGuardrails.no_absolute_certainty,
        InvestmentAdvisoryGuardrails.realistic_projections,
    ]


def get_financial_modeling_guardrails() -> List[Callable]:
    """Guardrails for financial modeling tasks"""
    return [
        InvestmentAdvisoryGuardrails.no_guaranteed_returns,
        InvestmentAdvisoryGuardrails.realistic_projections,
    ]


def get_risk_assessment_guardrails() -> List[Callable]:
    """Guardrails for risk assessment tasks"""
    return [
        InvestmentAdvisoryGuardrails.no_absolute_certainty,
    ]


def get_final_recommendation_guardrails() -> List[Callable]:
    """Guardrails for final investment recommendations"""
    return get_all_investment_guardrails()
