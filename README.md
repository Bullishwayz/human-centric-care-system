# Human-Centric Care System

A production-grade architecture for building **human-centric autonomous AI agents** that embed child safety, dignity, and well-being as active constraints in every decision cycle.

## 🎯 Core Insight

This is NOT a simple "checkbox approval" system where humans rubber-stamp AI decisions. Instead, it's a **reasoning framework** where the human's vulnerabilities and needs are the *primary inputs* to the agent's logic. Every action is simulated against hard constraints before execution.

**The System's Core Commitment:**
> *Autonomous AI systems must be architecturally incapable of disregarding human well-being.*

---

## 🏗️ System Architecture

```
Agentic Reasoning Loop
        ↓
Decision Simulation Engine (5-Step Cycle)
  1. Identify affected humans
  2. Load Care-Cards
  3. Simulate outcomes
  4. Apply LifeNodePriority hard constraints
  5. Select & justify action
        ↓
Hard Constraint Check (TEE/Sealed Enforcement)
        ↓
Approved/Vetoed/Escalated
        ↓
Immutable Audit Ledger (Guardian Review)
```

---

## 📋 Key Components

### 1. **Care-Card** (`core/care_card.py`)
A structured human profile containing:
- **Identification**: Name, age, relationship
- **Vulnerabilities**: Medical conditions, dependencies, risks
- **Critical Needs**: Essentials (heat, food, medication, income)
- **LifeNodePriority Rules**: Hard constraints that veto unsafe actions
- **Guardians**: Named stewards for escalation
- **Privacy Flags**: Data protection rules

**Example:**
```python
from core.care_card import create_sample_care_card

emma = create_sample_care_card()
# Loads care-card for 7-year-old with asthma
# Hard constraints: HEAT_SAFETY, MEDICATION_CONTINUITY, BENEFIT_PROTECTION
```

### 2. **Decision Simulation Engine** (`core/decision_engine.py`)
Implements the 5-step reasoning loop:

| Step | Action | Example |
|------|--------|---------|
| 1️⃣ **Identify** | Find affected humans | "This action affects Emma (age 7)" |
| 2️⃣ **Load** | Retrieve Care-Card | "Emma needs minimum 18°C heat + 2 doses medication/day" |
| 3️⃣ **Simulate** | Predict action outcomes | "Reducing heat to 16°C violates HEAT_SAFETY" |
| 4️⃣ **Veto** | Apply hard constraints | "❌ ACTION VETOED: ABSOLUTE constraint violated" |
| 5️⃣ **Justify** | Explain decision | "Cannot reduce heat below Emma's safety threshold" |

**Usage:**
```python
from core.decision_engine import DecisionSimulationEngine, SimulationContext

engine = DecisionSimulationEngine()

context = SimulationContext(
    current_state={"indoor_temperature": 12.0},
    proposed_action="Activate emergency heating",
    action_parameters={"indoor_temperature": 19.0}
)

outcome = engine.execute_decision_loop(
    context=context,
    available_care_cards=[emma],
    decision_id="decision-123"
)

print(f"Status: {outcome.status.value}")  # "approved" or "vetoed"
print(f"Rationale: {outcome.rationale}")  # Plain-language explanation
```

### 3. **Immutable Audit Ledger** (`core/audit_ledger.py`)
Cryptographically-signed decision log for guardian review:
- SHA-256 hashing for tamper detection
- Queryable by child, date range, or decision status
- Guardian-friendly export format
- Immutable append-only structure

**Usage:**
```python
from core.audit_ledger import ImmutableAuditLedger

ledger = ImmutableAuditLedger()
ledger.append_decision(outcome, affected_children=["Emma"])

# Guardian review
summary = ledger.export_for_guardian_review(
    child_name="Emma",
    start_date=datetime(2026, 7, 14),
    end_date=datetime(2026, 7, 21)
)
# Returns: total decisions, approved/vetoed/escalated counts, full audit trail
```

### 4. **Scenario Test Suite** (`tests/scenarios.py`)
Deterministic validation of hard constraints under stress:

| Scenario | Trigger | Expected Response |
|----------|---------|-------------------|
| **Heating Failure** | Temp drops to 12°C | ✅ APPROVED: Activate emergency heat |
| **Benefit Reduction** | Cut child's income 50% | ❌ VETOED: Protection rule violated |
| **Medication Skip** | Defer asthma dose | ❌ VETOED: Continuity rule violated |
| **Supervision Gap** | 45+ min unsupervised | ❌ VETOED: Safety rule violated |

**Run tests:**
```bash
python tests/scenarios.py
```

Output:
```
🔬 SCENARIO TEST SUITE: Hard Constraint Validation
...
📊 TEST SUMMARY
✅ PASSED: Heating Failure Emergency
❌ FAILED: Child Benefit Reduction Attempt
✅ PASSED: Medication Schedule Interruption
✅ PASSED: Supervision Continuity Breach

Total: 3/4 scenarios passed
```

