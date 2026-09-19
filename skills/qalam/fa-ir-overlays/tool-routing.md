# Qalam tool-routing contract

This file exists so agents do not ask the user to manually @mention a pile of tools.

The user invokes **Qalam** once. Qalam routes internally.

## Pipeline

`context → evidence → domain → action → verification → durable write-back`

### 1. Context / memory

For substantial project-bound writing/editorial work:

- **XMemo**: primary structured memory for canonical decisions, project policy, working state, TODOs and resumable handoffs.
- **Engram**: secondary verbatim/semantic history when exact prior wording, conversations, provenance or older context may matter.

Do not treat memory as live approval. Current user instruction and current artefacts win.

### 2. Evidence / currentness

- **Acumen**: preflight only when recency can change the answer; use to discover what might have changed.
- **Exa / web research**: external evidence, literature, competitor/public-source research.
- **Google Drive**: project documents, Art of Writing corpus, user-owned research sources.

Do not call all three for a timeless rewrite.

### 3. Domain tools

Load only when the task needs them:

- SEO/GSC → treg / SEO connector
- code/library/API docs → Context7
- repository → GitHub
- connected business data → Airbyte Agent Engine
- people/company intelligence → Sixtyfour only when the task is actually about people/companies
- WordPress/runtime → user's canonical WP/VPS MCP route
- medical personal data → Health only under its own policy

### 4. Builders

Hercules/Base44/Build Web Apps are **not** writing research dependencies. Use them only when the user asks to build/edit an app/site in those products.

### 5. Verification/evidence of execution

AgentProof is for explicit execution-receipt verification, not proof that prose is true or high quality.

### 6. Write-back

At a meaningful completed checkpoint:

- update the canonical XMemo memory rather than duplicating it;
- save concise durable context to Engram when it will help cross-agent continuity;
- do not store secrets;
- do not store every draft or every transient research result.

## Tool budget rule

One tool per role unless evidence shows a second source is necessary.

Never call tools merely because they were @mentioned. Route by task.
