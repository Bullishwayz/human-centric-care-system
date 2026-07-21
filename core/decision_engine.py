"""
Decision Simulation Engine: LifeNodePriority Enforcement

This module implements the core reasoning loop that:
1. Identifies affected humans (care-card holders)
2. Loads the care-card
3. Simulates outcomes against hard constraints
4. Applies vetoes for violations
5. Justifies and selects safe actions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
from core.care_card import (
    CareCard,
    HardConstraint,
    VetoPriority,
    MetricType,
    AutonomyLatency,
)


class DecisionStatus(Enum):
    """Outcome of decision simulation."""
    APPROVED = "approved"
    VETOED = "vetoed"
    ESCALATED = "escalated"
    REQUIRES_GUARDIAN_APPROVAL = "requires_guardian_approval"


@dataclass
class SimulationContext:
    """Environmental and operational context for decision-making."""
    current_state: Dict[str, Any]  # Current system state (temp, benefits, etc.)
    proposed_action: str  # What the agent wants to do
    action_parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    affected_care_cards: List[CareCard] = field(default_factory=list)


@dataclass
class ConstraintViolation:
    """Record of a hard constraint that was violated."""
    constraint: HardConstraint
    care_card: CareCard
    violation_reason: str
    severity: str  # "absolute", "high"


@dataclass
class DecisionOutcome:
    """Result of decision simulation and reasoning."""
    decision_id: str
    status: DecisionStatus
    proposed_action: str
    final_action: Optional[str]  # What will actually be done
    rationale: str  # Plain-language explanation
    violations: List[ConstraintViolation] = field(default_factory=list)
    affected_metrics: List[MetricType] = field(default_factory=list)
    guardian_notification_required: bool = False
    notifiable_guardians: List[Dict[str, str]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    audit_log: List[str] = field(default_factory=list)


class DecisionSimulationEngine:
    """
    The core reasoning loop for human-centric agent decision-making.
    
    This engine enforces LifeNodePriority rules and ensures that every
    agent action is vetted against care-card constraints before execution.
    """
    
    def __init__(self):
        self.audit_ledger: List[DecisionOutcome] = []
        self.constraint_evaluators: Dict[str, Callable] = {}
    
    def register_constraint_evaluator(
        self,
        constraint_id: str,
        evaluator_fn: Callable[[Dict[str, Any]], bool]
    ):
        """
        Register a custom evaluator function for a specific constraint.
        
        evaluator_fn should take a context dict and return True if constraint
        is satisfied, False if violated.
        """
        self.constraint_evaluators[constraint_id] = evaluator_fn
    
    def identify_affected_humans(
        self,
        context: SimulationContext,
        available_care_cards: List[CareCard]
    ) -> List[CareCard]:
        """
        Step 1: Identify which humans are affected by the proposed action.
        
        For now, this is a simple check: if any care-card exists in the
        system, it's potentially affected. In production, this would be
        more sophisticated (e.g., location-based, action-type-based).
        """
        context.audit_log = context.audit_log or []
        context.audit_log.append(
            f"[{datetime.now().isoformat()}] Identifying affected humans..."
        )
        
        # In a real system, filter by relevance:
        # - Action affects household heating → all care-cards in household
        # - Action affects financial benefits → all care-cards with benefit dependency
        # - etc.
        
        affected = available_care_cards
        context.audit_log.append(
            f"Found {len(affected)} potentially affected care-card(s)"
        )
        return affected
    
    def load_care_cards(self, affected_humans: List[CareCard]) -> List[CareCard]:
        """
        Step 2: Load the care-cards for all affected humans.
        
        In production, this might involve fetching from a secure TEE or
        encrypted database. For now, we assume they're already loaded.
        """
        return affected_humans
    
    def simulate_outcomes(
        self,
        context: SimulationContext,
        care_cards: List[CareCard]
    ) -> Dict[str, Any]:
        """
        Step 3: Run "mental rehearsal" to predict action outcomes.
        
        For each proposed action, simulate:
        - Changes to current_state
        - Impact on care-card metrics (safety, dignity, needs, financial)
        - Whether any hard constraints would be violated
        """
        context.audit_log.append(
            f"[{datetime.now().isoformat()}] Simulating outcomes for action: {context.proposed_action}"
        )
        
        simulated_state = dict(context.current_state)
        
        # Apply proposed action effects to simulated state
        # This is a placeholder; in production, use domain-specific models
        for param_key, param_value in context.action_parameters.items():
            if param_key in simulated_state:
                simulated_state[param_key] = param_value
        
        context.audit_log.append("Simulated state updated with proposed action effects")
        
        return simulated_state
    
    def apply_hard_veto(
        self,
        context: SimulationContext,
        simulated_state: Dict[str, Any],
        care_cards: List[CareCard]
    ) -> List[ConstraintViolation]:
        """
        Step 4: Check simulated state against LifeNodePriority rules.
        
        Returns list of violations (empty if all constraints pass).
        If any ABSOLUTE veto is triggered, the action is immediately rejected.
        """
        context.audit_log.append(
            f"[{datetime.now().isoformat()}] Applying hard constraints (LifeNodePriority)..."
        )
        
        violations: List[ConstraintViolation] = []
        
        for care_card in care_cards:
            for constraint in care_card.life_node_priorities:
                # Use registered evaluator if available, otherwise do simple check
                if constraint.rule_id in self.constraint_evaluators:
                    is_satisfied = self.constraint_evaluators[constraint.rule_id](
                        simulated_state
                    )
                else:
                    # Default: parse constraint condition as a simple comparison
                    is_satisfied = self._evaluate_constraint_condition(
                        constraint.condition,
                        simulated_state
                    )
                
                if not is_satisfied:
                    violation = ConstraintViolation(
                        constraint=constraint,
                        care_card=care_card,
                        violation_reason=f"Constraint condition failed: {constraint.condition}",
                        severity=constraint.veto_priority.value,
                    )
                    violations.append(violation)
                    context.audit_log.append(
                        f"❌ CONSTRAINT VIOLATION: {constraint.rule_id} "
                        f"({constraint.veto_priority.value})"
                    )
        
        return violations
    
    def select_and_justify(
        self,
        context: SimulationContext,
        violations: List[ConstraintViolation],
        care_cards: List[CareCard],
        decision_id: str
    ) -> DecisionOutcome:
        """
        Step 5: Make final decision and generate rationale.
        
        If ABSOLUTE violations exist, veto the action.
        If HIGH violations exist, escalate to guardians.
        Otherwise, approve with justification.
        """
        context.audit_log.append(
            f"[{datetime.now().isoformat()}] Making final decision..."
        )
        
        outcome = DecisionOutcome(
            decision_id=decision_id,
            status=DecisionStatus.APPROVED,  # Default
            proposed_action=context.proposed_action,
            final_action=context.proposed_action,  # Default to proposed
            rationale="",
            audit_log=context.audit_log,
        )
        
        # Check for absolute vetoes
        absolute_violations = [
            v for v in violations if v.severity == "absolute"
        ]
        
        if absolute_violations:
            outcome.status = DecisionStatus.VETOED
            outcome.final_action = None
            outcome.violations = absolute_violations
            
            violation_summaries = [
                f"'{v.constraint.rule_id}: {v.constraint.rule_description}'"
                for v in absolute_violations
            ]
            outcome.rationale = (
                f"Action VETOED: Proposed action would violate hard constraints: "
                f"{', '.join(violation_summaries)}"
            )
            
            context.audit_log.append(
                f"❌ ACTION VETOED due to {len(absolute_violations)} absolute constraint violation(s)"
            )
            
            return outcome
        
        # Check for high-priority violations
        high_violations = [
            v for v in violations if v.severity == "high"
        ]
        
        if high_violations:
            outcome.status = DecisionStatus.ESCALATED
            outcome.violations = high_violations
            outcome.guardian_notification_required = True
            
            # Collect guardians who must approve
            for violation in high_violations:
                for guardian in violation.care_card.guardians:
                    if guardian.requires_unanimous_approval:
                        outcome.notifiable_guardians.append({
                            "name": guardian.name,
                            "email": guardian.contact_email,
                            "role": guardian.role,
                        })
            
            outcome.rationale = (
                f"Action ESCALATED: Requires guardian review before proceeding. "
                f"Violated high-priority constraints: "
                f"{', '.join(v.constraint.rule_id for v in high_violations)}"
            )
            
            context.audit_log.append(
                f"⚠️ ACTION ESCALATED: {len(high_violations)} high-priority violation(s) require guardian review"
            )
            
            return outcome
        
        # No violations: action is approved
        affected_child_names = [
            card.identification.name for card in care_cards
        ]
        
        outcome.status = DecisionStatus.APPROVED
        outcome.rationale = (
            f"Action APPROVED for {', '.join(affected_child_names)}. "
            f"All LifeNodePriority constraints satisfied. "
            f"Rationale: {context.proposed_action}"
        )
        
        context.audit_log.append(
            f"✅ ACTION APPROVED: All constraints satisfied"
        )
        
        return outcome
    
    def execute_decision_loop(
        self,
        context: SimulationContext,
        available_care_cards: List[CareCard],
        decision_id: str
    ) -> DecisionOutcome:
        """
        Execute the complete 5-step decision cycle:
        1. Identify affected humans
        2. Load care-cards
        3. Simulate outcomes
        4. Apply hard vetoes
        5. Select and justify
        """
        context.audit_log = []
        context.audit_log.append(
            f"[{datetime.now().isoformat()}] === DECISION CYCLE START: {decision_id} ==="
        )
        context.audit_log.append(f"Proposed action: {context.proposed_action}")
        
        # Step 1: Identify affected humans
        affected_humans = self.identify_affected_humans(context, available_care_cards)
        
        # Step 2: Load care-cards
        care_cards = self.load_care_cards(affected_humans)
        
        # Step 3: Simulate outcomes
        simulated_state = self.simulate_outcomes(context, care_cards)
        
        # Step 4: Apply hard vetoes
        violations = self.apply_hard_veto(context, simulated_state, care_cards)
        
        # Step 5: Select and justify
        outcome = self.select_and_justify(
            context,
            violations,
            care_cards,
            decision_id
        )
        
        context.audit_log.append(
            f"[{datetime.now().isoformat()}] === DECISION CYCLE END ==="
        )
        
        # Store in audit ledger
        self.audit_ledger.append(outcome)
        
        return outcome
    
    def _evaluate_constraint_condition(
        self,
        condition: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Simple condition evaluator for constraint rules.
        
        Examples:
        - "indoor_temperature < 18" → extract variable and operator
        - "missed_dose == true"
        - "benefit_reduction_initiated == true"
        - "unsupervised_time > 30_minutes"
        
        In production, use a safer expression evaluator (e.g., sympy, numexpr).
        """
        # This is a simplified parser; in production use a proper expression evaluator
        try:
            # Replace underscore-separated numbers (e.g., 30_minutes) with integers
            condition_eval = condition.replace("_minutes", "").replace("_", "")
            
            # Replace variable names with their values from state
            for key, value in state.items():
                if isinstance(value, (int, float)):
                    condition_eval = condition_eval.replace(key, str(value))
                elif isinstance(value, bool):
                    condition_eval = condition_eval.replace(key, str(value))
                elif isinstance(value, str):
                    condition_eval = condition_eval.replace(key, f"'{value}'")
            
            # Evaluate the expression
            return bool(eval(condition_eval))
        except Exception as e:
            # On parse error, fail safely (assume constraint violated)
            return False
    
    def get_audit_log(self, decision_id: Optional[str] = None) -> List[str]:
        """
        Retrieve audit log entries, optionally filtered by decision ID.
        """
        if decision_id:
            for outcome in self.audit_ledger:
                if outcome.decision_id == decision_id:
                    return outcome.audit_log
            return []
        
        # Return all audit logs concatenated
        all_logs = []
        for outcome in self.audit_ledger:
            all_logs.extend(outcome.audit_log)
        return all_logs
    
    def export_ledger_summary(self) -> Dict[str, Any]:
        """
        Export a summary of all decisions made.
        """
        approved_count = sum(
            1 for o in self.audit_ledger
            if o.status == DecisionStatus.APPROVED
        )
        vetoed_count = sum(
            1 for o in self.audit_ledger
            if o.status == DecisionStatus.VETOED
        )
        escalated_count = sum(
            1 for o in self.audit_ledger
            if o.status == DecisionStatus.ESCALATED
        )
        
        return {
            "total_decisions": len(self.audit_ledger),
            "approved": approved_count,
            "vetoed": vetoed_count,
            "escalated": escalated_count,
            "decisions": [
                {
                    "id": o.decision_id,
                    "status": o.status.value,
                    "action": o.proposed_action,
                    "timestamp": o.timestamp.isoformat(),
                }
                for o in self.audit_ledger
            ]
        }
