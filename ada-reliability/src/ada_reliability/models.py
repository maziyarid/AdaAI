"""Data structures for Ada reliability engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from .crypto import sha256_obj, sha256_text, utcnow


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


class Provenance(str, Enum):
    PROPOSED = "PROPOSED"
    OBSERVED = "OBSERVED"
    CONFIRMED = "CONFIRMED"
    VERIFIED = "VERIFIED"
    CANONICAL = "CANONICAL"
    SUPERSEDED = "SUPERSEDED"


class Priority:
    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
    P5 = 5


ZWNJ = "\u200c"
TEZNEVISE_SITE = "teznevise.ir"
DEFAULT_RECEIPT_TTL_SECONDS = 900
DEFAULT_APPROVAL_TTL_SECONDS = 3600


@dataclass
class MemoryRecord:
    id: str
    canonical_key: str
    record_type: str
    scope_type: str
    scope_id: str
    priority: int
    authority: str
    provenance: str
    title: str
    content: str
    status: str = "ACTIVE"
    creator: str = "system"
    supersedes_id: Optional[str] = None
    superseded_by: Optional[str] = None
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            self.checksum = sha256_text(self.content)


@dataclass
class ScopeVersion:
    scope_type: str
    scope_id: str
    version: int = 1


@dataclass
class PolicyRelease:
    component: str
    release: str
    content_hash: str
    status: str = "ACTIVE"
    path: str = ""


@dataclass
class AgentPassport:
    id: str
    agent_id: str
    task_type: str = "*"
    allowed_sites: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    allowed_page_roles: list[str] = field(default_factory=lambda: ["*"])
    allowed_mutation_types: list[str] = field(default_factory=list)
    max_batch_size: int = 1
    max_retries: int = 3
    deletion_permission: bool = False
    policy_change_permission: bool = False
    approval_mandatory: bool = False
    approval_classes: list[str] = field(default_factory=list)
    enabled: bool = True
    version: int = 1


@dataclass
class ToolSpec:
    tool_name: str
    side_effect_class: str
    mutation_type: Optional[str] = None
    requires_receipt: bool = True
    requires_snapshot: bool = False
    requires_live_verification: bool = False
    default_decision: str = "DENY"
    enabled: bool = True


@dataclass
class ReceiptDependency:
    scope_type: str
    scope_id: str
    version: int
    release_label: Optional[str] = None


@dataclass
class ContextReceipt:
    id: str
    agent_id: str
    task_run_id: str
    project_id: str
    site_id: str
    task_type: str
    memory_ids: list[str]
    qalam_release: Optional[str]
    qalam_hash: Optional[str]
    passport_id: str
    context_hash: str
    payload_hash: str
    allowed_mutation_classes: list[str]
    dependencies: list[ReceiptDependency]
    signature_alg: str
    key_id: str
    signature: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or utcnow()
        if self.revoked_at is not None:
            return True
        return now >= self.expires_at


@dataclass
class ApprovalTicket:
    id: str
    task_run_id: str
    tool_name: str
    site_id: str
    resource_id: str
    payload_hash: str
    snapshot_hash: Optional[str]
    context_receipt_id: str
    dependency_hash: str
    state: str
    requested_by: str
    requester_identity: str
    approved_by: Optional[str] = None
    approver_identity: Optional[str] = None
    approval_id: Optional[str] = None
    one_time_token_hash: Optional[str] = None
    requested_at: datetime = field(default_factory=utcnow)
    decided_at: Optional[datetime] = None
    expires_at: datetime = field(default_factory=lambda: utcnow() + timedelta(seconds=DEFAULT_APPROVAL_TTL_SECONDS))
    consumed_at: Optional[datetime] = None


@dataclass
class MutationJournalEntry:
    id: str
    task_run_id: str
    idempotency_key: str
    tool_name: str
    site_id: str
    resource_id: str
    payload_hash: str
    snapshot_id: Optional[str]
    expected_postcondition: dict
    status: str
    authorize_decision: str
    receipt_id: str
    remote_ref: Optional[dict] = None
    last_error: Optional[str] = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)


@dataclass
class VerificationRecord:
    id: str
    site_id: str
    resource_id: str
    after_mutation_id: Optional[str]
    passed: bool
    stale: bool
    failures: list[str]
    live_hash: str
    verifier_identity: str = "verifier"
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class ExternalInput:
    id: str
    source_kind: str
    content_hash: str
    content_text: str
    trust_class: str = "UNTRUSTED_EXTERNAL"
    quarantine_status: str = "QUARANTINED"
    injection_flags: list[str] = field(default_factory=list)
    ingested_by: str = "system"


@dataclass
class LiveResource:
    site_id: str
    resource_id: str
    content: str
    meta: dict = field(default_factory=dict)
    version: int = 1

    @property
    def live_hash(self) -> str:
        return sha256_obj({"content": self.content, "meta": self.meta, "version": self.version})
