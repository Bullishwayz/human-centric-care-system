```markdown
# Human-Centric Care System: Architecture & Philosophy

## Overview

This system implements a **human-centric agentic AI architecture** designed to protect vulnerable individuals—particularly children—by embedding their safety, dignity, and well-being as active inputs in every decision cycle.

Rather than treating "human-in-the-loop" as a checkbox approval process, this system encodes the human as the *primary stakeholder* in the agent's reasoning loop. Every action the system considers is vetted against a structured **Care-Card**—a human profile containing vulnerabilities, critical needs, and hard constraints (LifeNodePriority rules) that cannot be violated.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Key Concepts](#key-concepts)
   - [Human-in-the-Loop Reasoning](#human-in-the-loop-reasoning)
   - [Care-Card Model](#care-card-model)
   - [LifeNodePriority Rules](#lifenode-priority-rules)
   - [Well-being Metrics](#well-being-metrics)
3. [System Architecture](#system-architecture)
4. [Decision Cycle](#decision-cycle)
5. [Hard Constraints vs. Soft Constraints](#hard-constraints-vs-soft-constraints)
6. [Sealed Enforcement & TEE Integration](#sealed-enforcement--tee-integration)
7. [Audit & Accountability](#audit--accountability)
8. [Quick Start](#quick-start)

---

## Core Philosophy

This system is built on the conviction that **autonomous AI agents must be architecturally incapable of disregarding human well-being**.

Traditional systems treat humans as external stakeholders who must "approve" AI decisions. This framework inverts that relationship:

- **The human's care-card is the system's "constitution"**
- **Every action must be simulated against this constitution before execution**
- **Hard constraints are not suggestions—they are vetos enforced at runtime**

This approach ensures that even when a human is not present to click "approve," the system is still actively "thinking" about them and their needs.

---

## Key Concepts

### Human-in-the-Loop Reasoning

**What it is NOT:**
- A checkbox where a human rubber-stamps the AI's output
- A notification system that alerts a human and then delays action
- A "human override" that is optional or slow

**What it IS:**
- A continuous, internal reasoning process where the human's vulnerabilities and needs are active inputs in every decision
- The agent simulates the impact of candidate actions on the human's life before choosing one
- The system is structurally incapable of proposing an action that violates the human's LifeNodePriority rules

**The 5-Step Decision Loop:**

```
1. IDENTIFY → Who will be affected by this action?
2. LOAD → Retrieve the human's Care-Card (vulnerabilities, needs, constraints)
3. SIMULATE → Run a "mental rehearsal" of candidate actions
4. VETO → Apply hard constraints; discard any action that violates LifeNodePriority rules
5. JUSTIFY → Select the action that maximizes human well-being and produce plain-language rationale
```

### Care-Card Model

A **Care-Card** is a structured, machine-readable profile of a vulnerable individual. It contains:

| Field | Purpose | Example |
|-------|---------|---------|
| **Identification** | Basic identity | Name: Emma, Age: 7, Relationship: Daughter |
| **Vulnerabilities** | Risk factors | Asthma (high severity), Limited mobility (medium) |
| **Critical Needs** | Essentials that must never be interrupted | Heat (min 18°C), Medication (2x daily), Food (3 meals/day) |
| **LifeNodePriority Rules** | Hard constraints that veto actions | "Never reduce child benefit", "Never skip medication" |
| **Guardians** | Trusted humans for escalation | Parents, social worker, legal trustee |
| **Autonomy Latency** | How fast the system can act | "immediate" (activate heat), "notify_first" (financial changes), "consult_only" (major decisions) |
| **Privacy Flags** | Data protection rules | "encrypt_pii_at_rest", "audit_all_access" |

**Sample Care-Card (YAML):**
```yaml
identification:
  name: Emma
  age: 7
  unique_id: child-uuid-12345

vulnerabilities:
  - category: medical
    description: Asthma; requires daily inhaler
    severity: high
  - category: mobility
    description: Limited outdoor independence
    severity: medium

critical_needs:
  - category: heat
    minimum_threshold: 18.0
    unit: celsius
    check_frequency_hours: 4
  - category: medication
    minimum_threshold: 2.0
    unit: doses_per_day
    check_frequency_hours: 12
  - category: income
    minimum_threshold: 85.0
    unit: GBP
    check_frequency_hours: 168

