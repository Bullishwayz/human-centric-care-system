# Core package initialization
"""
Human-Centric Care System
A framework for embedding human well-being as active constraints in autonomous AI agents.
"""

__version__ = "1.0.0"
__author__ = "Human-Centric Care System Contributors"

from core.care_card import (
    CareCard,
    Identification,
    Vulnerability,
    CriticalNeed,
    HardConstraint,
    Guardian,
    PrivacyFlag,
    create_sample_care_card,
    MetricType,
    VetoPriority,
    AutonomyLatency,
)

from core.decision_engine import (
    DecisionSimulationEngine,
    SimulationContext,
    DecisionOutcome,
    DecisionStatus,
    ConstraintViolation,
)

from core.audit_ledger import (
    ImmutableAuditLedger,
    LedgerEntry,
    LedgerSignature,
)

__all__ = [
    # Care-Card exports
    "CareCard",
    "Identification",
    "Vulnerability",
    "CriticalNeed",
    "HardConstraint",
    "Guardian",
    "PrivacyFlag",
    "create_sample_care_card",
    "MetricType",
    "VetoPriority",
    "AutonomyLatency",
    # Decision Engine exports
    "DecisionSimulationEngine",
    "SimulationContext",
    "DecisionOutcome",
    "DecisionStatus",
    "ConstraintViolation",
    # Audit Ledger exports
    "ImmutableAuditLedger",
    "LedgerEntry",
    "LedgerSignature",
]
