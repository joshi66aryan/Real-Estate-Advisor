"""
Configuration settings for the Real Estate Investment Advisory Engine.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Provider/model configuration constants.
# Note: these names are currently legacy and may not be used by all runtime entrypoints.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("MODEL")

# Strategy thresholds used for scoring/risk interpretation in helper logic.
STRATEGY_CONFIGS = {
    "Passive Income": {
        "min_coc": 0.08,  # Minimum 8% cash-on-cash return
        "min_cap_rate": 0.06,  # Minimum 6% cap rate
        "max_vacancy": 8.0,  # Maximum 8% vacancy rate
        "preferred_hold": 10,  # 10+ year hold period
        "focus": "rental_income",
        "risk_tolerance": "low"
    },
    "Aggressive Growth": {
        "min_irr": 0.15,  # Minimum 15% IRR
        "min_appreciation": 0.05,  # Minimum 5% annual appreciation
        "max_hold": 5,  # 3-5 year hold period
        "focus": "appreciation",
        "risk_tolerance": "high"
    },
    "Fix & Flip": {
        "min_profit_margin": 0.20,  # Minimum 20% profit margin
        "max_hold": 1,  # 6-12 month hold period
        "focus": "renovation_profit",
        "risk_tolerance": "medium"
    }
}

# Generic risk bands that can be referenced by evaluators/visualizations.
RISK_THRESHOLDS = {
    "vacancy_rate": {
        "low": 5.0,
        "medium": 8.0,
        "high": 12.0
    },
    "cap_rate": {
        "excellent": 8.0,
        "good": 6.0,
        "acceptable": 4.0,
        "poor": 0.0
    },
    "cash_on_cash": {
        "excellent": 12.0,
        "good": 8.0,
        "acceptable": 5.0,
        "poor": 0.0
    },
    "debt_service_coverage": {
        "strong": 1.25,
        "adequate": 1.15,
        "weak": 1.0
    }
}

# Mapping from qualitative recommendation labels to numeric score floors.
RECOMMENDATION_SCORES = {
    "STRONG BUY": 80,
    "BUY": 60,
    "CONDITIONAL BUY": 40,
    "HOLD": 20,
    "PASS": 0
}