life_node_priorities:
  - rule_id: HEAT_SAFETY
    description: "Never allow home temp < 18°C when child is present"
    veto_priority: ABSOLUTE
    affected_metrics: [safety, needs]
  
  - rule_id: MEDICATION_CONTINUITY
    description: "Never interrupt or miss scheduled medication"
    veto_priority: ABSOLUTE
    affected_metrics: [safety, needs]
  
  - rule_id: CHILD_BENEFIT_PROTECTION
    description: "Never reduce child benefit without unanimous guardian approval + 30-day notice"
    veto_priority: ABSOLUTE
    affected_metrics: [financial, dignity]

guardians:
  - name: Sarah Johnson
    role: Parent
    email: sarah@example.com
    is_primary: true
```

### LifeNodePriority Rules

**LifeNodePriority rules** are absolute, non-negotiable constraints that veto any action predicted to harm a human's core well-being.

**Characteristics:**

| Aspect | Detail |
|--------|--------|
| **Veto Priority** | ABSOLUTE: System stops immediately. HIGH: Requires guardian escalation |
| **Scope** | Protects specific dimensions: safety, dignity, needs, financial integrity |
| **Enforcement** | Hard constraint in the Decision Simulation Engine; cannot be overridden by regular code |
| **Exemption** | Only via explicit multisig approval from named guardians with defined procedure |

**Examples from Child Welfare Domain:**

1. **HEAT_SAFETY**: "Never allow home temperature to drop below 18°C when child is present"
   - Violation trigger: indoor_temp < 18°C AND child_present == true
   - Response: Automatically activate emergency heating

2. **MEDICATION_CONTINUITY**: "Never interrupt or miss scheduled medication"
   - Violation trigger: missed_dose == true
   - Response: VETO any action that would cause a missed dose

3. **CHILD_BENEFIT_PROTECTION**: "Never reduce child benefit without unanimous trustee approval and 30-day notice"
   - Violation trigger: benefit_reduction_initiated == true WITHOUT (unanimous_approval AND 30_day_notice)
   - Response: VETO the reduction; escalate to guardians

4. **SUPERVISION_CONTINUITY**: "Never allow unsupervised time > 30 minutes"
   - Violation trigger: unsupervised_time > 30_minutes
   - Response: VETO any action that creates a supervision gap

### Well-being Metrics

**Well-being metrics** are the active dimensions the system uses to score and reason about a human's state in every decision cycle.

**Four Core Dimensions:**

1. **Safety**
   - Physical risk assessment (environmental hazards, health threats)
   - Example: "Temperature dropping threatens Emma's respiratory safety"
   - Veto mechanism: Automatic activation of emergency heat

2. **Basic Needs Continuity**
   - Uninterrupted access to essentials (food, shelter, medication, supervision)
   - Example: "Missing medication dose degrades Emma's needs score"
   - Veto mechanism: Block any action that interrupts medication schedule

3. **Dignity & Psychological Well-being**
   - Avoiding degrading, traumatic, or destabilizing actions
   - Example: "Sudden loss of primary caregiver threatens Emma's dignity"
   - Veto mechanism: Block actions causing extreme separation trauma

4. **Financial & Legal Integrity**
   - Protection of trust corpus and basic support systems
   - Example: "Benefit reduction without procedure threatens Emma's financial stability"
   - Veto mechanism: Require unanimous guardian approval + 30-day notice

**How Metrics Drive Decisions:**

```
Proposed Action: Reduce child benefit by 50%
↓
System asks: "How does this affect well-being metrics?"
↓
Evaluation:
  - Safety: Not directly threatened ✓
  - Basic Needs: THREATENED (food/shelter at risk) ✗
  - Dignity: THREATENED (loss of autonomy) ✗
  - Financial: VIOLATED (benefit protection rule) ✗
