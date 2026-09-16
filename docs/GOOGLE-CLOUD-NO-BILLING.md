# Google services we can use without billing information

Verified September 2026. This document is intentionally conservative: it lists services that can help Ada development without requiring us to attach a billing account/payment method, and separates them from products whose free quota still requires billing.

## Useful now

### Cloud Shell
- Free for users with a Google Cloud account.
- Useful for temporary CLI work, `gcloud`, Git, quick tests, and reproducing deployment commands.
- Not a production host for Ada; sessions are ephemeral and resource-limited.

### BigQuery sandbox
- Works without a credit card or billing account.
- Useful for exploratory analytics, large public datasets, and occasional offline analysis of exported Ada/AdaEval events.
- Do **not** use it as Context Core's authoritative transactional database. Sandbox capabilities are limited and are not a substitute for PostgreSQL.

### Firebase Spark plan
- No payment method needed.
- Some Firebase products/features have no-cost quotas.
- Potentially useful later for non-sensitive dashboards, Authentication experiments, App Check, or notifications.
- Do not move authoritative memory, secrets, or execution authority away from the VPS just because a Firebase quota is free.

### Gemini Developer API / Google AI Studio free tier
- New API projects can start on a free tier; upgrading to paid usage requires Cloud Billing.
- Useful as an **optional external evaluation/fallback model**, not as Ada's memory or authority.
- Context Core privacy classes still apply: LOCAL_ONLY data must never be sent to external models; LOCAL_PREFERRED requires an explicit redacted context packet.
- Quotas/model availability can change, so the model registry must record current limits rather than assuming permanent free capacity.

### Google AI Studio build/starter features
- Current AI Studio documentation describes a starter path that can publish a limited number of full-stack apps without creating a billed Google Cloud project.
- Useful for prototypes only. Ada production continues to live on our own controlled infrastructure.

## Do not plan around these as no-billing services

### Gemini Code Assist for individuals / Gemini CLI consumer access
Consumer access was deprecated and stopped serving requests in June 2026. Current Gemini Code Assist Standard/Enterprise requires licensed/billed organization access. The older marketing screen that says “use Gemini Code Assist at no cost” is not a reliable basis for the Ada architecture now.

### Cloud Run / Cloud Build / Artifact Registry / Secret Manager
Firebase Spark does not provide these Google Cloud products as no-billing infrastructure. They normally require a billing account even when usage may fall inside free quotas.

### Firebase App Hosting
Requires a Cloud Billing account/Blaze plan.

### Firebase Studio
Existing workspaces can still be used at no cost, but new workspace creation/sign-up was disabled in June 2026 and Firebase Studio is scheduled to shut down in March 2027. Do not adopt it as a new dependency.

### Cloud Workstations, Apigee, Application Integration, Colab Enterprise
Treat these as billed/enterprise services unless a specific current entitlement proves otherwise.

## Ada recommendation

Use Google services only where they reduce development friction without becoming architectural dependencies:

1. Cloud Shell for temporary CLI/testing.
2. BigQuery sandbox for optional analytics experiments/exported AdaEval data.
3. Gemini API free tier as a replaceable external test/fallback worker with privacy gating.
4. Firebase Spark only for optional non-authoritative app features later.

The Ada reliability core stays on our VPS: PostgreSQL, Context Core, Qalam, authorization, task journal, backup/recovery, MCP gateway, and validators.
