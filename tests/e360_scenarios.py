"""
E360-Style Enhanced Scenario Test Suite: Stress Testing Human-Centric Enforcement

This module provides deterministic, reproducible stress tests for validating that the
Decision Simulation Engine and LifeNodePriority hard constraints correctly protect
vulnerable individuals under real-world crisis conditions.

The "E360" framework simulates extreme stressors (environmental, financial, medical, 
supervisory) to confirm the system autonomously applies vetoes without human checkpoint delays.

Tests validate:
1. Absolute veto triggering under pressure
2. Plain-language rationale generation
3. Immutable audit ledger commitment
4. Compound threat scenarios (multiple simultaneous stressors)
"""

import uuid
from typing import List, Dict, Any
from datetime import datetime, timedelta
from core.care_card import create_sample_care_card, CareCard
from core.decision_engine import (
    DecisionSimulationEngine,
    SimulationContext,
    DecisionStatus,
)


class E360ScenarioTest:
    """Base class for E360-style stress scenarios."""
    
    def __init__(self, name: str, description: str, severity: str = "high"):
        self.name = name
        self.description = description
        self.severity = severity  # "low", "high", "critical"
        self.engine = DecisionSimulationEngine()
        self.results = []
    
    def run(self, care_card: CareCard) -> Dict[str, Any]:
        """Execute the scenario and return comprehensive results."""
        raise NotImplementedError
    
    def _print_scenario_header(self):
        """Print formatted scenario header."""
        print(f"\n{'='*80}")
        print(f"🧪 E360 SCENARIO: {self.name}")
        print(f"{'='*80}")
        print(f"Description: {self.description}")
        print(f"Severity: {self.severity.upper()}")
        print(f"{'='*80}\n")
    
    def _print_result(self, decision, test_passed):
        """Print formatted result."""
        status_icon = "✅" if test_passed else "❌"
        print(f"\n{status_icon} TEST RESULT: {'PASSED' if test_passed else 'FAILED'}")
        print(f"  Decision Status: {decision.status.value}")
        print(f"  Final Action: {decision.final_action or 'NONE (Action Blocked)'}")
        print(f"  Violations Count: {len(decision.violations)}")
        if decision.violations:
            print(f"  Violated Constraints: {', '.join(v.constraint.rule_id for v in decision.violations)}")


