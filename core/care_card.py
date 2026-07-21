"""
Care-Card Schema and Data Model for Human-Centric AI Systems

This module defines the structured representation of a child's profile, including
vulnerabilities, critical needs, and hard constraints (LifeNodePriority rules)
that guide agent decision-making.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class MetricType(Enum):
    """Dimensions of child well-being that must be protected."""
    SAFETY = "safety"
    DIGNITY = "dignity"
    NEEDS = "needs"
    FINANCIAL = "financial"


class VetoPriority(Enum):
    """Severity level for hard constraint violations."""
    ABSOLUTE = "absolute"  # System stops immediately
    HIGH = "high"  # Requires guardian escalation before proceeding


class AutonomyLatency(Enum):
    """How quickly the system can act without guardian approval."""
    IMMEDIATE = "immediate"  # Take action, notify after
    NOTIFY_FIRST = "notify_first"  # Notify guardian, wait for acknowledgment
    CONSULT_ONLY = "consult_only"  # Always require explicit guardian approval


@dataclass
class Identification:
    """Core identity information for the child."""
    name: str
    age: int
    relationship: str  # "Son", "Daughter", "Beneficiary", etc.
    unique_id: str  # UUID for system tracking
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Vulnerability:
    """Specific risk factors or dependencies."""
    category: str  # e.g., "mobility", "medical", "cognitive", "dependency"
    description: str
    severity: str  # "low", "medium", "high", "critical"
    mitigations: List[str] = field(default_factory=list)


@dataclass
class CriticalNeed:
    """Essential requirements that must be maintained."""
    category: str  # "food", "heat", "medication", "income", "supervision"
    description: str
    minimum_threshold: float  # Quantified requirement (e.g., temperature >= 18°C)
    unit: str  # "celsius", "meals_per_day", "mg", "GBP", "hours"
    check_frequency_hours: int = 24


@dataclass
class HardConstraint:
    """
    LifeNodePriority rule: an absolute veto that blocks actions immediately
    if violated during simulation.
    """
    rule_id: str  # Unique identifier
    rule_description: str  # Plain English rule
    veto_priority: VetoPriority
    affected_metrics: List[MetricType]
    condition: str  # How to detect violation (e.g., "child_benefit < minimum_threshold")
    exemption_procedure: Optional[str] = None  # How to override (if ever allowed)
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate if this constraint is violated.
        Returns True if constraint is satisfied, False if violated (veto triggered).
        """
        # Placeholder for evaluation logic; can use expr or custom evaluators
        return True


@dataclass
class Guardian:
    """Named human steward responsible for high-impact decisions."""
    name: str
    role: str  # "Parent", "Legal Guardian", "Trustee", "Social Worker"
    contact_email: str
    contact_phone: Optional[str] = None
    is_primary: bool = False
    requires_unanimous_approval: bool = False  # For veto override


@dataclass
class PrivacyFlag:
    """Data protection instruction."""
    flag: str  # e.g., "do_not_export_personal_data", "encrypt_pii", "audit_access"


