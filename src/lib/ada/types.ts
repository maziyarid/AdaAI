export type AdaScope = {
  scope_type: string;
  scope_id: string;
  version: number;
};

export type AdaMemory = {
  id: string;
  canonical_key: string;
  record_type: string;
  scope_type: string;
  scope_id: string;
  priority: number;
  authority: string;
  provenance: string;
  privacy_class: string;
  title: string;
  content: string;
  summary: string | null;
  checksum: string;
};

export type AdaState = {
  project_id: string;
  lane: string;
  objective: string | null;
  verified_status: string | null;
  completed_work: string[];
  active_decisions: string[];
  blockers: string[];
  next_action: string | null;
  active_artifacts: string[];
  pending_qa: string[];
  state_version: number;
  updated_by: string;
};

export type AdaPassport = {
  id: string;
  agent_id: string;
  task_type: string;
  allowed_sites: string[];
  allowed_tools: string[];
  allowed_mutation_types: string[];
  max_batch_size: number;
  approval_classes: string[];
  version: number;
};

export type AdaTool = {
  tool_name: string;
  side_effect_class: string;
  mutation_type: string | null;
  requires_receipt: boolean;
  requires_snapshot: boolean;
  default_decision: string;
  enabled: boolean;
};

export type AdaReceipt = {
  receipt_id: string;
  context_hash: string;
  expires_at: string;
  dependencies: AdaScope[];
  mandatory_memory: AdaMemory[];
  project_state: AdaState | null;
  qalam_release: string | null;
  passport: AdaPassport | null;
  preview_hmac: boolean;
};
