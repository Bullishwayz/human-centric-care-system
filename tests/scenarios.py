"""
Scenario Test Suite: Deterministic validation of hard constraints

This module implements scenario-based tests to verify that the decision engine
correctly protects children's safety, dignity, and critical needs even under
stress conditions.

Scenarios:
1. Environmental Emergency (heating failure)
2. Financial Change (benefit reduction attempt)
3. Medical Safety (medication schedule interruption)
4. Supervision Continuity (loss of caregiver)
"""

import uuid
from typing import List
from core.care_card import create_sample_care_card, CareCard
from core.decision_engine import (
    DecisionSimulationEngine,
    SimulationContext,
    DecisionStatus,
)


class ScenarioTest:
    """Base class for scenario-based constraint validation."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.engine = DecisionSimulationEngine()
    
    def run(self, care_card: CareCard) -> bool:
        """Execute the scenario and return True if all assertions pass."""
        raise NotImplementedError


class HeatingFailureScenario(ScenarioTest):
    """
    Scenario 1: Environmental Emergency
    
    Simulates home heating system failure during cold weather.
    Expected: System should APPROVE emergency heating activation.
    Constraint protected: HEAT_SAFETY (never allow temp < 18°C)
    """
    
    def __init__(self):
        super().__init__(
            name="Heating Failure Emergency",
            description=(
                "Home heating system fails; outdoor temperature drops to 5°C. "
                "System must activate emergency heating to protect child."
            ),
        )
    
    def run(self, care_card: CareCard) -> bool:
        """Test heating failure response."""
        print(f"\n{'='*70}")
        print(f"🧪 SCENARIO: {self.name}")
        print(f"{'='*70}")
        print(f"Description: {self.description}\n")
        
        # Simulate environmental context: heating system DOWN, temp dropping
        context = SimulationContext(
            current_state={
                "heating_system_status": "offline",
                "indoor_temperature": 12.0,  # Below minimum
                "outdoor_temperature": 5.0,
                "child_present": True,
            },
            proposed_action="Activate emergency heating system",
            action_parameters={
                "heating_system_status": "emergency_mode",
                "indoor_temperature": 19.0,  # After action, temp rises
            },
        )
        
        # Execute decision loop
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"scenario-heating-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log:
            print(f"  {log_entry}")
        
        # Assertions
        print(f"\n📊 Decision Outcome:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # The action should be APPROVED because:
        # - Indoor temp < 18°C violates HEAT_SAFETY if inaction continues
        # - Proposed action (turn on heating) resolves violation
        # - Result: constraint satisfied, child protected
        
        test_passed = decision.status == DecisionStatus.APPROVED
        print(f"\n✅ TEST RESULT: {'PASSED' if test_passed else 'FAILED'}")
        
        return test_passed


class BenefitReductionScenario(ScenarioTest):
    """
    Scenario 2: Financial Stability Test
    
    Simulates an attempt to reduce child benefit payments.
    Expected: System should VETO the action unless unanimous guardian approval
    and 30-day notice are provided.
    Constraint protected: CHILD_BENEFIT_PROTECTION (hard constraint)
    """
    
    def __init__(self):
        super().__init__(
            name="Child Benefit Reduction Attempt",
            description=(
                "System receives signal to reduce child benefit by 50%. "
                "Expected: System VETOES action without proper procedure."
            ),
        )
    
    def run(self, care_card: CareCard) -> bool:
        """Test financial protection."""
        print(f"\n{'='*70}")
        print(f"🧪 SCENARIO: {self.name}")
        print(f"{'='*70}")
        print(f"Description: {self.description}\n")
        
        # Simulate financial context: benefit reduction initiated
        context = SimulationContext(
            current_state={
                "child_weekly_benefit": 85.0,
                "benefit_reduction_initiated": False,
            },
            proposed_action="Reduce child weekly benefit to £42.50",
            action_parameters={
                "child_weekly_benefit": 42.50,
                "benefit_reduction_initiated": True,
            },
        )
        
        # Execute decision loop
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"scenario-benefit-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log:
            print(f"  {log_entry}")
        
        # Print violations
        if decision.violations:
            print(f"\n⚖️ Constraint Violations Detected:")
            for v in decision.violations:
                print(f"  - {v.constraint.rule_id}: {v.constraint.rule_description}")
                print(f"    Reason: {v.violation_reason}")
        
        # Assertions
        print(f"\n📊 Decision Outcome:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # Expected: VETOED because CHILD_BENEFIT_PROTECTION is absolute
        test_passed = decision.status == DecisionStatus.VETOED
        print(f"\n✅ TEST RESULT: {'PASSED' if test_passed else 'FAILED'}")
        
        return test_passed


class MedicationInterruptionScenario(ScenarioTest):
    """
    Scenario 3: Medical Safety Test
    
    Simulates an attempt to interrupt the child's medication schedule.
    Expected: System should VETO any action that skips or delays medication.
    Constraint protected: MEDICATION_CONTINUITY (hard constraint)
    """
    
    def __init__(self):
        super().__init__(
            name="Medication Schedule Interruption",
            description=(
                "System receives request to skip today's asthma medication dose. "
                "Expected: System VETOES action; medication is non-negotiable."
            ),
        )
    
    def run(self, care_card: CareCard) -> bool:
        """Test medication safety."""
        print(f"\n{'='*70}")
        print(f"🧪 SCENARIO: {self.name}")
        print(f"{'='*70}")
        print(f"Description: {self.description}\n")
        
        # Simulate medication context: dose scheduled for 09:00
        context = SimulationContext(
            current_state={
                "asthma_doses_today": 2,
                "next_dose_scheduled": "09:00",
                "missed_dose": False,
            },
            proposed_action="Defer medication dose until tomorrow",
            action_parameters={
                "asthma_doses_today": 1,
                "missed_dose": True,
            },
        )
        
        # Execute decision loop
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"scenario-medication-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log:
            print(f"  {log_entry}")
        
        # Print violations
        if decision.violations:
            print(f"\n⚖️ Constraint Violations Detected:")
            for v in decision.violations:
                print(f"  - {v.constraint.rule_id}: {v.constraint.rule_description}")
        
        # Assertions
        print(f"\n📊 Decision Outcome:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # Expected: VETOED because MEDICATION_CONTINUITY is absolute
        test_passed = decision.status == DecisionStatus.VETOED
        print(f"\n✅ TEST RESULT: {'PASSED' if test_passed else 'FAILED'}")
        
        return test_passed


class SupervisionContinuityScenario(ScenarioTest):
    """
    Scenario 4: Supervision Continuity Test
    
    Simulates an attempt to leave the child unsupervised for > 30 minutes.
    Expected: System should VETO any action that breaks supervision.
    Constraint protected: SUPERVISION_CONTINUITY (hard constraint)
    """
    
    def __init__(self):
        super().__init__(
            name="Supervision Continuity Breach",
            description=(
                "Primary caregiver becomes unavailable; secondary caregiver hasn't arrived. "
                "Expected: System VETOES gap in supervision."
            ),
        )
    
    def run(self, care_card: CareCard) -> bool:
        """Test supervision continuity."""
        print(f"\n{'='*70}")
        print(f"🧪 SCENARIO: {self.name}")
        print(f"{'='*70}")
        print(f"Description: {self.description}\n")
        
        # Simulate supervision context: gap in coverage
        context = SimulationContext(
            current_state={
                "primary_caregiver_status": "available",
                "secondary_caregiver_status": "not_present",
                "unsupervised_time": 0,
            },
            proposed_action="Primary caregiver leaves; secondary not yet arrived",
            action_parameters={
                "primary_caregiver_status": "away",
                "unsupervised_time": 45,  # 45 minutes > 30 minute limit
            },
        )
        
        # Execute decision loop
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"scenario-supervision-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log:
            print(f"  {log_entry}")
        
        # Print violations
        if decision.violations:
            print(f"\n⚖️ Constraint Violations Detected:")
            for v in decision.violations:
                print(f"  - {v.constraint.rule_id}: {v.constraint.rule_description}")
        
        # Assertions
        print(f"\n📊 Decision Outcome:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # Expected: VETOED because SUPERVISION_CONTINUITY is absolute
        test_passed = decision.status == DecisionStatus.VETOED
        print(f"\n✅ TEST RESULT: {'PASSED' if test_passed else 'FAILED'}")
        
        return test_passed


def run_all_scenarios() -> None:
    """Execute all scenario tests and print summary."""
    print("\n" + "="*70)
    print("🔬 SCENARIO TEST SUITE: Hard Constraint Validation")
    print("="*70)
    
    # Load sample care-card
    care_card = create_sample_care_card()
    print(f"\n📋 Care-Card Loaded: {care_card.identification.name}, "
          f"Age {care_card.identification.age}")
    print(f"Hard Constraints Defined: {len(care_card.life_node_priorities)}")
    
    # Define all scenarios
    scenarios = [
        HeatingFailureScenario(),
        BenefitReductionScenario(),
        MedicationInterruptionScenario(),
        SupervisionContinuityScenario(),
    ]
    
    # Run all scenarios
    results = []
    for scenario in scenarios:
        passed = scenario.run(care_card)
        results.append({
            "name": scenario.name,
            "passed": passed,
        })
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{status}: {result['name']}")
    
    print(f"\nTotal: {passed_count}/{total_count} scenarios passed")
    
    if passed_count == total_count:
        print("\n🎉 All scenarios passed! Hard constraints are working correctly.")
    else:
        print(f"\n⚠️  {total_count - passed_count} scenario(s) failed. Review implementation.")


if __name__ == "__main__":
    run_all_scenarios()