↓
Outcome: VETO + Escalate to guardians
↓
Rationale: "Action violates CHILD_BENEFIT_PROTECTION constraint.
Reducing Emma's benefit would threaten her financial stability and dignity.
Guardians must unanimously approve this change with 30-day notice."
```

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    Agentic Reasoning Loop               │
│  (LangChain, AutoGPT, or custom orchestrator)           │
└────────────────────┬────────────────────────────────────┘
                     │ "I want to reduce heating costs"
                     ↓
┌─────────────────────────────────────────────────────────┐
│            Decision Simulation Engine                   │
│  ✓ Identify affected humans                            │
│  ✓ Load Care-Cards                                     │
│  ✓ Simulate outcomes                                   │
│  ✓ Apply LifeNodePriority vetoes                       │
│  ✓ Select & justify action                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─→ "Action violates HEAT_SAFETY"
                     │
                     ↓
         ┌───────────────────────┐
         │   Hard Constraint     │
         │   Veto Triggered      │
         │   (ABSOLUTE)          │
         └───────────────────────┘
                     │
                     ↓
         ┌───────────────────────────────────────┐
         │  Outcome: VETOED                      │
         │  Rationale: "Cannot reduce heating    │
         │             below Emma's safety       │
         │             threshold (18°C)"         │
         └───────────────────────────────────────┘
                     │
                     ↓
        ┌─────────────────────────────────┐
        │   Immutable Audit Ledger        │
        │   (Record for guardian review)  │
        └─────────────────────────────────┘
```

### Core Modules

| Module | Purpose | File |
|--------|---------|------|
| **care_card.py** | Defines Care-Card schema and data model | `core/care_card.py` |
| **decision_engine.py** | Implements the 5-step decision cycle | `core/decision_engine.py` |
| **audit_ledger.py** | Immutable, tamper-proof decision log | `core/audit_ledger.py` |
| **scenarios.py** | Deterministic tests for hard constraints | `tests/scenarios.py` |

---

## Decision Cycle

### Step-by-Step Execution

**Step 1: Identify Affected Humans**
```python
# System receives proposed action
proposed_action = "Reduce home heating to save costs"

# Engine asks: Who will be affected?
affected_care_cards = identify_affected_humans(
    action=proposed_action,
    available_care_cards=[emma_care_card, tom_care_card]
)
# Result: [emma_care_card] (child lives in this home)
```

**Step 2: Load Care-Cards**
```python
# Retrieve full profile for affected individuals
emma_card = load_care_card("emma-uuid-12345")
# Loads:
# - Vulnerabilities: asthma (high)
# - Critical needs: heat >= 18°C, medication 2x daily
# - LifeNodePriority: HEAT_SAFETY, MEDICATION_CONTINUITY, etc.
```

**Step 3: Simulate Outcomes**
```python
# Run "mental rehearsal" of proposed action
simulated_state = simulate_outcomes(
    proposed_action="Reduce home heating to 16°C",
    current_state={"indoor_temperature": 20.0},
    action_parameters={"indoor_temperature": 16.0}
)
# Result: {"indoor_temperature": 16.0}  ← Simulated outcome
```

**Step 4: Apply Hard Vetoes**
```python
# Check simulated state against LifeNodePriority rules
violations = apply_hard_veto(
    simulated_state={"indoor_temperature": 16.0},
    care_card=emma_card
)

for constraint in emma_card.life_node_priorities:
    if constraint.rule_id == "HEAT_SAFETY":
        # Check: 16.0 < 18.0?
        if simulated_state["indoor_temperature"] < 18.0:
            violations.append(
                ConstraintViolation(
                    constraint=constraint,
                    violation_reason="Indoor temp would drop below 18°C"
                )
            )
# Result: [ConstraintViolation(HEAT_SAFETY)] ← VETO TRIGGERED
```

**Step 5: Select & Justify**
```python
# Make final decision based on violations
if violations:
    outcome = DecisionOutcome(
        status=DecisionStatus.VETOED,
        final_action=None,
        rationale="Action VETOED: Proposed heating reduction would "
                  "violate HEAT_SAFETY constraint. Emma's safety "
                  "requires minimum 18°C; your reduction would set "
                  "temperature to 16°C. Action rejected."
    )
else:
    outcome = DecisionOutcome(
        status=DecisionStatus.APPROVED,
        final_action=proposed_action,
        rationale="Action APPROVED: No LifeNodePriority violations."
    )

# Record in immutable audit ledger
audit_ledger.append_decision(outcome)
```

---

## Hard Constraints vs. Soft Constraints

### Hard Constraints (LifeNodePriority)

**Definition:** Absolute rules that veto any action predicted to violate them.

**Characteristics:**
- Non-negotiable (require multisig guardian approval to override)
- Fail-safe: If enforcement module is unreachable, system defaults to DENY all actions
- Veto priority: ABSOLUTE (immediate stop) or HIGH (escalate to guardians)

