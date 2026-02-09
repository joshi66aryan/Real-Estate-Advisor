"""
Event-Driven Flow Manager for Crew Orchestration
Implements state management, sequencing, and branching logic
"""

from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
import time


class FlowState(Enum):
    """Flow execution states"""
    INITIALIZED = "initialized"
    DATA_COLLECTION = "data_collection"
    FINANCIAL_ANALYSIS = "financial_analysis"
    RISK_ANALYSIS = "risk_analysis"
    STRATEGY_EVALUATION = "strategy_evaluation"
    FINAL_RECOMMENDATION = "final_recommendation"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_HUMAN_INPUT = "requires_human_input"


class DecisionPoint(Enum):
    """Decision points that can trigger branching"""
    NEGATIVE_CASH_FLOW = "negative_cash_flow"
    HIGH_RISK_DETECTED = "high_risk_detected"
    STRATEGY_MISMATCH = "strategy_mismatch"
    INSUFFICIENT_DATA = "insufficient_data"
    EXCEPTIONAL_OPPORTUNITY = "exceptional_opportunity"


@dataclass
class FlowEvent:
    """Event in the flow execution"""
    event_type: str
    timestamp: datetime
    state: FlowState
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowContext:
    """Context maintained throughout flow execution"""
    property_data: Dict[str, Any]
    strategy: str
    current_state: FlowState = FlowState.INITIALIZED
    events: List[FlowEvent] = field(default_factory=list)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    decision_points: List[DecisionPoint] = field(default_factory=list)
    human_input_required: bool = False
    execution_metadata: Dict[str, Any] = field(default_factory=dict)


