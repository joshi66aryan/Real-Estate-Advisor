"""
Streamlit UI for RE-101 Investment Advisory Engine
Guardrails work transparently in the background
"""

import streamlit as st
import sys
from pathlib import Path
import time

# Add project root to path so absolute package imports work in Streamlit script mode.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui.orchestrator import InvestmentAdvisorOrchestrator
from dotenv import load_dotenv

load_dotenv()

# Exact input fields referenced by crew task templates.
REQUIRED_AGENT_FIELDS = [
    "property_address",
    "purchase_price",
    "square_footage",
    "bedrooms",
    "bathrooms",
    "property_type",
    "year_built",
    "estimated_monthly_rent",
    "annual_operating_expenses",
    "down_payment_percent",
    "interest_rate",
    "loan_term_years",
]

# Page config
# Keep layout wide because recommendation and financial metrics are shown side-by-side.
st.set_page_config(
    page_title="RE-101 Investment Advisor",
    page_icon="🏠",
    layout="wide"
)

# Initialize session state
# Session state persists outputs between reruns triggered by widget interaction.
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'execution_time' not in st.session_state:
    st.session_state.execution_time = None

# Title
st.title("🏠 RE-101: AI-Driven Investment Advisory Engine")
st.markdown("**Powered by CrewAI Multi-Agent System with Safety Guardrails**")
st.markdown("---")

# Sidebar for strategy selection
# Strategy is provided separately from property payload to keep intent explicit.
st.sidebar.header("Investment Strategy")
strategy = st.sidebar.selectbox(
    "Select your investment strategy:",
    ["Passive Income", "Aggressive Growth", "Fix & Flip"],
    help="Choose the strategy that aligns with your investment goals"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Strategy Definitions

**Passive Income**
- Focus: Stable monthly cash flow
- Target: 8%+ Cash-on-Cash Return
- Timeline: Long-term hold (10+ years)

**Aggressive Growth**
- Focus: Capital appreciation
- Target: 12%+ IRR
- Timeline: Medium-term (3-7 years)

**Fix & Flip**
- Focus: Quick profit on resale
- Target: 20%+ profit margin
- Timeline: Short-term (6-12 months)
""")

st.sidebar.markdown("---")
st.sidebar.info("🛡️ **Safety Guardrails Active**\n\nAll AI outputs are automatically validated to ensure:\n- No guaranteed return claims\n- Realistic projections\n- Risk acknowledgment\n- Professional consultation guidance")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    # Left column collects required structured inputs for all downstream tasks.
    st.header("Property Details")
    
    property_address = st.text_input(
        "Property Address",
        value="456 Oak Avenue, Austin, TX 78701"
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        purchase_price = st.number_input(
            "Purchase Price ($)",
            min_value=0,
            value=475000,
            step=10000
        )
        square_footage = st.number_input(
            "Square Footage",
            min_value=0,
            value=1950,
            step=50
        )
        bedrooms = st.number_input("Bedrooms", min_value=0, value=3, step=1)
    
    with col_b:
        estimated_monthly_rent = st.number_input(
            "Estimated Monthly Rent ($)",
            min_value=0,
            value=3400,
            step=100
        )
        bathrooms = st.number_input("Bathrooms", min_value=0.0, value=2.0, step=0.5)
        year_built = st.number_input("Year Built", min_value=1800, max_value=2030, value=2015, step=1)
    
    property_type = st.selectbox(
        "Property Type",
        ["Single Family Home", "Condo", "Townhouse", "Multi-Family", "Commercial"]
    )
    
    st.subheader("Financial Details")
    
    col_c, col_d = st.columns(2)
    with col_c:
        annual_operating_expenses = st.number_input(
            "Annual Operating Expenses ($)",
            min_value=0,
            value=14000,
            step=500
        )
        down_payment_percent = st.number_input(
            "Down Payment (%)",
            min_value=0.0,
            max_value=100.0,
            value=25.0,
            step=5.0
        )
    
    with col_d:
        interest_rate = st.number_input(
            "Interest Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.25,
            step=0.25
        )
        loan_term_years = st.number_input(
            "Loan Term (years)",
            min_value=1,
            max_value=30,
            value=30,
            step=5
        )

with col2:
    # Right column controls execution and renders recommendation/metrics output.
    st.header("Analysis & Recommendation")
    
    if st.button("🔍 Analyze Property", type="primary", use_container_width=True):
        with st.spinner("Running multi-agent analysis with safety guardrails..."):
            form_data = {
                'property_address': property_address,
                'purchase_price': purchase_price,
                'square_footage': square_footage,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'property_type': property_type,
                'year_built': year_built,
                'estimated_monthly_rent': estimated_monthly_rent,
                'annual_operating_expenses': annual_operating_expenses,
                'down_payment_percent': down_payment_percent,
                'interest_rate': interest_rate,
                'loan_term_years': loan_term_years,
            }

            # Send only the keys that task templates and backend validation require.
            property_data = {field: form_data[field] for field in REQUIRED_AGENT_FIELDS}
            
            start_time = time.time()
            orchestrator = InvestmentAdvisorOrchestrator()
            result = orchestrator.analyze_property(property_data, strategy)
            execution_time = time.time() - start_time
            
            st.session_state.analysis_result = result
            st.session_state.execution_time = execution_time
    
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        exec_time = st.session_state.execution_time
        
        st.metric(
            "Response Time",
            f"{exec_time:.2f}s",
            delta="Target: <5s",
            delta_color="normal" if exec_time < 5 else "inverse"
        )
        
        status = result.get('status', 'unknown')
        if status == 'completed':
            st.success("✅ Analysis Complete (Safety Guardrails Passed)")
            
            tab1, tab2 = st.tabs(["📊 Recommendation", "📈 Financial Data"])
            
            with tab1:
                st.markdown("### Investment Recommendation")
                recommendation = result.get('recommendation', 'No recommendation available')
                st.markdown(recommendation)
            
            with tab2:
                st.markdown("### Preliminary Financial Analysis")
                
                if 'preliminary_financials' in result:
                    financials = result['preliminary_financials']
                    
                    if financials.get('status') == 'success':
                        metrics = financials['core_metrics']
                        
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        with metric_col1:
                            st.metric("Cap Rate", f"{metrics['cap_rate']}%")
                        with metric_col2:
                            st.metric("Cash-on-Cash", f"{metrics['cash_on_cash_return']}%")
                        with metric_col3:
                            st.metric("IRR (5-year)", f"{metrics['irr_estimate']}%")
                        
                        cf = financials['cash_flow_analysis']
                        cf_col1, cf_col2 = st.columns(2)
                        with cf_col1:
                            st.metric("Monthly Cash Flow", f"${cf['monthly_cash_flow']:,.2f}")
                        with cf_col2:
                            st.metric("Annual Cash Flow", f"${cf['annual_cash_flow']:,.2f}")
        
        elif status == 'pending_human_input':
            st.warning("⚠️ Human Input Required")
            st.markdown(result.get('required_action', 'Additional information needed'))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>RE-101 Investment Advisory Engine v1.0</strong></p>
    <p>🛡️ Protected by AI Safety Guardrails | Powered by CrewAI</p>
    <p style='font-size: 0.8em; color: gray;'>
        All recommendations are validated for safety and compliance.
    </p>
</div>
""", unsafe_allow_html=True)
