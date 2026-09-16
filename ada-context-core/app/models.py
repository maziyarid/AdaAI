from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Optional
from uuid import UUID

class BootstrapRequest(BaseModel):
    agent_id: str
    task_type: str
    project_id: Optional[str] = None
    project_lane: str = 'main'
    site_id: Optional[str] = None
    task_run_id: Optional[UUID] = None

class MemoryUpsert(BaseModel):
    canonical_key: str
    record_type: str
    scope_type: str
    scope_id: str = '*'
    priority: int = Field(ge=0, le=5)
    authority: str
    provenance: str = 'CONFIRMED'
    privacy_class: str = 'LOCAL_ONLY'
    title: str
    content: str
    summary: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    created_by: str
    reason: str = 'update'
    status: str = 'ACTIVE'

class StateUpdate(BaseModel):
    project_id: str
    lane: str = 'main'
    objective: Optional[str] = None
    verified_status: Optional[str] = None
    completed_work: list[Any] = Field(default_factory=list)
    active_decisions: list[Any] = Field(default_factory=list)
    blockers: list[Any] = Field(default_factory=list)
    next_action: Optional[str] = None
    active_artifacts: list[Any] = Field(default_factory=list)
    pending_qa: list[Any] = Field(default_factory=list)
    updated_by: str

class TaskCreate(BaseModel):
    idempotency_key: str
    task_type: str
    agent_id: str
    requested_action: str
    project_id: Optional[str] = None
    site_id: Optional[str] = None
    parent_task_run_id: Optional[UUID] = None
    requested_payload: Optional[dict[str,Any]] = None
    state: str = 'QUEUED'

class AuthorizationRequest(BaseModel):
    agent_id: str
    task_type: str
    tool_name: str
    receipt_id: Optional[UUID] = None
    site_id: Optional[str] = None
    mutation_type: Optional[str] = None
    batch_size: int = 1
    payload: dict[str,Any] = Field(default_factory=dict)
    snapshot_hash: Optional[str] = None

class ApprovalRequest(BaseModel):
    task_run_id: UUID
    tool_name: str
    site_id: Optional[str] = None
    resource_id: Optional[str] = None
    payload: dict[str,Any]
    snapshot_hash: Optional[str] = None
    context_receipt_id: UUID
    requested_by: str
    ttl_seconds: int = Field(default=3600, ge=60, le=86400)

class ApprovalDecision(BaseModel):
    approver: str
    decision: str = Field(pattern='^(GRANT|DENY)$')

class ExternalInput(BaseModel):
    source_uri: Optional[str] = None
    source_kind: str
    content_text: str
    ingested_by: str

class JournalIntent(BaseModel):
    task_run_id: UUID
    idempotency_key: str
    tool_name: str
    site_id: Optional[str] = None
    resource_id: Optional[str] = None
    payload: dict[str,Any]
    snapshot_id: Optional[UUID] = None
    expected_postcondition: dict[str,Any] = Field(default_factory=dict)