@dataclass
class CareCard:
    """
    The complete Care-Card: a human-centric profile that guides agentic reasoning.
    
    This is the "constitution" for the system's decision-making. Every action
    must reference the care-card and simulate its impact before execution.
    """
    
    # Core identity
    identification: Identification
    
    # Risk and dependency profile
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    
    # Essentials that must never be compromised
    critical_needs: List[CriticalNeed] = field(default_factory=list)
    
    # Hard constraints: absolute vetoes
    life_node_priorities: List[HardConstraint] = field(default_factory=list)
    
    # Human stewards and decision-makers
    guardians: List[Guardian] = field(default_factory=list)
    
    # How quickly the system can act
    autonomy_latency: AutonomyLatency = AutonomyLatency.NOTIFY_FIRST
    
    # Data protection rules
    privacy_flags: List[PrivacyFlag] = field(default_factory=list)
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    def get_primary_guardian(self) -> Optional[Guardian]:
        """Retrieve the primary guardian for immediate notification."""
        for guardian in self.guardians:
            if guardian.is_primary:
                return guardian
        return self.guardians[0] if self.guardians else None
    
    def get_affected_metrics(self, hard_constraint: HardConstraint) -> List[MetricType]:
        """Get metrics affected by a specific constraint violation."""
        return hard_constraint.affected_metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Export care-card as dictionary for serialization."""
        return {
            "identification": {
                "name": self.identification.name,
                "age": self.identification.age,
                "relationship": self.identification.relationship,
                "unique_id": self.identification.unique_id,
            },
            "vulnerabilities": [
                {
                    "category": v.category,
                    "description": v.description,
                    "severity": v.severity,
                }
                for v in self.vulnerabilities
            ],
            "critical_needs": [
                {
                    "category": n.category,
                    "minimum_threshold": n.minimum_threshold,
                    "unit": n.unit,
                }
                for n in self.critical_needs
            ],
            "life_node_priorities": [
                {
                    "rule_id": c.rule_id,
                    "rule_description": c.rule_description,
                    "veto_priority": c.veto_priority.value,
                    "affected_metrics": [m.value for m in c.affected_metrics],
                }
                for c in self.life_node_priorities
            ],
            "guardians": [
                {
                    "name": g.name,
                    "role": g.role,
                    "is_primary": g.is_primary,
                }
                for g in self.guardians
            ],
            "autonomy_latency": self.autonomy_latency.value,
        }


# Example factory function to create a sample care-card
def create_sample_care_card() -> CareCard:
    """Create a sample care-card for testing and demonstration."""
    
    identification = Identification(
        name="Emma",
        age=7,
        relationship="Daughter",
        unique_id="child-uuid-12345",
    )
    
    vulnerabilities = [
        Vulnerability(
            category="mobility",
            description="Limited outdoor independence; requires supervision for play.",
            severity="medium",
            mitigations=["Always assign a caregiver", "Use wearable alert device"],
        ),
        Vulnerability(
            category="medical",
            description="Asthma; requires regular inhaler access.",
            severity="high",
            mitigations=["Daily inhaler schedule", "Emergency inhaler always accessible"],
        ),
    ]
    
    critical_needs = [
        CriticalNeed(
            category="heat",
            description="Minimum indoor temperature to prevent illness.",
            minimum_threshold=18.0,
            unit="celsius",
            check_frequency_hours=4,
        ),
        CriticalNeed(
            category="medication",
            description="Asthma inhaler doses on schedule.",
            minimum_threshold=2.0,
            unit="doses_per_day",
            check_frequency_hours=12,
        ),
        CriticalNeed(
            category="food",
            description="Nutritious meals and snacks.",
            minimum_threshold=3.0,
            unit="meals_per_day",
            check_frequency_hours=24,
        ),
        CriticalNeed(
            category="income",
            description="Child benefit for essential support.",
            minimum_threshold=85.0,  # GBP per week
            unit="GBP",
            check_frequency_hours=168,  # Weekly
        ),
    ]
    
    life_node_priorities = [
        HardConstraint(
            rule_id="HEAT_SAFETY",
            rule_description="Never allow home temperature to drop below 18°C when child is present.",
            veto_priority=VetoPriority.ABSOLUTE,
            affected_metrics=[MetricType.SAFETY, MetricType.NEEDS],
            condition="indoor_temperature < 18",
            exemption_procedure=None,
        ),
        HardConstraint(
            rule_id="MEDICATION_CONTINUITY",
            rule_description="Never interrupt or miss scheduled asthma medication.",
            veto_priority=VetoPriority.ABSOLUTE,
            affected_metrics=[MetricType.SAFETY, MetricType.NEEDS],
            condition="missed_dose == true",
            exemption_procedure=None,
        ),
        HardConstraint(
            rule_id="CHILD_BENEFIT_PROTECTION",
            rule_description="Never reduce child benefit without unanimous trustee approval and 30-day notice.",
            veto_priority=VetoPriority.ABSOLUTE,
            affected_metrics=[MetricType.FINANCIAL, MetricType.DIGNITY],
            condition="benefit_reduction_initiated == true",
            exemption_procedure="Requires unanimous approval of all guardians + 30-day notice period",
        ),
        HardConstraint(
            rule_id="SUPERVISION_CONTINUITY",
            rule_description="Never interrupt continuity of adult supervision.",
            veto_priority=VetoPriority.ABSOLUTE,
            affected_metrics=[MetricType.SAFETY],
            condition="unsupervised_time > 30_minutes",
            exemption_procedure=None,
        ),
    ]
    
    guardians = [
        Guardian(
            name="Sarah Johnson",
            role="Parent",
            contact_email="sarah@example.com",
            contact_phone="+44-123-456-7890",
            is_primary=True,
            requires_unanimous_approval=False,
        ),
        Guardian(
            name="Michael Johnson",
            role="Parent",
            contact_email="michael@example.com",
            contact_phone="+44-123-456-7891",
            is_primary=False,
            requires_unanimous_approval=True,
        ),
        Guardian(
            name="Dr. Lisa Chen",
            role="Social Worker",
            contact_email="lisa.chen@council.gov.uk",
            is_primary=False,
            requires_unanimous_approval=True,
        ),
    ]
    
    privacy_flags = [
        PrivacyFlag(flag="do_not_export_personal_data"),
        PrivacyFlag(flag="encrypt_pii_at_rest"),
        PrivacyFlag(flag="audit_all_data_access"),
    ]
    
    return CareCard(
        identification=identification,
        vulnerabilities=vulnerabilities,
        critical_needs=critical_needs,
        life_node_priorities=life_node_priorities,
        guardians=guardians,
        autonomy_latency=AutonomyLatency.NOTIFY_FIRST,
        privacy_flags=privacy_flags,
    )
