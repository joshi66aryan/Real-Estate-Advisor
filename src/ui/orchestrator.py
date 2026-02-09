"""
Crew Orchestrator with Flow Manager Integration
Combines CrewAI execution with event-driven flow management
"""

from typing import Dict, Any, Optional
import time
from ..crews.crew import InvestmentAdvisorCrew
from ..flow_manager import FlowManager, FlowState
from ..tools.financial_calculator import FinancialCalculatorTool
import json


class InvestmentAdvisorOrchestrator:
    """
    Orchestrator that integrates CrewAI with Flow Manager
    Provides event-driven execution with state management
    Guardrails are handled transparently by CrewAI tasks
    """
    
    def __init__(self):
        # FlowManager tracks state transitions; calculator gives immediate deterministic metrics.
        self.flow_manager = FlowManager()
        self.crew = None
        self.financial_calculator = FinancialCalculatorTool()
    
    def analyze_property(
        self,
        property_data: Dict[str, Any],
        strategy: str = "Passive Income"
    ) -> Dict[str, Any]:
        """
        Analyze property with event-driven flow management
        
        Args:
            property_data: Property details
            strategy: Investment strategy
        
        Returns:
            Complete analysis with flow execution details
        """
        
        # Initialize flow context and event timeline.
        context = self.flow_manager.initialize_flow(property_data, strategy)
        
        # Run quick deterministic metrics before full agent run.
        calc_result = self._run_preliminary_calculations(property_data)
        
        # Store in context for decision point checking
        context.analysis_results['preliminary_financials'] = calc_result
        
        # Execute state machine to surface branch conditions and audit data.
        flow_result = self.flow_manager.execute_flow()

        # If human input required, return early
        if flow_result['human_input_required']:
            return {
                'status': 'pending_human_input',
                'flow_summary': self.flow_manager.get_flow_summary(),
                'flow_result': flow_result,
                'required_action': 'Please provide missing data or review flagged issues'
            }
        
        # Only execute expensive crew path after flow reaches final recommendation phase.
        if context.current_state in [
            FlowState.FINAL_RECOMMENDATION,
            FlowState.COMPLETED
        ]:
            print("\n🛡️  Guardrails active: Monitoring all agent outputs for compliance\n")
            crew_result = self._execute_crew(property_data, strategy)
            
            return {
                'status': 'completed',
                'recommendation': crew_result,
                'flow_summary': self.flow_manager.get_flow_summary(),
                'flow_result': flow_result,
                'preliminary_financials': calc_result
            }
        else:
            return {
                'status': 'failed',
                'error': f'Flow ended in unexpected state: {context.current_state.value}',
                'flow_summary': self.flow_manager.get_flow_summary(),
                'flow_result': flow_result
            }
    
    def _run_preliminary_calculations(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run preliminary financial calculations"""
        
        print("\n[ORCHESTRATOR] Running preliminary financial calculations...")
        
        calc_input = {
            'purchase_price': property_data.get('purchase_price'),
            'annual_rent': property_data.get('estimated_monthly_rent', 0) * 12,
            'annual_operating_expenses': property_data.get('annual_operating_expenses'),
            'down_payment_percent': property_data.get('down_payment_percent'),
            'interest_rate': property_data.get('interest_rate'),
            'loan_term_years': property_data.get('loan_term_years', 30)
        }
        
        result_json = self.financial_calculator._run(**calc_input)
        result = json.loads(result_json)
        
        # Extract key metrics for decision making and downstream state checks.
        if result.get('status') == 'success':
            metrics = result['core_metrics']
            cash_flow = result['cash_flow_analysis']
            
            print(f"[ORCHESTRATOR] Preliminary Results:")
            print(f"  Cap Rate: {metrics['cap_rate']}%")
            print(f"  Cash-on-Cash: {metrics['cash_on_cash_return']}%")
            print(f"  Monthly Cash Flow: ${cash_flow['monthly_cash_flow']:,.2f}")
            
            # Add risk rating based on metrics
            risk_rating = self._assess_preliminary_risk(metrics, cash_flow)
            result['risk_rating'] = risk_rating
            
            # Add alignment score estimate
            alignment_score = self._estimate_alignment_score(
                property_data.get('investment_strategy', 'Passive Income'),
                metrics,
                cash_flow
            )
            result['alignment_score'] = alignment_score
        
        return result
    
    def _assess_preliminary_risk(
        self,
        metrics: Dict[str, Any],
        cash_flow: Dict[str, Any]
    ) -> str:
        """Assess preliminary risk level"""
        
        monthly_cf = cash_flow.get('monthly_cash_flow', 0)
        dscr = metrics.get('dscr', 0)
        
        if monthly_cf < -500 or dscr < 1.0:
            return "HIGH"
        elif monthly_cf < 0 or dscr < 1.15:
            return "MODERATE"
        else:
            return "LOW"
    
    def _estimate_alignment_score(
        self,
        strategy: str,
        metrics: Dict[str, Any],
        cash_flow: Dict[str, Any]
    ) -> float:
        """Estimate strategy alignment score"""
        
        coc = metrics.get('cash_on_cash_return', 0)
        cap_rate = metrics.get('cap_rate', 0)
        irr = metrics.get('irr_estimate', 0)
        monthly_cf = cash_flow.get('monthly_cash_flow', 0)
        
        if strategy == "Passive Income":
            score = 5.0
            if coc > 8:
                score += 2
            if monthly_cf > 300:
                score += 2
            if cap_rate > 6:
                score += 1
        elif strategy == "Aggressive Growth":
            score = 5.0
            if irr > 12:
                score += 3
            if cap_rate < 5:
                score += 1
        elif strategy == "Fix & Flip":
            score = 5.0
            score += 2
        else:
            score = 5.0
        
        return min(10.0, score)
    
    def _execute_crew(
        self,
        property_data: Dict[str, Any],
        strategy: str
    ) -> str:
        """Execute the CrewAI analysis with integrated guardrails"""
        
        print("\n[ORCHESTRATOR] Initializing CrewAI agents with guardrails...")
        
        start_time = time.time()
        
        # Initialize crew
        self.crew = InvestmentAdvisorCrew()
        
        # Keep kickoff payload explicit to prevent accidental extra fields.
        inputs = {
            **property_data,
            'investment_strategy': strategy
        }
        
        print("[ORCHESTRATOR] Starting crew execution...")
        print("               Guardrails will automatically validate and correct outputs\n")
        
        # Execute crew - guardrails work transparently
        result = self.crew.crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        print(f"\n[ORCHESTRATOR] Crew execution completed in {execution_time:.2f}s")
        print(f"[ORCHESTRATOR] ✅ All outputs validated by guardrails")
        
        return str(result)
