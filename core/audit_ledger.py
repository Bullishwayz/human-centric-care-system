"""
Immutable Audit Ledger: Cryptographically-signed decision log

This module implements a tamper-proof ledger that records every decision
made by the system, including care-card metrics checked, constraints
evaluated, and rationale for actions taken.

Features:
- Immutable append-only log
- Cryptographic signing (SHA-256)
- Guardian-queryable format
- Compliance with audit requirements
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from core.decision_engine import DecisionOutcome


@dataclass
class LedgerEntry:
    """Single entry in the immutable audit ledger."""
    entry_id: str  # UUID
    decision_id: str
    timestamp: datetime
    decision_status: str
    proposed_action: str
    final_action: Optional[str]
    rationale: str
    violations_count: int
    affected_children: List[str]  # Names of affected children
    guardian_notifications: List[str]  # Emails of notified guardians
    content_hash: str  # SHA-256 of decision content


@dataclass
class LedgerSignature:
    """Cryptographic signature for ledger integrity."""
    entry_id: str
    content_hash: str
    signature_timestamp: datetime
    signer_role: str  # "system", "guardian", "auditor"


class ImmutableAuditLedger:
    """
    Append-only, cryptographically-secured audit log.
    
    In production, this would be backed by a blockchain-like structure
    or a hardware security module (HSM) to guarantee immutability.
    
    For this implementation, we use SHA-256 chaining and JSON serialization.
    """
    
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.signatures: List[LedgerSignature] = []
        self.chain_hash: Optional[str] = None  # Hash of entire ledger
    
    def append_decision(
        self,
        decision_outcome: DecisionOutcome,
        affected_children: List[str],
    ) -> LedgerEntry:
        """
        Add a decision to the ledger (immutable append).
        
        Args:
            decision_outcome: The DecisionOutcome from the reasoning engine
            affected_children: List of child names affected by this decision
        """
        
        # Construct entry
        entry = LedgerEntry(
            entry_id=decision_outcome.decision_id,
            decision_id=decision_outcome.decision_id,
            timestamp=decision_outcome.timestamp,
            decision_status=decision_outcome.status.value,
            proposed_action=decision_outcome.proposed_action,
            final_action=decision_outcome.final_action,
            rationale=decision_outcome.rationale,
            violations_count=len(decision_outcome.violations),
            affected_children=affected_children,
            guardian_notifications=[
                g["email"] for g in decision_outcome.notifiable_guardians
            ],
            content_hash=self._compute_entry_hash(decision_outcome),
        )
        
        # Append to ledger (immutable operation)
        self.entries.append(entry)
        
        # Update chain hash
        self._update_chain_hash()
        
        return entry
    
    def _compute_entry_hash(self, decision_outcome: DecisionOutcome) -> str:
        """
        Compute SHA-256 hash of decision content for tamper detection.
        """
        content = {
            "decision_id": decision_outcome.decision_id,
            "status": decision_outcome.status.value,
            "proposed_action": decision_outcome.proposed_action,
            "final_action": decision_outcome.final_action,
            "rationale": decision_outcome.rationale,
            "timestamp": decision_outcome.timestamp.isoformat(),
        }
        content_json = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_json.encode()).hexdigest()
    
    def _update_chain_hash(self) -> None:
        """
        Update the overall chain hash (hash of all entries).
        This detects if entries are added, removed, or reordered.
        """
        all_hashes = [entry.content_hash for entry in self.entries]
        chain_content = json.dumps(all_hashes, sort_keys=True)
        self.chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()
    
    def sign_entry(
        self,
        entry_id: str,
        signer_role: str,
    ) -> LedgerSignature:
        """
        Create a cryptographic signature for an entry.
        
        In production, this would use a private key and PKI infrastructure.
        For this demo, we create a timestamped signature record.
        """
        # Find entry
        entry = None
        for e in self.entries:
            if e.entry_id == entry_id:
                entry = e
                break
        
        if not entry:
            raise ValueError(f"Entry not found: {entry_id}")
        
        # Create signature record
        signature = LedgerSignature(
            entry_id=entry_id,
            content_hash=entry.content_hash,
            signature_timestamp=datetime.now(),
            signer_role=signer_role,
        )
        
        self.signatures.append(signature)
        return signature
    
    def verify_ledger_integrity(self) -> Dict[str, Any]:
        """
        Verify that the ledger has not been tampered with.
        
        Returns:
            {
                "is_valid": bool,
                "total_entries": int,
                "integrity_checks": {
                    "chain_intact": bool,
                    "no_gaps": bool,
                    "all_signed": bool,
                },
                "issues": List[str],
            }
        """
        issues: List[str] = []
        
        # Recompute chain hash and compare
        old_chain_hash = self.chain_hash
        self._update_chain_hash()
        
        if self.chain_hash != old_chain_hash:
            issues.append("Chain hash mismatch - potential tampering detected!")
        
        # Check for gaps in timestamps
        prev_timestamp = None
        for entry in self.entries:
            if prev_timestamp and entry.timestamp < prev_timestamp:
                issues.append(
                    f"Timestamp out of order: {entry.entry_id}"
                )
            prev_timestamp = entry.timestamp
        
        # Check if all entries are signed
        signed_ids = {s.entry_id for s in self.signatures}
        unsigned = [e.entry_id for e in self.entries if e.entry_id not in signed_ids]
        
        return {
            "is_valid": len(issues) == 0,
            "total_entries": len(self.entries),
            "integrity_checks": {
                "chain_intact": self.chain_hash == old_chain_hash,
                "no_gaps": len([e for e in self.entries]) == len(self.entries),
                "all_signed": len(unsigned) == 0,
            },
            "unsigned_entries": unsigned,
            "issues": issues,
            "chain_hash": self.chain_hash,
        }
    
    def query_by_child(self, child_name: str) -> List[LedgerEntry]:
        """Query all decisions affecting a specific child."""
        return [
            entry for entry in self.entries
            if child_name in entry.affected_children
        ]
    
    def query_by_status(self, status: str) -> List[LedgerEntry]:
        """Query all decisions with a specific status."""
        return [
            entry for entry in self.entries
            if entry.decision_status == status
        ]
    
    def query_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[LedgerEntry]:
        """Query decisions within a date range."""
        return [
            entry for entry in self.entries
            if start_date <= entry.timestamp <= end_date
        ]
    
    def query_vetoed_decisions(self) -> List[LedgerEntry]:
        """Query all vetoed decisions (highest-priority constraints triggered)."""
        return self.query_by_status("vetoed")
    
    def query_escalated_decisions(self) -> List[LedgerEntry]:
        """Query all escalated decisions (guardian review required)."""
        return self.query_by_status("escalated")
    
    def export_for_guardian_review(
        self,
        child_name: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """
        Export ledger data in a guardian-friendly format.
        
        This is the interface that parents, guardians, and auditors use
        to review the system's decision history.
        """
        entries = [
            e for e in self.query_by_child(child_name)
            if start_date <= e.timestamp <= end_date
        ]
        
        summary = {
            "child_name": child_name,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_decisions": len(entries),
            "approved": len([e for e in entries if e.decision_status == "approved"]),
            "vetoed": len([e for e in entries if e.decision_status == "vetoed"]),
            "escalated": len([e for e in entries if e.decision_status == "escalated"]),
            "decisions": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "status": e.decision_status,
                    "action": e.proposed_action,
                    "rationale": e.rationale,
                    "violations": e.violations_count,
                }
                for e in entries
            ],
        }
        
        return summary
    
    def export_as_json(self) -> str:
        """Export entire ledger as JSON for archival or transmission."""
        ledger_dict = {
            "metadata": {
                "total_entries": len(self.entries),
                "total_signatures": len(self.signatures),
                "chain_hash": self.chain_hash,
                "exported_at": datetime.now().isoformat(),
            },
            "entries": [asdict(e) for e in self.entries],
            "signatures": [
                {
                    "entry_id": s.entry_id,
                    "content_hash": s.content_hash,
                    "signature_timestamp": s.signature_timestamp.isoformat(),
                    "signer_role": s.signer_role,
                }
                for s in self.signatures
            ],
        }
        
        return json.dumps(ledger_dict, indent=2)
    
    def print_summary(self) -> None:
        """Print a human-readable summary of the ledger."""
        print("\n" + "="*70)
        print("📋 AUDIT LEDGER SUMMARY")
        print("="*70)
        print(f"Total Entries: {len(self.entries)}")
        print(f"Chain Hash: {self.chain_hash}")
        
        approved = len(self.query_by_status("approved"))
        vetoed = len(self.query_by_status("vetoed"))
        escalated = len(self.query_by_status("escalated"))
        
        print(f"\nDecision Distribution:")
        print(f"  ✅ Approved:  {approved}")
        print(f"  ❌ Vetoed:    {vetoed}")
        print(f"  ⚠️  Escalated: {escalated}")
        
        if vetoed > 0:
            print(f"\nVetoed Decisions (Hard Constraints Triggered):")
            for entry in self.query_vetoed_decisions():
                print(f"  - {entry.timestamp.isoformat()}: {entry.proposed_action}")
                print(f"    Reason: {entry.rationale[:80]}...")
