# Article Plan: Deploying Foundry Hosted Agents — A Developer's Guide

> Companion to `07-deploy-foundry-agents/foundry-agents-deployment.md` (the
> leader's guide). This article is the developer-focused deep-dive on
> **hosted agents** specifically, reflecting the new hosted-agents backend
> announced in the April 2026 Microsoft Foundry docs refresh.

## Problem and approach

The existing leader's guide intentionally treats all three agent types at a
strategic level and excludes code. Microsoft has just shipped a **new
hosted-agents backend** that materially changes how hosted agents are
deployed, scaled, versioned, addressed, and authenticated:

- New `azd ai agent` extension (≥ `0.1.27-preview`); the previous
  `0.1.25-preview` line targets the **legacy Azure Container Apps backend**
  and is now a different product surface.
- Compute is **provisioned on demand and torn down after a 15-minute idle
  timeout** — there are no manual start/stop operations and no always-on
  Container Apps revision to manage.
- **Sessions** are now a first-class platform concept: per-request isolated
  sandbox compute, opaque `agent_session_id`, mandatory
  `x-session-isolation-key` header, and a preview `Foundry-Features:
  HostedAgents=V1Preview` toggle.
- **Versions and agent endpoints** are explicit objects: `creating /
  active / failed / deleting / deleted` lifecycle, traffic-percentage
  `version_selection_rules` for canary routing, per-endpoint protocol
  selection (`responses`, `invocations`, or both).
- Each hosted agent has its own **`instance_identity`** (Microsoft Entra
  service principal) distinct from the project managed identity. Role
  assignments must use `--assignee-object-id` + `--assignee-principal-type
  ServicePrincipal` to avoid Microsoft Graph lookup failures.
- Two container protocols are supported: **OpenAI Responses** (stateful,
  uses platform sessions) and **Invocations** (the agent owns its own
  state; sessions don't apply).

This article is the **developer companion** the existing plan already
promised (line 169 of `foundry-agents-deployment.plan.md`), narrowed to
hosted agents only and built around the new backend. It gives developers
working code paths across **azd**, the **Python SDK**, and **REST / `az
rest`**, plus the evaluation hand-off implied by versioned canary
deployments.

The leader's guide stays as-is; this article cross-links to it for
strategic context (region/network/identity decisions) and links forward to
the evaluation pipeline article for the eval hand-off.

## Audience

- Application developers, platform engineers, and ML engineers who own a
  hosted-agent codebase end-to-end (Microsoft Agent Framework, LangGraph,
  Semantic Kernel, or custom code).
- Comfortable with containers, Azure CLI, OIDC federation, and basic RBAC.
- Want concrete commands and minimal SDK snippets for **azd, Python, and
  REST** in equal weight, not a prose overview.
- Reading after — or in parallel with — the leader's guide; we do **not**
  re-litigate agent-type selection or private-network design here.

## Series context

| Article | Audience | Status |
|---------|----------|--------|
| [Deploying Microsoft Foundry Agents — A Leader's Guide](../07-deploy-foundry-agents/foundry-agents-deployment.md) | Architects & IT leaders | Draft |
| **Deploying Foundry Hosted Agents — A Developer's Guide** ← this article | Developers & platform engineers | Planned |
| [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md) | Developers & architects | Published |
| [Reference Architecture for Agent Evaluation](../02-ref-architecture/ai-eval-ref-architecture.md) | Developers & DevOps | Draft |

File location: a new sibling folder, e.g.
`07-deploy-foundry-agents/hosted-agents-developer-guide.md` plus its
companion `hosted-agents-developer-guide.plan.md`. (Confirm folder layout
during implementation; using the same numbered folder keeps the two
guides discoverable as a pair.)

## Outline

### 1. Introduction
- What changed in the latest hosted-agents announcement (new backend,
  serverless lifecycle, sessions, instance identity, versioned endpoints).
- Who this article is for and what is **out of scope** (network design,
  agent-type selection, leadership trade-offs — covered in the leader's
  guide).
- The legacy-vs-new-backend boundary: `azd ai agent` extension version
  rule (`0.1.27-preview` and later vs `0.1.25-preview`); how to identify
  which backend an existing project is on.

### 2. Mental model: what a hosted agent actually is now
- A **container image** in your ACR, plus a **declarative
  `HostedAgentDefinition`** registered with Foundry (CPU, memory, image,
  protocol versions).
- An **agent endpoint** that resolves the active version and routes traffic
  by `version_selection_rules`.
- A **per-request session** that owns isolated sandbox compute, scoped by
  an isolation key.
- An **instance identity** (Entra service principal) distinct from the
  project MI.
- Diagram: image → version → endpoint → session → identity, with the
  responsibility split (you own / Foundry owns).

### 3. Prerequisites and one-time setup
- Tooling versions: `azd ≥ 1.24.0`, `azd ext install azure.ai.agents`
  (`≥ 0.1.27-preview`), Azure CLI `≥ 2.80`, Python `≥ 3.10`,
  `azure-ai-projects ≥ 2.1.0`, `azure-identity`.
- RBAC the developer needs: `Contributor` on the subscription/RG for
  provisioning; `Owner` or `User Access Administrator` for `azd deploy`'s
  agent-identity role assignments; `Azure AI Project Manager` at project
  scope to create/deploy the agent.
- Resource provider registrations (cross-link to leader's guide §5).
- Foundry project + model deployment + ACR + Log Analytics + App
  Insights — the resource set `azd provision` creates.

### 4. Build and run locally
- `azd ai agent init` interactive flow: language, template, model
  configuration, container size; non-interactive `--no-prompt` for CI.
- `azd ai agent run` and `azd ai agent invoke --local`.
- VS Code F5 / Foundry Toolkit Agent Inspector flow as a side-by-side.
- Common local errors (`AuthenticationError`, `ResourceNotFound`,
  `DeploymentNotFound`, port 8088 in use) and fixes.
- Quick note on protocol choice for the local server (Responses vs
  Invocations).

### 5. Deploy and verify
- `azd deploy` — what it does (remote container build, version create,
  endpoint patch, RBAC for the instance identity).
- The two protocol surfaces:
  - **Responses** (OpenAI-compatible, sessions-based, stateful per
    session).
  - **Invocations** (your agent manages state; sessions don't apply).
  - When to expose both.
- Verifying status with `azd ai agent show`, the REST `GET /agents/{name}`
  call, and `project.agents.get(...)` — show all three.
- Smoke test via Foundry Playground link emitted by `azd deploy`.

### 6. Versions and the agent endpoint
- Version lifecycle: `creating → active`; `failed`, `deleting`, `deleted`.
- Polling pattern (sample Python `wait_for_version_active` loop, REST
  equivalent with `az rest` + `--query`).
- `HostedAgentDefinition` fields: `image`, `cpu`, `memory`,
  `container_protocol_versions`, env vars (`AZURE_AI_PROJECT_TOOL_CONNECTION_ID`
  caveat for non-MCP samples).
- Endpoint routing as `merge-patch+json` PATCH on the agent:
  `version_selection_rules` with `FixedRatio`, traffic split between
  versions (100/0 → 90/10 → 100/0 for canary), `protocols` selection,
  required `Foundry-Features=AgentEndpoints=V1Preview` header.
- Python equivalents: `AgentEndpoint`, `VersionSelector`,
  `FixedRatioVersionSelectionRule`, `patch_agent_details`.

### 7. Sessions
- Why sessions exist: isolated sandbox compute per request, parallel
  conversations without shared state.
- Required headers and the preview gate
  (`Foundry-Features=HostedAgents=V1Preview`).
- `x-session-isolation-key` semantics — caller-defined string for
  grouping (per user, per tenant); same key required to delete.
- Lifecycle: create → invoke (Responses API with `agent_session_id`) →
  list → get → delete; idle compute deprovision after 15 minutes.
- `azd` limitations: implicit-only session create on `invoke`; explicit
  session ops require REST or Python.
- Code samples for create/list/get/delete in REST, Python (`project.beta.agents.*`),
  and azd (where supported).

### 8. The instance identity and downstream RBAC
- What `instance_identity.principal_id` is and how it differs from the
  project MI.
- Extracting the principal ID:
  - REST: `az rest ... --query "instance_identity.principal_id" -o tsv`.
  - Python: `agent.instance_identity["principal_id"]`.
- Assigning roles correctly:
  - `az role assignment create --assignee-object-id <pid>
    --assignee-principal-type ServicePrincipal --role <role> --scope <scope>`
    — never use `--assignee` because Graph lookups for agent SPs fail.
  - Common scopes/roles: `Azure AI Developer` on the project,
    `Storage Blob Data Contributor` on a storage account, plus the data
    roles needed for Cosmos DB and AI Search if the agent reads them
    directly.
- Verifying assignments with `az role assignment list`.
- Re-assignment after every published version — cross-link to the
  leader's guide §7 for the why; this section gives the commands.

### 9. Logs and monitoring
- `azd ai agent monitor` (`--tail`, `--type system`, `--session
  <id> --follow`).
- REST logstream endpoint:
  `GET /agents/{name}/versions/{v}/sessions/{sid}:logstream` — SSE,
  30-min connection cap, 2-min idle timeout, `event: log` frames with
  `timestamp / stream / message`.
- Python SDK gap (no logstream today) — call out the workaround.
- Wiring into Application Insights / Log Analytics created by `azd
  provision`; correlation IDs to log from inside the agent code so
  `monitor`'s output is searchable.

### 10. CI/CD recipe
- Minimal GitHub Actions / Azure DevOps pipeline:
  1. OIDC login.
  2. `azd provision` (idempotent) or skip if infra is managed separately.
  3. `azd deploy` to publish a new version.
  4. Poll until the new version is `active`.
  5. PATCH endpoint to send N% traffic to the new version (canary).
  6. Run evaluation gate (cross-link).
  7. PATCH endpoint to 100% traffic on success; otherwise PATCH back to
     the previous version.
- Identity hand-off: deployer SP needs Owner/UAA + Azure AI Project
  Manager; runtime instance identity gets the data-plane roles after
  publish.
- Private-Foundry caveat: cross-link to leader's guide §6 for runner
  patterns; do not re-explain runner topology.

### 11. Evaluation hand-off
- How versioned endpoints and traffic split map to evaluation gates from
  [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md):
  - Pin the eval run to a specific version with the agent endpoint
    `protocols` + an explicit `agent_version` selector or by addressing
    the version URL directly.
  - Use a dedicated `x-session-isolation-key` per eval run (e.g., the
    eval-run ID) so concurrent eval traffic doesn't mix with production
    sessions.
  - Tear down eval sessions deterministically (`DELETE /sessions/{id}`)
    so cost lines up with eval runs.
- Patterns for canary + eval:
  - Pre-promotion eval: 100/0, run eval against the new version URL
    directly, then flip traffic.
  - Live canary eval: 90/10, run eval over the 10% slice using the
    isolation key as a tag, alert on regression.
- Cross-link to [Reference Architecture for Agent Evaluation](../02-ref-architecture/ai-eval-ref-architecture.md)
  for where the hosted agent fits in the broader topology.

### 12. Troubleshooting and gotchas
- `SubscriptionNotRegistered`, `AuthorizationFailed`, `AcrPullUnauthorized`
  (project MI needs AcrPull on ACR).
- `azd ai agent init` fails → check `azd version` and extension version.
- Mixing legacy (`0.1.25-preview`, Container Apps backend) and new
  (`0.1.27-preview`, new backend) projects in the same repo.
- Agent identity role assignments that "look right" but fail at runtime —
  almost always missing `--assignee-principal-type ServicePrincipal`.
- Logstream silently disconnects after 2 min idle — add a heartbeat from
  the agent or reconnect from the client.
- `AZURE_AI_PROJECT_TOOL_CONNECTION_ID` placeholder left in `agent.yaml`
  for samples without an MCP connection.

### 13. What's next
- Pointer back to the leader's guide for region/network/identity
  strategy.
- Pointer to evaluation articles for what to do with the canary slice.
- Open items to revisit when hosted agents reach GA: SLA, removal of the
  preview headers, Python SDK logstream support, `azd` parity for session
  management.

## Code-sample policy

- Every operational topic (build, deploy, version, endpoint, session,
  identity, logs) shows **azd, Python, and REST** equivalents wherever
  the docs offer all three.
- Where a surface is missing (e.g., `azd` lacks standalone session
  create; Python lacks logstream), call it out explicitly rather than
  hiding the gap.
- Snippets are minimal and copy-pasteable. Long flows live in numbered
  steps, not in one giant block.
- Bash for REST and Linux/macOS; PowerShell variant only where Windows
  developers are likely to hit a real difference (e.g., the local-test
  `Invoke-RestMethod` example).

## Diagrams to create

1. **Hosted-agent object model** — image → version (`creating`/`active`/…)
   → agent endpoint (with `version_selection_rules`) → session
   (`agent_session_id`, isolation key) → instance identity.
2. **Request lifecycle** — client → endpoint → version selector → session
   sandbox (cold start vs warm) → 15-min idle deprovision.
3. **Canary + evaluation hand-off** — 100/0 → 90/10 → 100/0 with the eval
   gate sitting between traffic shifts.
4. **CI/CD pipeline** — OIDC → `azd deploy` → poll → endpoint patch →
   eval gate → promote/rollback.

## References

- Quickstart — Deploy your first hosted agent (azd / VS Code pivots):
  https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent?pivots=azd
- Manage hosted agents (REST / Python / azd pivots):
  https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/manage-hosted-agent?pivots=rest
- Manage hosted agent sessions:
  https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/manage-hosted-sessions
- Hosted agents concept:
  https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents
- Hosted agent permissions reference:
  https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions
- Agent identity concepts:
  https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity
- Microsoft Foundry Toolkit for VS Code: https://aka.ms/foundrytk
- Azure Developer CLI: https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd
- Companion leader's guide: `../07-deploy-foundry-agents/foundry-agents-deployment.md`
- Pipeline overview: `../01-pipeline-overview/ai-eval-pipeline-overview.md`
- Reference architecture: `../02-ref-architecture/ai-eval-ref-architecture.md`

## Notes

- **Preview labelling.** Hosted agents, sessions, and Microsoft Entra
  Agent ID are all preview. Flag preview status the first time each
  appears in a section, and again in the CI/CD and eval-handoff
  sections where production commitments matter.
- **Backend boundary.** Be explicit and consistent: "the new
  hosted-agents backend" vs "the legacy Container Apps backend
  (`azd ai agent` ≤ `0.1.25-preview`)." Do not assume readers know
  which one they're on.
- **Re-verify before publish.** The Learn pages cited above were updated
  recently and the API version (`v1`) and preview headers
  (`HostedAgents=V1Preview`, `AgentEndpoints=V1Preview`) may shift
  before GA. Refresh the snippets and the version-status table just
  before publishing.
- **Stay in scope.** Do **not** re-cover network design, agent-type
  selection, or organizational identity strategy — the leader's guide
  owns those. This article only goes deep on hosted agents.
- **No marketing voice.** Practitioner-to-practitioner tone, same as the
  rest of the series.