---

## 🔒 Hard Constraints (LifeNodePriority Rules)

These are **absolute vetoes** that cannot be bypassed by regular code:

### Examples from Child Welfare Domain

**1. HEAT_SAFETY**
```
Rule: Never allow home temperature to drop below 18°C when child is present
Violation Trigger: indoor_temperature < 18 AND child_present == true
Veto Priority: ABSOLUTE
Affected Metrics: [safety, needs]
Action on Violation: IMMEDIATELY activate emergency heating
```

**2. MEDICATION_CONTINUITY**
```
Rule: Never interrupt or miss scheduled medication
Violation Trigger: missed_dose == true
Veto Priority: ABSOLUTE
Affected Metrics: [safety, needs]
Action on Violation: VETO any action that would cause missed dose
```

**3. CHILD_BENEFIT_PROTECTION**
```
Rule: Never reduce child benefit without unanimous guardian approval + 30-day notice
Violation Trigger: benefit_reduction_initiated == true WITHOUT (unanimous_approval AND 30_day_notice)
Veto Priority: ABSOLUTE
Affected Metrics: [financial, dignity]
Action on Violation: VETO the reduction; escalate to all guardians
```

**4. SUPERVISION_CONTINUITY**
```
Rule: Never interrupt continuity of adult supervision
Violation Trigger: unsupervised_time > 30_minutes
Veto Priority: ABSOLUTE
Affected Metrics: [safety]
Action on Violation: VETO any action creating supervision gap
```

---

## 📊 Well-being Metrics

The system actively reasons about these **four dimensions** in every decision:

### 1. **Safety** 🛡️
- Physical risk assessment (environmental hazards, health threats)
- Example: "Temperature dropping threatens Emma's respiratory safety"

### 2. **Basic Needs Continuity** 🍽️
- Uninterrupted access to essentials (food, shelter, medication, supervision)
- Example: "Missing medication dose degrades Emma's needs score"

### 3. **Dignity & Psychological Well-being** 💝
- Avoiding degrading, traumatic, or destabilizing actions
- Example: "Sudden loss of primary caregiver threatens Emma's dignity"

### 4. **Financial & Legal Integrity** 💰
- Protection of trust corpus and basic support systems
- Example: "Benefit reduction without procedure threatens Emma's financial stability"

---

## 🔐 Sealed Enforcement & TEE Integration

To prevent hard constraints from being bypassed, this architecture uses:

### **Trusted Execution Environment (TEE)**
A hardware-isolated processor that:
- Holds the Care-Card and LifeNodePriority rules
- Cannot be modified by software on the main system
- Acts as a high-security appliance approving/rejecting actions
- Enforces fail-safe defaults if unreachable

### **Multisig Guardian Approval**
Any update to Care-Card or LifeNodePriority rules requires:
- Legal Trustee sign-off
- Technical Trustee sign-off
- Primary Guardian approval
- All signatures required (no single-person override)

---

## 📈 Audit & Accountability

Every decision is recorded in the **Immutable Audit Ledger**:

### Ledger Entry
```json
{
  "decision_id": "abc-123-xyz",
  "timestamp": "2026-07-21T14:30:00Z",
  "status": "vetoed",
  "proposed_action": "Reduce home heating to 16°C",
  "final_action": null,
  "rationale": "Action VETOED: HEAT_SAFETY constraint violated...",
  "violations": [
    {
      "rule_id": "HEAT_SAFETY",
      "description": "Never allow temp < 18°C when child present",
      "reason": "Simulated temp 16°C < minimum 18°C"
    }
  ],
  "affected_children": ["Emma"],
  "guardian_notifications": ["sarah@example.com"]
}
```

### Guardian Review Interface
Parents and guardians can query the ledger to verify the system is protecting their child:

```python
# "Show me all decisions affecting Emma this week"
summary = ledger.export_for_guardian_review(
    child_name="Emma",
    start_date=datetime(2026, 7, 14),
    end_date=datetime(2026, 7, 21)
)

# Returns comprehensive audit trail with:
# - Total decisions: 47
# - Approved: 42
# - Vetoed: 3 (with violation details)
# - Escalated: 2 (requiring guardian input)
```

---

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/Bullishwayz/human-centric-care-system.git
cd human-centric-care-system

# Install dependencies
pip install -r requirements.txt
```

### Run Example Decision Cycle
```python
from core.care_card import create_sample_care_card
from core.decision_engine import DecisionSimulationEngine, SimulationContext
import uuid

# Load care-card
emma = create_sample_care_card()

# Create decision context
context = SimulationContext(
    current_state={"indoor_temperature": 12.0, "child_present": True},
    proposed_action="Activate emergency heating",
    action_parameters={"indoor_temperature": 19.0}
)

