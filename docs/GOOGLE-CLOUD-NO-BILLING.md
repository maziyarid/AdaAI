# Google services we can use without billing information

Verified September 2026. This document is intentionally conservative: it lists services that can help Ada development without requiring us to attach a billing account/payment method, and separates them from products whose free quota still requires billing.

## Useful now

### Google Antigravity — individual free tier
- Current Antigravity pricing includes a **$0/month individual tier** with baseline weekly quota.
- The individual tier currently includes Gemini agent models, unlimited tab completions, unlimited command requests, Scheduled Tasks, and CLI access, subject to rate limits that Google may change.
- This is the most relevant replacement for the old individual Gemini Code Assist/Gemini CLI path.
- Useful for repository development, parallel coding agents, experiments, and possibly helping us accelerate Ada implementation from a personal Google account.
- Do not make Antigravity authoritative for Ada memory, policy, credentials, or production execution. It is a development client/agent, not the control plane.
- Do not try to reuse Antigravity account authentication through third-party agents; Google's documentation says third-party use of the Antigravity login is not supported. Use AI Studio/Vertex APIs for programmatic Gemini access instead.

### Cloud Shell
- Free for users with a Google Cloud account.
- Useful for temporary CLI work, `gcloud`, Git, quick tests, and reproducing deployment commands.
- Not a production host for Ada; sessions are ephemeral and resource-limited.

### BigQuery sandbox
- Works without a credit card or billing account.
- Useful for exploratory analytics, large public datasets, and occasional offline analysis of exported Ada/AdaEval events.
- Do **not** use it as Context Core's authoritative transactional database. Sandbox capabilities are limited and are not a substitute for PostgreSQL.

### Firebase Spark plan
- No payment information is needed.
- Includes no-cost products and no-cost quotas for several paid-tier Firebase products.
- Potentially useful later for a non-authoritative dashboard, Authentication experiments, App Check, Cloud Messaging, or lightweight analytics.
- Do not move authoritative memory, secrets, approval authority, or execution state away from the VPS just because a Firebase quota is free.
- Paid Google Cloud products such as Cloud Run are not available merely because a project is on Spark.

### Gemini Developer API / Google AI Studio free tier
- New accounts/projects can use a free tier for eligible models without attaching a Cloud Billing account/payment method.
- Useful as an **optional external AdaEval/fallback model**, not as Ada's memory or authority.
- Context Core privacy classes still apply: `LOCAL_ONLY` data must never be sent to external models; `LOCAL_PREFERRED` requires an explicit redacted context packet.
- Quotas/model availability can change, so the model registry must record current limits rather than assuming permanent free capacity.

### Google AI Studio Build starter tier
- Current Gemini API billing documentation describes a Google Cloud Starter Tier that can publish up to two full-stack applications without setting up a Google Cloud project or billing account.
- Useful for prototypes only. Ada production continues to live on our controlled infrastructure.

## Do not plan around these as no-billing services

### Gemini Code Assist for individuals / old consumer Gemini CLI access
The screenshot/older marketing path is outdated for individual use. Google stopped serving Gemini Code Assist IDE extensions and Gemini CLI for Gemini Code Assist for individuals and Google AI Pro/Ultra consumer accounts on June 18, 2026. Standard/Enterprise organizational subscriptions are separate.

Use **Antigravity individual** for free interactive coding/agent work, or the Gemini Developer API free tier for programmatic access.

### Cloud Run / Cloud Build / Artifact Registry / Secret Manager
Firebase Spark does not provide these Google Cloud products as no-billing infrastructure. They normally require a billing account even when usage may fall inside no-cost quotas.

### Firebase App Hosting
Requires Cloud Billing/Blaze for normal use and should not become an Ada dependency merely for convenience.

### Firebase Studio
Existing workspaces can still be used until the sunset, but new workspace creation/sign-up was disabled on June 22, 2026 and Firebase Studio shuts down on March 22, 2027. Do not adopt it as a new dependency. Google recommends AI Studio or Antigravity instead.

### Cloud Workstations, Apigee, Application Integration, Colab Enterprise
Treat these as billed/enterprise services unless a specific current entitlement proves otherwise.

## Ada recommendation

Use Google services only where they reduce development friction without becoming architectural dependencies:

1. **Antigravity individual free tier** for coding/repository work, scheduled development tasks, and parallel developer-agent experiments.
2. **Cloud Shell** for temporary CLI/testing when a browser-accessible shell is useful.
3. **BigQuery sandbox** for optional analytics experiments or exported AdaEval/task-event analysis.
4. **Gemini Developer API free tier** as a replaceable external evaluation/fallback worker with privacy gating.
5. **Firebase Spark** only for optional non-authoritative app features later.

The Ada reliability core stays on our VPS: PostgreSQL, Context Core, Qalam, authorization, task journal, backup/recovery, MCP gateway, and independent validators.