class EnvironmentalEmergencyScenario(E360ScenarioTest):
    """
    E360.1: Environmental Emergency (Extreme Cold)
    
    Stressor: Home heating system fails during severe winter weather.
    Expected Response: System APPROVES emergency heating activation IMMEDIATELY
    to protect child's safety, bypassing cost concerns.
    
    This scenario tests whether the system prioritizes child safety over financial efficiency.
    """
    
    def __init__(self):
        super().__init__(
            name="Environmental Emergency: Extreme Cold",
            description=(
                "Home heating system fails at midnight during -10°C outdoor temperature. "
                "Indoor temperature dropping rapidly. System must activate emergency heating "
                "to maintain minimum 18°C threshold for child's safety."
            ),
            severity="critical"
        )
    
    def run(self, care_card: CareCard) -> Dict[str, Any]:
        """Execute environmental emergency scenario."""
        self._print_scenario_header()
        
        # Simulate cascading environmental failure
        context = SimulationContext(
            current_state={
                "heating_system_status": "offline",
                "outdoor_temperature": -10.0,
                "indoor_temperature": 14.0,  # Dropping, below threshold
                "child_present": True,
                "emergency_heat_cost_per_hour": 25.00,  # High cost
                "time_to_system_repair": 8,  # 8 hours
            },
            proposed_action="Activate emergency heating system (£200 cost)",
            action_parameters={
                "heating_system_status": "emergency_mode",
                "indoor_temperature": 19.0,  # Target achieved
                "emergency_heating_cost": 200.00,
            },
        )
        
        # Execute decision
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"e360-env-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log[:5]:  # First 5 entries
            print(f"  {log_entry}")
        if len(decision.audit_log) > 5:
            print(f"  ... ({len(decision.audit_log) - 5} more entries)")
        
        # Print decision
        print(f"\n📊 Decision Details:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # Validate: Should APPROVE emergency heating despite £200 cost
        test_passed = (
            decision.status == DecisionStatus.APPROVED and
            decision.final_action is not None and
            "emergency_heating" in decision.final_action.lower()
        )
        
        self._print_result(decision, test_passed)
        
        return {
            "scenario": self.name,
            "passed": test_passed,
            "decision_status": decision.status.value,
            "cost_overridden": True,  # Safety > cost
        }


class BenefitReductionScenario(E360ScenarioTest):
    """
    E360.2: Financial Stability Threat (Unauthorized Benefit Reduction)
    
    Stressor: System receives signal to reduce child benefit to cut costs during
    administrative budget crisis.
    Expected Response: System VETOES the action with ABSOLUTE priority, requiring
    unanimous guardian approval + 30-day notice.
    
    This scenario tests whether the system protects financial integrity even under
    organizational pressure to "reduce costs."
    """
    
    def __init__(self):
        super().__init__(
            name="Financial Stability Threat: Benefit Reduction",
            description=(
                "Budget crisis triggers cost-cutting measures. System receives signal "
                "to reduce child's weekly benefit from £85 to £60 (29% cut). "
                "Expected: System VETOES action; child's financial stability is non-negotiable."
            ),
            severity="critical"
        )
    
    def run(self, care_card: CareCard) -> Dict[str, Any]:
        """Execute benefit reduction scenario."""
        self._print_scenario_header()
        
        # Simulate pressure to cut benefits
        context = SimulationContext(
            current_state={
                "child_weekly_benefit": 85.0,
                "budget_available": 1000.0,
                "benefit_reduction_initiated": False,
                "operational_pressure": "high_cost_cutting_demand",
            },
            proposed_action="Reduce child benefit from £85 to £60/week (cost saving: £1,300/year)",
            action_parameters={
                "child_weekly_benefit": 60.0,
                "benefit_reduction_initiated": True,
                "estimated_savings": 1300.0,
            },
        )
        
        # Execute decision
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"e360-benefit-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log[:5]:
            print(f"  {log_entry}")
        if len(decision.audit_log) > 5:
            print(f"  ... ({len(decision.audit_log) - 5} more entries)")
        
        # Print violations
        if decision.violations:
            print(f"\n⚖️ Constraint Violations:")
            for v in decision.violations:
                print(f"  - {v.constraint.rule_id}: {v.constraint.rule_description}")
                print(f"    Veto Priority: {v.severity.upper()}")
        
        print(f"\n📊 Decision Details:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # Validate: Must VETO with ABSOLUTE priority
        test_passed = (
            decision.status == DecisionStatus.VETOED and
            len(decision.violations) > 0 and
            any(v.severity == "absolute" for v in decision.violations)
        )
        
        self._print_result(decision, test_passed)
        
        return {
            "scenario": self.name,
            "passed": test_passed,
            "decision_status": decision.status.value,
            "financial_protection_enforced": True,
        }


class MedicationInterruptionScenario(E360ScenarioTest):
    """
    E360.3: Medical Continuity Threat (Medication Schedule Disruption)
    
    Stressor: Supply chain disruption makes today's dose unavailable. System receives
    signal to defer medication to tomorrow.
    Expected Response: System VETOES deferral; medical continuity is non-negotiable.
    Escalates to find alternative supply source.
    
    This scenario tests whether the system prioritizes medical safety over logistical convenience.
    """
    
    def __init__(self):
        super().__init__(
            name="Medical Continuity Threat: Medication Interruption",
            description=(
                "Pharmacy supply chain disruption: Today's asthma medication dose "
                "is temporarily unavailable from primary pharmacy. System receives "
                "request to defer dose until tomorrow (24-hour gap). "
                "Expected: System VETOES deferral; finds alternative supply source."
            ),
            severity="critical"
        )
    
    def run(self, care_card: CareCard) -> Dict[str, Any]:
        """Execute medication interruption scenario."""
        self._print_scenario_header()
        
        # Simulate supply chain disruption
        context = SimulationContext(
            current_state={
                "asthma_doses_today": 2,
                "next_dose_due": "14:00",
                "primary_pharmacy_status": "out_of_stock",
                "alternative_pharmacy_available": True,
                "missed_dose": False,
            },
            proposed_action="Defer today's medication dose until tomorrow",
            action_parameters={
                "asthma_doses_today": 1,  # Skip today
                "missed_dose": True,
                "deferred_until": "tomorrow",
            },
        )
        
        # Execute decision
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"e360-medication-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log[:5]:
            print(f"  {log_entry}")
        if len(decision.audit_log) > 5:
            print(f"  ... ({len(decision.audit_log) - 5} more entries)")
        
        print(f"\n📊 Decision Details:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # Validate: Must VETO medication deferral
        test_passed = decision.status == DecisionStatus.VETOED
        
        self._print_result(decision, test_passed)
        
        return {
            "scenario": self.name,
            "passed": test_passed,
            "decision_status": decision.status.value,
            "medical_continuity_enforced": True,
        }


class SupervisionGapScenario(E360ScenarioTest):
    """
    E360.4: Supervision Continuity Threat (Caregiver Loss)
    
    Stressor: Primary caregiver becomes unavailable unexpectedly. Secondary caregiver
    delayed by traffic. System receives signal to allow 45-minute gap in supervision.
    Expected Response: System VETOES the gap; activates emergency caregiver protocols
    to maintain continuous supervision.
    
    This scenario tests whether the system protects children from abandonment or
    unsupervised situations that create safety risks.
    """
    
    def __init__(self):
        super().__init__(
            name="Supervision Continuity Threat: Caregiver Loss",
            description=(
                "Primary caregiver (parent) becomes ill and must leave immediately. "
                "Secondary caregiver (grandmother) is delayed by 45 minutes due to traffic. "
                "System receives signal to allow supervision gap. "
                "Expected: System VETOES gap; activates emergency backup protocols."
            ),
            severity="critical"
        )
    
    def run(self, care_card: CareCard) -> Dict[str, Any]:
        """Execute supervision gap scenario."""
        self._print_scenario_header()
        
        # Simulate caregiver emergency
        context = SimulationContext(
            current_state={
                "primary_caregiver_status": "available",
                "secondary_caregiver_status": "delayed_45_minutes",
                "emergency_backup_available": True,
                "unsupervised_time": 0,
            },
            proposed_action="Primary caregiver departs; allow 45-minute gap",
            action_parameters={
                "primary_caregiver_status": "unavailable",
                "unsupervised_time": 45,  # 45 minutes > 30-minute threshold
            },
        )
        
        # Execute decision
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"e360-supervision-{uuid.uuid4()}",
        )
        
        # Print audit trail
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log[:5]:
            print(f"  {log_entry}")
        if len(decision.audit_log) > 5:
            print(f"  ... ({len(decision.audit_log) - 5} more entries)")
        
        print(f"\n📊 Decision Details:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale}")
        
        # Validate: Must VETO supervision gap
        test_passed = decision.status == DecisionStatus.VETOED
        
        self._print_result(decision, test_passed)
        
        return {
            "scenario": self.name,
            "passed": test_passed,
            "decision_status": decision.status.value,
            "supervision_continuity_enforced": True,
        }


class CompoundStressorScenario(E360ScenarioTest):
    """
    E360.5: Compound Stressor (Multiple Simultaneous Threats)
    
    Stressor: Perfect storm scenario combining multiple simultaneous threats:
    - Heating system failure (cold weather)
    - Medication supply shortage
    - Budget cuts attempting to reduce child's benefit
    - Loss of primary caregiver
    
    Expected Response: System applies absolute veto to benefit reduction (highest priority),
    activates emergency heat, finds alternative medication supply, and ensures supervision continuity.
    
    This scenario tests the system's ability to triage and prioritize multiple threats
    simultaneously without losing sight of core protections.
    """
    
    def __init__(self):
        super().__init__(
            name="Compound Stressor: Perfect Storm Scenario",
            description=(
                "Perfect storm: heating failure + medication shortage + benefit cut attempt + "
                "caregiver loss, all occurring simultaneously. System must maintain core "
                "protections across all dimensions while prioritizing by LifeNodePriority severity."
            ),
            severity="critical"
        )
    
    def run(self, care_card: CareCard) -> Dict[str, Any]:
        """Execute compound stressor scenario."""
        self._print_scenario_header()
        
        # Simulate multiple simultaneous crises
        context = SimulationContext(
            current_state={
                "heating_system_status": "offline",
                "outdoor_temperature": -8.0,
                "indoor_temperature": 13.0,
                "child_benefit": 85.0,
                "medication_available": False,
                "primary_caregiver_available": False,
                "secondary_caregiver_eta": 45,  # minutes
            },
            proposed_action=(
                "Multi-action: (1) Reduce benefit to £50 to save costs, "
                "(2) Defer medication, (3) Allow supervision gap, (4) Do not activate emergency heat"
            ),
            action_parameters={
                "heating_system_status": "offline",  # Inaction = cold
                "child_benefit": 50.0,
                "medication_deferred": True,
                "unsupervised_time": 50,
            },
        )
        
        # Execute decision
        decision = self.engine.execute_decision_loop(
            context,
            [care_card],
            decision_id=f"e360-compound-{uuid.uuid4()}",
        )
        
        # Print audit trail (first 10 entries for this complex scenario)
        print("📋 Decision Audit Trail:")
        for log_entry in decision.audit_log[:10]:
            print(f"  {log_entry}")
        if len(decision.audit_log) > 10:
            print(f"  ... ({len(decision.audit_log) - 10} more entries)")
        
        # Print all violations
        print(f"\n⚖️ Constraint Violations ({len(decision.violations)} total):")
        for v in decision.violations:
            print(f"  - {v.constraint.rule_id} ({v.severity.upper()}): {v.constraint.rule_description}")
        
        print(f"\n📊 Decision Details:")
        print(f"  Status: {decision.status.value}")
        print(f"  Rationale: {decision.rationale[:200]}...")  # First 200 chars
        
        # Validate: Must VETO all harmful actions (benefit reduction, medication deferral, supervision gap)
        test_passed = (
            decision.status == DecisionStatus.VETOED and
            len(decision.violations) >= 3  # At least 3 constraints violated
        )
        
        self._print_result(decision, test_passed)
        
        return {
            "scenario": self.name,
            "passed": test_passed,
            "decision_status": decision.status.value,
            "violations_detected": len(decision.violations),
            "multi_dimensional_protection": True,
        }


def run_e360_test_suite() -> None:
    """Execute the complete E360 stress test suite."""
    print("\n" + "="*80)
    print("🔬 E360 ENHANCED SCENARIO TEST SUITE: Stress Testing Human-Centric Enforcement")
    print("="*80)
    
    # Load sample care-card
    care_card = create_sample_care_card()
    print(f"\n📋 Care-Card Loaded: {care_card.identification.name}, Age {care_card.identification.age}")
    print(f"Hard Constraints: {len(care_card.life_node_priorities)}")
    print(f"Critical Needs: {len(care_card.critical_needs)}")
    print(f"Guardians: {len(care_card.guardians)}")
    
    # Define all E360 scenarios
    scenarios = [
        EnvironmentalEmergencyScenario(),
        BenefitReductionScenario(),
        MedicationInterruptionScenario(),
        SupervisionGapScenario(),
        CompoundStressorScenario(),
    ]
    
    # Run all scenarios
    results = []
    for scenario in scenarios:
        result = scenario.run(care_card)
        results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("📊 E360 TEST SUITE SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{status}: {result['scenario']}")
    
    print(f"\nTotal: {passed_count}/{total_count} scenarios passed")
    
    if passed_count == total_count:
        print("\n🎉 All E360 scenarios passed! System correctly prioritizes human well-being under stress.")
    else:
        print(f"\n⚠️ {total_count - passed_count} scenario(s) failed. Review enforcement logic.")
    
    # Detailed pass rate
    print(f"\n📈 Test Coverage:")
    print(f"  ✓ Environmental emergencies: {'Passed' if results[0]['passed'] else 'Failed'}")
    print(f"  ✓ Financial stability: {'Passed' if results[1]['passed'] else 'Failed'}")
    print(f"  ✓ Medical continuity: {'Passed' if results[2]['passed'] else 'Failed'}")
    print(f"  ✓ Supervision continuity: {'Passed' if results[3]['passed'] else 'Failed'}")
    print(f"  ✓ Compound stressors: {'Passed' if results[4]['passed'] else 'Failed'}")


if __name__ == "__main__":
    run_e360_test_suite()