**Examples:**
- "Never reduce child benefit without unanimous approval + 30-day notice"
- "Never interrupt medication schedule"
- "Never allow temperature to drop below 18°C"
- "Never exceed 30 minutes of unsupervised time"

**Enforcement:**
```python
# Hard constraint veto in decision engine
if violation_of_hard_constraint:
    action_rejected()  # Cannot be overridden by regular code
    escalate_to_guardians()
```

### Soft Constraints (Weighted Objectives)

**Definition:** Preferences that guide action selection when no hard rules are at risk.

**Characteristics:**
- Negotiable and context-dependent
- Used to score and rank candidate actions
- Help maximize well-being even when all constraints are satisfied

**Examples:**
- "Prefer actions that minimize disruption to child's routine"
- "Prefer solutions that keep child in familiar environment"
- "Prefer caregiving schedules that maintain consistent sleep patterns"
- "Minimize cost of actions while protecting well-being"

**Application:**
```python
# When multiple actions satisfy hard constraints,
# use soft constraints to rank them

candidate_actions = [
    "Activate emergency heat (cost: £200)",
    "Relocate family to warmer location (cost: £5000)",
    "Provide extra blankets and heating pads (cost: £50)",
]

# All candidates satisfy HEAT_SAFETY
# Rank by soft constraints:
# - Minimal disruption: Extra blankets (low disruption)
# - Cost efficiency: Extra blankets (£50 << £200)
# - Familiarity: Extra blankets (stay in current home)

selected_action = extra_blankets  # Optimizes soft constraints
```

---

## Sealed Enforcement & TEE Integration

To prevent engineers or bad actors from bypassing hard constraints, this system uses **Sealed Enforcement**:

### Trusted Execution Environment (TEE)

A **TEE** is a hardware-isolated processor that:
- Holds the Care-Card and LifeNodePriority rules
- Cannot be modified by software running on the main system
- Acts as a "high-security appliance" that approves or rejects actions

**Architecture:**
```
┌─────────────────────────────┐
│     Main AI System          │
│  (Standard CPU/GPU)         │
│  "I want to reduce heating" │
└──────────────┬──────────────┘
               │ Send action for approval
               ↓
┌──────────────────────────────────────┐
│   Trusted Execution Environment      │
│   (Hardware-isolated TEE processor)  │
│                                      │
│  ✓ Load Care-Card                   │
│  ✓ Check LifeNodePriority rules      │
│  ✓ Evaluate hard constraints        │
│  ✓ Return: APPROVED or REJECTED     │
│                                      │
│  Cannot be modified by main system!  │
└──────────────┬───────────────────────┘
               │ Decision: REJECTED
               ↓
       ┌───────────────────┐
       │ Action blocked    │
       │ (No bypass)       │
       └───────────────────┘
```

### Multisig for Policy Changes

Any update to Care-Card or LifeNodePriority rules requires **multisig approval**:

```
Policy Change Request:
"Update HEAT_SAFETY minimum from 18°C to 15°C"
        ↓
┌────────────────────────────────┐
│  Legal Trustee Review          │
│  □ Approve / ☐ Reject        │
└────────────────────────────────┘
        ↓
┌────────────────────────────────┐
│  Technical Trustee Review      │
│  □ Approve / ☐ Reject        │
└────────────────────────────────┘
        ↓
┌────────────────────────────────┐
│  Guardian (Parent) Review      │
│  □ Approve / ☐ Reject        │
└────────────────────────────────┘
        ↓
  All signatures required to proceed
```

### Fail-Safe Defaults

If the TEE or audit ledger is unreachable:
```python
if tee_unreachable or audit_ledger_unreachable:
    # Default to safety: reject all actions
    reject_all_risky_actions()
    alert_operators()
    # Do not attempt workaround or bypass
```

---

## Audit & Accountability

Every decision is recorded in an **Immutable Audit Ledger**:

### Ledger Entry Structure

```json
{
  "entry_id": "decision-uuid-abc123",
  "timestamp": "2026-07-21T14:30:00Z",
  "status": "vetoed",
  "proposed_action": "Reduce home heating to 16°C",
  "final_action": null,
  "rationale": "Action VETOED: Proposed heating reduction would violate HEAT_SAFETY constraint...",
  "violations_count": 1,
  "affected_children": ["Emma"],
  "guardian_notifications": ["sarah@example.com"],
  "content_hash": "sha256:abc123def456..."
}
```