class FlowManager:
    """
    Event-driven flow manager for crew orchestration
    Manages state, sequencing, and branching logic
    """
    
    def __init__(self):
        # One FlowManager instance tracks one active run context at a time.
        self.context: Optional[FlowContext] = None
        self.state_handlers: Dict[FlowState, Callable] = {}
        self.decision_handlers: Dict[DecisionPoint, Callable] = {}
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """Initialize state and decision handlers"""
        # State handlers implement the default linear pipeline.
        # State handlers
        self.state_handlers = {
            FlowState.INITIALIZED: self._handle_initialization,
            FlowState.DATA_COLLECTION: self._handle_data_collection,
            FlowState.FINANCIAL_ANALYSIS: self._handle_financial_analysis,
            FlowState.RISK_ANALYSIS: self._handle_risk_analysis,
            FlowState.STRATEGY_EVALUATION: self._handle_strategy_evaluation,
            FlowState.FINAL_RECOMMENDATION: self._handle_final_recommendation,
        }
        
        # Decision handlers run when threshold-based branch points are detected.
        self.decision_handlers = {
            DecisionPoint.NEGATIVE_CASH_FLOW: self._handle_negative_cash_flow,
            DecisionPoint.HIGH_RISK_DETECTED: self._handle_high_risk,
            DecisionPoint.STRATEGY_MISMATCH: self._handle_strategy_mismatch,
            DecisionPoint.INSUFFICIENT_DATA: self._handle_insufficient_data,
            DecisionPoint.EXCEPTIONAL_OPPORTUNITY: self._handle_exceptional_opportunity,
        }
    
    def initialize_flow(self, property_data: Dict[str, Any], strategy: str) -> FlowContext:
        """Initialize a new flow execution"""
        self.context = FlowContext(
            property_data=property_data,
            strategy=strategy,
            execution_metadata={
                'start_time': time.time(),
                'flow_version': '1.0.0'
            }
        )
        
        self._emit_event(
            event_type="FLOW_INITIALIZED",
            data={
                'property': property_data.get('property_address'),
                'strategy': strategy
            }
        )
        
        return self.context
    
    def _emit_event(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit an event and add to context"""
        if not self.context:
            raise RuntimeError("Flow context not initialized")
        
        event = FlowEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            state=self.context.current_state,
            data=data,
            metadata=metadata or {}
        )
        
        # Event log is used for traceability and UI summaries.
        self.context.events.append(event)
        print(f"[EVENT] {event_type} at {event.state.value}")
    
    def _transition_state(self, new_state: FlowState):
        """Transition to a new state"""
        if not self.context:
            raise RuntimeError("Flow context not initialized")
        
        old_state = self.context.current_state
        self.context.current_state = new_state
        
        self._emit_event(
            event_type="STATE_TRANSITION",
            data={
                'from_state': old_state.value,
                'to_state': new_state.value
            }
        )
    
    def _check_decision_points(self, analysis_data: Dict[str, Any]) -> List[DecisionPoint]:
        """Check for decision points based on analysis data"""
        # These checks are deterministic heuristics, not model-based judgments.
        decision_points = []
        
        # Check for negative cash flow
        if 'cash_flow_analysis' in analysis_data:
            monthly_cf = analysis_data['cash_flow_analysis'].get('monthly_cash_flow', 0)
            if monthly_cf < 0:
                decision_points.append(DecisionPoint.NEGATIVE_CASH_FLOW)
        
        # Check for high risk
        if 'risk_rating' in analysis_data:
            if analysis_data['risk_rating'] in ['HIGH', 'CRITICAL']:
                decision_points.append(DecisionPoint.HIGH_RISK_DETECTED)
        
        # Check for strategy mismatch
        if 'alignment_score' in analysis_data:
            if analysis_data['alignment_score'] < 6:
                decision_points.append(DecisionPoint.STRATEGY_MISMATCH)
        
        # Check for exceptional opportunity
        if 'core_metrics' in analysis_data:
            metrics = analysis_data['core_metrics']
            if metrics.get('cash_on_cash_return', 0) > 12 and metrics.get('cap_rate', 0) > 8:
                decision_points.append(DecisionPoint.EXCEPTIONAL_OPPORTUNITY)
        
        return decision_points
    
    def _handle_initialization(self) -> FlowState:
        """Handle initialization state"""
        self._emit_event(
            event_type="VALIDATION_START",
            data={'property': self.context.property_data.get('property_address')}
        )
        
        # Validate required fields
        required_fields = [
            'property_address', 'purchase_price', 'estimated_monthly_rent',
            'annual_operating_expenses', 'down_payment_percent', 'interest_rate'
        ]
        
        missing_fields = [f for f in required_fields if f not in self.context.property_data]
        
        if missing_fields:
            self._emit_event(
                event_type="VALIDATION_FAILED",
                data={'missing_fields': missing_fields}
            )
            self.context.decision_points.append(DecisionPoint.INSUFFICIENT_DATA)
            return FlowState.REQUIRES_HUMAN_INPUT
        
        self._emit_event(
            event_type="VALIDATION_PASSED",
            data={'validated_fields': required_fields}
        )
        
        return FlowState.DATA_COLLECTION
    
    def _handle_data_collection(self) -> FlowState:
        """Handle data collection state"""
        self._emit_event(
            event_type="DATA_COLLECTION_START",
            data={'sources': ['MLS', 'market_data', 'neighborhood_stats']}
        )
        
        # In real implementation, this would trigger data integration agent
        # For flow management, we just track the state transition
        
        self._emit_event(
            event_type="DATA_COLLECTION_COMPLETE",
            data={'status': 'success'}
        )
        
        return FlowState.FINANCIAL_ANALYSIS
    
    def _handle_financial_analysis(self) -> FlowState:
        """Handle financial analysis state"""
        self._emit_event(
            event_type="FINANCIAL_ANALYSIS_START",
            data={'metrics': ['cap_rate', 'coc', 'irr']}
        )
        
        # Check for decision points after financial analysis
        # In real implementation, this would use actual analysis results
        
        return FlowState.RISK_ANALYSIS
    
    def _handle_risk_analysis(self) -> FlowState:
        """Handle risk analysis state"""
        self._emit_event(
            event_type="RISK_ANALYSIS_START",
            data={'categories': ['demographic', 'market', 'economic', 'property']}
        )
        
        # Risk analysis might trigger decision points
        
        return FlowState.STRATEGY_EVALUATION
    
    def _handle_strategy_evaluation(self) -> FlowState:
        """Handle strategy evaluation state"""
        self._emit_event(
            event_type="STRATEGY_EVALUATION_START",
            data={'strategy': self.context.strategy}
        )
        
        # Strategy evaluation determines if we proceed to recommendation
        
        return FlowState.FINAL_RECOMMENDATION
    
    def _handle_final_recommendation(self) -> FlowState:
        """Handle final recommendation state"""
        self._emit_event(
            event_type="RECOMMENDATION_GENERATION_START",
            data={'approach': 'chain_of_thought'}
        )
        
        return FlowState.COMPLETED
    
    # Decision point handlers (branching logic)
    
    def _handle_negative_cash_flow(self) -> Dict[str, Any]:
        """Handle negative cash flow decision point"""
        self._emit_event(
            event_type="DECISION_POINT_TRIGGERED",
            data={
                'decision_point': DecisionPoint.NEGATIVE_CASH_FLOW.value,
                'action': 'flag_for_review'
            }
        )
        
        return {
            'action': 'flag_for_review',
            'message': 'Property shows negative cash flow. Additional analysis recommended.',
            'next_steps': [
                'Verify rent estimates',
                'Review expense projections',
                'Consider different financing options',
                'Evaluate if strategy should be Aggressive Growth instead'
            ]
        }
    
    def _handle_high_risk(self) -> Dict[str, Any]:
        """Handle high risk decision point"""
        self._emit_event(
            event_type="DECISION_POINT_TRIGGERED",
            data={
                'decision_point': DecisionPoint.HIGH_RISK_DETECTED.value,
                'action': 'deep_dive_analysis'
            }
        )
        
        return {
            'action': 'deep_dive_analysis',
            'message': 'High risk factors detected. Recommend detailed due diligence.',
            'next_steps': [
                'Conduct property inspection',
                'Research neighborhood trends in detail',
                'Analyze comparable sales closely',
                'Consider risk mitigation strategies'
            ]
        }
    
    def _handle_strategy_mismatch(self) -> Dict[str, Any]:
        """Handle strategy mismatch decision point"""
        self._emit_event(
            event_type="DECISION_POINT_TRIGGERED",
            data={
                'decision_point': DecisionPoint.STRATEGY_MISMATCH.value,
                'action': 'suggest_alternative'
            }
        )
        
        return {
            'action': 'suggest_alternative',
            'message': 'Property does not align well with selected strategy.',
            'next_steps': [
                'Review alternative investment strategies',
                'Consider different property types',
                'Re-evaluate investment goals'
            ]
        }
    
    def _handle_insufficient_data(self) -> Dict[str, Any]:
        """Handle insufficient data decision point"""
        self._emit_event(
            event_type="DECISION_POINT_TRIGGERED",
            data={
                'decision_point': DecisionPoint.INSUFFICIENT_DATA.value,
                'action': 'request_additional_data'
            }
        )
        
        self.context.human_input_required = True
        
        return {
            'action': 'request_additional_data',
            'message': 'Insufficient data to complete analysis.',
            'required_data': self._get_missing_data_requirements()
        }
    
    def _handle_exceptional_opportunity(self) -> Dict[str, Any]:
        """Handle exceptional opportunity decision point"""
        self._emit_event(
            event_type="DECISION_POINT_TRIGGERED",
            data={
                'decision_point': DecisionPoint.EXCEPTIONAL_OPPORTUNITY.value,
                'action': 'expedite_recommendation'
            }
        )
        
        return {
            'action': 'expedite_recommendation',
            'message': 'Exceptional investment opportunity detected!',
            'next_steps': [
                'Fast-track due diligence',
                'Prepare offer immediately',
                'Secure financing pre-approval',
                'Schedule property inspection ASAP'
            ]
        }
    
    def _get_missing_data_requirements(self) -> List[str]:
        """Get list of missing data requirements"""
        required_fields = [
            'property_address', 'purchase_price', 'square_footage',
            'bedrooms', 'bathrooms', 'property_type', 'year_built',
            'estimated_monthly_rent', 'annual_operating_expenses',
            'down_payment_percent', 'interest_rate', 'loan_term_years'
        ]
        
        return [f for f in required_fields if f not in self.context.property_data]
    
    def execute_flow(self) -> Dict[str, Any]:
        """Execute the complete flow with state management and branching"""
        if not self.context:
            raise RuntimeError("Flow context not initialized. Call initialize_flow() first.")
        
        print(f"\n{'='*80}")
        print(f"EVENT-DRIVEN FLOW EXECUTION STARTED")
        print(f"{'='*80}\n")
        
        # Execute state machine until a terminal state is reached.
        while self.context.current_state not in [FlowState.COMPLETED, FlowState.FAILED, FlowState.REQUIRES_HUMAN_INPUT]:
            current_state = self.context.current_state
            
            print(f"[STATE] {current_state.value}")
            
            # Get handler for current state
            handler = self.state_handlers.get(current_state)
            
            if not handler:
                self._emit_event(
                    event_type="ERROR",
                    data={'error': f'No handler for state: {current_state.value}'}
                )
                self._transition_state(FlowState.FAILED)
                break
            
            # Execute handler and get next state
            try:
                next_state = handler()
                self._transition_state(next_state)
                
                # Check for decision points
                decision_points = self._check_decision_points(
                    self.context.analysis_results
                )
                
                if decision_points:
                    self.context.decision_points.extend(decision_points)
                    
                    for dp in decision_points:
                        decision_handler = self.decision_handlers.get(dp)
                        if decision_handler:
                            decision_result = decision_handler()
                            self.context.analysis_results[f'decision_{dp.value}'] = decision_result
                
            except Exception as e:
                self._emit_event(
                    event_type="ERROR",
                    data={'error': str(e), 'state': current_state.value}
                )
                self._transition_state(FlowState.FAILED)
                break
        
        # Calculate execution time
        execution_time = time.time() - self.context.execution_metadata['start_time']
        
        print(f"\n{'='*80}")
        print(f"FLOW EXECUTION COMPLETED")
        print(f"{'='*80}")
        print(f"Final State: {self.context.current_state.value}")
        print(f"Execution Time: {execution_time:.2f}s")
        print(f"Total Events: {len(self.context.events)}")
        print(f"Decision Points: {len(self.context.decision_points)}")
        print(f"{'='*80}\n")
        
        return {
            'final_state': self.context.current_state.value,
            'execution_time': execution_time,
            'events': [
                {
                    'type': e.event_type,
                    'timestamp': e.timestamp.isoformat(),
                    'state': e.state.value,
                    'data': e.data
                }
                for e in self.context.events
            ],
            'decision_points': [dp.value for dp in self.context.decision_points],
            'analysis_results': self.context.analysis_results,
            'human_input_required': self.context.human_input_required
        }
    
    def get_flow_summary(self) -> str:
        """Get human-readable flow summary"""
        if not self.context:
            return "No flow executed"
        
        summary = f"""
FLOW EXECUTION SUMMARY
{'='*80}

Property: {self.context.property_data.get('property_address', 'N/A')}
Strategy: {self.context.strategy}
Final State: {self.context.current_state.value}

Events Timeline:
"""
        for i, event in enumerate(self.context.events, 1):
            summary += f"{i}. [{event.timestamp.strftime('%H:%M:%S')}] {event.event_type} ({event.state.value})\n"
        
        if self.context.decision_points:
            summary += f"\nDecision Points Triggered:\n"
            for dp in self.context.decision_points:
                summary += f"  - {dp.value}\n"
        
        return summary