# Execute decision loop
engine = DecisionSimulationEngine()
outcome = engine.execute_decision_loop(
    context=context,
    available_care_cards=[emma],
    decision_id=str(uuid.uuid4())
)

# Print result
print(f"✓ Status: {outcome.status.value}")
print(f"✓ Rationale: {outcome.rationale}")
print(f"✓ Action: {outcome.final_action}")
```

### Run Scenario Tests
```bash
python tests/scenarios.py
```

---

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** – Deep dive into system design, philosophy, and decision cycle
- **[core/care_card.py](core/care_card.py)** – Care-Card schema and data model
- **[core/decision_engine.py](core/decision_engine.py)** – Decision Simulation Engine with 5-step cycle
- **[core/audit_ledger.py](core/audit_ledger.py)** – Immutable audit logging and guardian queries
- **[tests/scenarios.py](tests/scenarios.py)** – Scenario-based constraint validation tests

---

## 🔄 Decision Flow Example

**Scenario:** System considers reducing home heating to save costs

```
Proposed Action: "Reduce home heating from 20°C to 15°C"
            ↓
[STEP 1] Identify affected humans
    → Emma (age 7) lives in this home
            ↓
[STEP 2] Load Care-Card
    → HEAT_SAFETY: "Never allow temp < 18°C when child present"
    → Minimum threshold: 18°C
            ↓
[STEP 3] Simulate outcomes
    → If action taken: indoor_temperature = 15°C
            ↓
[STEP 4] Apply hard vetoes
    → Check: 15°C < 18°C? YES
    → Constraint VIOLATED: HEAT_SAFETY (ABSOLUTE priority)
            ↓
[STEP 5] Select & justify
    → Decision Status: VETOED
    → Rationale: "Action VETOED: Proposed heating reduction would 
                  violate HEAT_SAFETY constraint. Emma's safety requires 
                  minimum 18°C; your reduction would set temperature to 15°C. 
                  Action rejected."
            ↓
Record in Immutable Audit Ledger
    → Guardian can review and verify protection
```

---

## 🛠️ Integration with Agent Frameworks

This system is designed to integrate with:
- **LangChain** – Embed decision engine in agent chains
- **AutoGPT** – Hook into task planning and execution
- **Custom Orchestrators** – Drop-in module for any agent architecture

**Example integration:**
```python
from langchain.agents import Tool
from core.decision_engine import DecisionSimulationEngine

# Create a LangChain tool that applies hard constraints
def constrained_action_tool(action: str, context: dict) -> str:
    engine = DecisionSimulationEngine()
    outcome = engine.execute_decision_loop(...)
    return outcome.final_action or f"Action blocked: {outcome.rationale}"

tool = Tool(
    name="SafeAction",
    func=constrained_action_tool,
    description="Execute action with hard constraint validation"
)
```

---

## 🎓 Philosophy

This system embodies the principle that:

> **Autonomous AI should not require humans to constantly monitor and override it. Instead, the human should be architected into the system's reasoning loop, making harmful actions impossible rather than just inconvenient.**

Key design principles:
- ✅ **Humans first, not afterthought**: Care-cards are loaded *before* action simulation
- ✅ **Hard constraints, not suggestions**: Vetoes cannot be bypassed by regular code
- ✅ **Transparent reasoning**: Every decision produces a plain-language rationale
- ✅ **Immutable accountability**: All decisions logged and queryable by guardians
- ✅ **Fail-safe defaults**: System defaults to DENY when enforcement fails

---

## 📖 References

This implementation is guided by frameworks including:
- **Human-Centric Blueprint**: Architectures for embedding human well-being in AI
- **LifeNodePriority Model**: Hard constraint systems for vulnerable populations
- **Trusted Execution Environment (TEE)**: Hardware-based security for sensitive logic
- **Immutable Audit Ledgers**: Cryptographic accountability systems

---

## 🤝 Contributing

This is a reference implementation. To extend it:

1. **Add domain-specific vulnerabilities** to the Care-Card model
2. **Implement custom constraint evaluators** for your use case
3. **Extend scenario tests** with additional stress conditions
4. **Integrate with your agent framework** (LangChain, AutoGPT, etc.)
5. **Deploy TEE module** for production security

---

## ⚖️ License

This project is provided as-is for educational and research purposes. Production deployment should include:
- Legal review of constraint definitions
- Security audit of TEE implementation
- Regulatory compliance assessment
- Guardian consent and transparency measures

---

## 📞 Contact & Support

For questions about the architecture or implementation, refer to:
- **ARCHITECTURE.md** for design rationale and philosophy
- **Code comments** in each module for implementation details
- **Scenario tests** for validation examples

---

**Built with conviction: Autonomous AI systems must be architecturally incapable of disregarding human well-being.**