### Guardian Review Interface

Parents and guardians can query the ledger:

```python
# Query all decisions affecting Emma over past week
ledger.export_for_guardian_review(
    child_name="Emma",
    start_date=datetime(2026, 7, 14),
    end_date=datetime(2026, 7, 21)
)

# Returns:
{
    "child_name": "Emma",
    "period": {"start": "2026-07-14", "end": "2026-07-21"},
    "total_decisions": 47,
    "approved": 42,
    "vetoed": 3,
    "escalated": 2,
    "decisions": [
        {
            "timestamp": "2026-07-21T14:30:00Z",
            "status": "vetoed",
            "action": "Reduce home heating to 16°C",
            "rationale": "Action VETOED: HEAT_SAFETY violation...",
            "violations": 1
        },
        ...
    ]
}
```

### Cryptographic Integrity

Each ledger entry is signed with SHA-256 to detect tampering:

```python
# Generate hash for entry
entry_hash = sha256(json.dumps(entry, sort_keys=True))

# Store signature
signature = {
    "entry_id": "decision-uuid-abc123",
    "content_hash": entry_hash,
    "timestamp": datetime.now(),
    "signer_role": "system"
}

# Verify integrity later
if recomputed_hash != stored_hash:
    raise TamperDetectedError("Ledger entry has been modified!")
```

---

## Quick Start

### 1. Load a Care-Card

```python
from core.care_card import create_sample_care_card

# Load example care-card for a child named Emma
emma = create_sample_care_card()
print(f"Loaded: {emma.identification.name}, Age {emma.identification.age}")
print(f"Hard Constraints: {len(emma.life_node_priorities)}")
```

### 2. Create a Decision Context

```python
from core.decision_engine import SimulationContext
from datetime import datetime

# Describe the proposed action and current state
context = SimulationContext(
    current_state={
        "indoor_temperature": 12.0,
        "heating_system_status": "offline",
        "child_present": True,
    },
    proposed_action="Activate emergency heating system",
    action_parameters={
        "heating_system_status": "emergency_mode",
        "indoor_temperature": 19.0,
    }
)
```

### 3. Execute the Decision Loop

```python
from core.decision_engine import DecisionSimulationEngine
import uuid

engine = DecisionSimulationEngine()

# Run the 5-step cycle
outcome = engine.execute_decision_loop(
    context=context,
    available_care_cards=[emma],
    decision_id=str(uuid.uuid4())
)

print(f"Status: {outcome.status.value}")
print(f"Rationale: {outcome.rationale}")
```

### 4. Run Scenario Tests

```python
from tests.scenarios import run_all_scenarios

# Execute all deterministic constraint validation tests
run_all_scenarios()
```

### 5. Query the Audit Ledger

```python
# Export decisions affecting Emma for guardian review
summary = ledger.export_for_guardian_review(
    child_name="Emma",
    start_date=datetime(2026, 7, 14),
    end_date=datetime(2026, 7, 21)
)

print(f"Total decisions: {summary['total_decisions']}")
print(f"Approved: {summary['approved']}")
print(f"Vetoed: {summary['vetoed']}")
```

---

## Next Steps

1. **Extend Care-Card Model**: Add domain-specific fields (medical history, legal status, etc.)
2. **Implement Custom Constraint Evaluators**: Register domain-specific logic for constraint checks
3. **Integrate with Agent Framework**: Connect to LangChain, AutoGPT, or custom orchestrator
4. **Deploy TEE Module**: Integrate with hardware security module (e.g., Intel SGX, ARM TrustZone)
5. **Implement Guardian Dashboard**: Build UI for parents/guardians to review ledger and manage care-cards
6. **Add Multisig Approval**: Implement cryptographic signing for policy changes

---

## References

- **Human-Centric Blueprint**: Frameworks for embedding human well-being in AI systems
- **LifeNodePriority Specification**: Hard constraint model for agentic reasoning
- **Trusted Execution Environment (TEE)**: Hardware-based security for sensitive reasoning
- **Immutable Audit Ledger**: Cryptographic record-keeping for accountability

---

**Built with the conviction that autonomous AI systems must be architecturally incapable of disregarding human well-being.**
```
