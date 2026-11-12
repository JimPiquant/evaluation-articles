# Research: azure foundry agent service idenitity with dev ops

*Generated: 30/04/2026, 14:13:40*

---

# Azure AI Foundry Agent Service Identity with DevOps

> Research report — last updated 2026-04-30. Based on Microsoft Learn documentation in the `learn.microsoft.com/azure/foundry/...` and `learn.microsoft.com/azure/devops/...` namespaces, plus the Azure Verified Modules registry.

## Executive Summary

Microsoft Foundry Agent Service uses a **layered Microsoft Entra ID identity model** in which a Foundry account/project's **system‑assigned managed identity** federates to an **agent identity blueprint**, which in turn issues short‑lived tokens for one or more **agent identities** (Entra service principals) that act on behalf of agents at runtime[^1][^2]. RBAC role assignments must be made on the *agent identity* (or, for some tools, the *project managed identity*) — not on a human user — and the assignments must be repeated whenever an agent is **published** because publishing creates a new distinct identity[^3]. For DevOps (CI/CD with Azure Pipelines or GitHub Actions), the recommended pattern is **workload identity federation (OIDC)** between the pipeline and an Entra **user‑assigned managed identity (UAMI) or service principal**, which is granted the Foundry control‑plane and downstream RBAC roles needed to provision Foundry resources, push container images, and assign roles to the platform‑created agent identity[^4][^5][^6]. The Azure Developer CLI (`azd`) can wire most of this up automatically for GitHub Actions, but for **Azure DevOps it currently configures only client‑credentials service connections** (OIDC for Azure DevOps must be configured manually or via the `AzureRM` service connection's WIF option)[^7][^8][^9].

---

## 1. The Foundry Agent Service identity model

There are **three distinct Entra principals** in any production Foundry Agent Service deployment, and confusing them is the most common cause of authentication failures[^1][^3]:

| Principal | Entra object type | Created when… | What it authenticates |
|-----------|------------------|---------------|------------------------|
| **Foundry project managed identity** (system‑assigned, sometimes also user‑assigned) | Managed identity / service principal | The Foundry account + project are provisioned | Acts as the *blueprint authority*; pulls images from ACR; reads Application Insights/Log Analytics; accesses BYO Cosmos DB / Storage / AI Search[^10][^11] |
| **Agent identity blueprint** | Entra "agent identity blueprint" object (preview) | First agent in a project is created (shared blueprint); each *published* agent creates its own dedicated blueprint | Acts as a governance template — Conditional Access, lifecycle, audit scope[^2] |
| **Agent identity** | Special Entra service principal ("Agent ID")  | Provisioned with the blueprint; one shared identity per project for unpublished agents, distinct identity per published agent application | The principal that calls *downstream tools* (MCP, A2A, Storage, Cosmos DB, Logic Apps, Graph, Key Vault) at runtime[^1][^3] |

### 1.1 Runtime token exchange

When an agent invokes a tool, Foundry Agent Service performs a four‑step OAuth 2.0 exchange — developers never handle the tokens directly[^1]:

```
                              Microsoft Entra ID
                                   │
 ┌───────────────────────┐   ① auth blueprint   ┌──────────────────┐
 │ Project managed       │──────────────────────▶│ Agent identity   │
 │ identity (federated   │                       │ blueprint        │
 │ credential)           │◀──────────────────────│ (FIC trust)      │
 └───────────────────────┘   ② agent identity    └──────────────────┘
            │                   token issued                │
            │                                               │
            ▼                                               ▼
 ┌───────────────────────┐                       ┌──────────────────┐
 │ Agent Service         │   ③ scoped access     │ Agent identity   │
 │ runtime               │──────token request───▶│ (Entra SP)       │
 │                       │   for "audience"      │                  │
 └───────────────────────┘                       └──────────────────┘
            │
            │   ④ authenticated tool call (Bearer <scoped token>)
            ▼
 ┌───────────────────────┐
 │ Downstream resource   │  validates token + RBAC against agent identity
 │ (Storage / MCP / A2A) │
 └───────────────────────┘
```

The blueprint's preferred OAuth credential type is a **federated identity credential (FIC)** that trusts the project managed identity, so **no client secret is ever stored** in Foundry configuration[^2]. The "audience" is the OAuth resource identifier of the *target* service, not the URL of the MCP/A2A endpoint — using the wrong audience produces 401s even when RBAC is correct[^1].

Common audiences (for setting `audience` on RemoteTool / RemoteA2A connections)[^1]:

| Downstream service | Audience |
|--------------------|----------|
| Azure Storage | `https://storage.azure.com` |
| Azure Logic Apps | `https://logic.azure.com` |
| Azure Cosmos DB | `https://cosmos.azure.com` |
| Microsoft Graph | `https://graph.microsoft.com` |
| Azure Key Vault | `https://vault.azure.net` |
| Foundry / Cognitive Services (e.g. OpenAPI tool to a Foundry account) | `https://cognitiveservices.azure.com/` |

### 1.2 Shared vs. distinct (published) agent identity

| State | Identity used at runtime | Implication for DevOps |
|-------|--------------------------|------------------------|
| **Unpublished** (drafting/testing in the project) | Shared **project agent identity** | All agents in the project share roles. Convenient, but a single role grant has a wider blast radius[^3]. |
| **Published** as an *agent application* | Distinct agent identity per agent | **You must re‑assign every RBAC role** that the agent needs against the new `agentIdentityId`. This must be in your release pipeline, not a manual portal step[^3][^12]. |

The `agentIdentityId` (and the blueprint ID) are exposed on the Foundry project resource's JSON view (Azure portal → project resource → Overview → JSON View) for the shared identity, and on the *agent application* resource's JSON view for published agents[^2].

---

## 2. RBAC roles you actually need

Foundry intentionally **separates control‑plane and data‑plane permissions**: classic Azure `Owner`/`Contributor` only grant management, not the ability to build with agents — you also need a Foundry "data action" role[^13][^14].

### 2.1 Built‑in Foundry roles

| Role | Plane | Typical use |
|------|-------|-------------|
| **Azure AI User** | Data | Build, edit, and call agents. Minimum role for developers and for the agent identity itself[^14][^12]. |
| **Azure AI Project Manager** | Data + limited control | Create and deploy hosted agents; can assign **Azure AI User** to the platform‑created agent identity[^12]. Recommended for the pipeline service principal that runs `azd up` or `az containerapp` deploys. |
| **Azure AI Account Owner** | Control + delegated data | Manage Foundry accounts, deploy models, create projects[^14]. |
| **Azure AI Owner** | Both | Full Foundry control + data; needed for fine‑tuning workflows that span planes[^13]. |
| **Role Based Access Administrator** (Azure built‑in) | Authorization | Required by the principal that runs `azd up`/Bicep so it can assign roles to the project MI and agent identity[^11][^15]. |

> **Note:** plain **Owner** and **Contributor** include `Microsoft.Authorization/roleAssignments/write` but **do not** grant Foundry data actions, so a Contributor cannot use the playground or call agents until also given `Azure AI User`[^14][^13].

### 2.2 Resources that need their own role assignments

For a **hosted agent** (the production deployment shape), these are the assignments your IaC/pipelines must produce[^11][^15]:

| Target resource | Assignee | Role | Purpose |
|----------------|----------|------|---------|
| Foundry account | Project managed identity | Azure AI User | Model access |
| Foundry project | Agent identity (shared and per published agent) | Azure AI User | Runtime model + tool access[^12] |
| Foundry project | End users / pipeline callers | Azure AI User | Invoke agents at runtime |
| Azure Container Registry | Project managed identity | **Container Registry Repository Reader** (or `AcrPull` for legacy) | Image pulls at runtime[^11][^16] |
| Azure Container Registry | Pipeline SP / UAMI | **Container Registry Repository Writer** (or `AcrPush`) | Image push from CI[^11] |
| Application Insights | Project managed identity | Reader / Monitoring Metrics Publisher (and `Log Analytics Data Reader` on the workspace for evaluations) | Telemetry ingest + read[^11][^17] |
| BYO Storage account | Project managed identity (SMI **and** UMI) | **Storage Blob Data Contributor** + **Storage Account Contributor** | Thread/file storage[^18] |
| BYO Cosmos DB (NoSQL) | Project managed identity | **Cosmos DB Operator** + **Cosmos DB Built‑in Data Contributor** | Thread storage[^18] |
| BYO Azure AI Search | Project managed identity | **Search Index Data Contributor** + **Search Service Contributor** | Vector store + index access[^18][^19] |
| Tool target (e.g. a Storage account the agent should read) | **Agent identity** (NOT project MI) | Resource‑specific data role (e.g. Storage Blob Data Reader) | Tool calls via MCP/A2A[^3] |

The single most common implementation mistake is granting the *project managed identity* a tool's data role and expecting the agent to use it — Foundry uses the **agent identity** for those tool calls, so the role must be on `agentIdentityId`[^1][^3].

---

## 3. Wiring this up with Azure DevOps

There are two DevOps surfaces to think about:

1. **Pipeline → Azure**: how the CI/CD agent authenticates *to* Azure to deploy infrastructure and the agent application.
2. **Deployed agent → downstream services**: how the *running* agent authenticates at runtime (covered in §1).

### 3.1 Pipeline → Azure: Workload Identity Federation (recommended)

Azure Pipelines supports an **ARM service connection backed by workload identity federation**, which exchanges the pipeline's short‑lived OIDC token for an Entra access token without storing a client secret or certificate[^4]. Two flavours exist[^4][^20]:

| Service connection sub‑type | What you grant roles to | Notes |
|-----------------------------|--------------------------|-------|
| **Workload identity federation (automatic)** | A new Microsoft Entra **app registration**/SP that Azure DevOps creates for you | Easiest; needs `Microsoft.Authorization/roleAssignments/write` on the target scope at creation time |
| **Workload identity federation (manual)** with a **user‑assigned managed identity** | An existing UAMI you created (e.g. `uami-foundry-deploy`) on which you've added a federated credential pointing at `https://vstoken.dev.azure.com/<orgId>` with subject `sc://<org>/<project>/<service-connection-name>` | Lets you use Conditional Access, RBAC reviews, and Microsoft Entra naming policies; preferred for regulated environments[^21] |

There is a **convert button** on existing ARM service connections that have stored secrets — Azure DevOps will move them to WIF in place, which is the lowest‑friction migration[^4].

> **`azd pipeline config` caveat for Azure DevOps:** As of the current `azd` releases, `azd pipeline config --provider azdo` configures **client credentials only** — passing `--auth-type federated` against Azure DevOps **errors out**. OIDC/federated is only the default for GitHub Actions and direct Azure Pipelines YAML edits[^7][^8]. If you want WIF on Azure Pipelines you must either (a) let `azd` create the SP, then convert the service connection to WIF in the portal, or (b) pre‑create the UAMI + service connection manually and skip `azd pipeline config`[^4][^21].

### 3.2 Roles for the pipeline identity

Grant the pipeline service principal / UAMI the **smallest set** of roles that lets it (i) create infra, (ii) push images, and (iii) assign the agent identity its runtime roles. A typical baseline:

| Scope | Role |
|-------|------|
| Resource group containing Foundry resources | `Contributor` (provision Foundry account, project, ACR, App Insights, Cosmos, Search, Storage) |
| Same RG | `Role Based Access Control Administrator` (for the role assignments below)[^15] |
| Foundry project | `Azure AI Project Manager` (so the pipeline can publish hosted agents and grant the agent identity `Azure AI User`)[^12] |
| ACR | `Container Registry Repository Writer` / `AcrPush` (image push)[^11] |

This combination lets a single pipeline identity run `az deployment group create` (Bicep), `az acr login --name … && docker push`, and the post‑deploy `az role assignment create --assignee <agentIdentityId> …` calls.

### 3.3 End‑to‑end DevOps pipeline shape

```
┌──────────────────┐   ① OIDC token exchange (WIF)   ┌──────────────────────┐
│ Azure Pipelines  │────────────────────────────────▶│ Microsoft Entra ID   │
│ agent (linux)    │                                 │ (UAMI / app reg)     │
└──────────────────┘                                 └──────────────────────┘
        │                                                       │
        │ ② az login --service-principal --federated-token       │
        ▼                                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Azure subscription                                                   │
│   - az deployment group create (Bicep)                               │
│       • Foundry account + project (system‑assigned MI)               │
│       • ACR, App Insights, Log Analytics, Cosmos, Storage, Search    │
│       • role assignments for project MI (Storage Blob Data Contrib…) │
│   - docker build + az acr login + docker push                        │
│   - az containerapp/azd deploy → publish agent application           │
│       (this creates the *distinct agent identity*)                   │
│   - az role assignment create --assignee <agentIdentityId>           │
│       --role "Azure AI User" --scope <project>                       │
│   - az role assignment create --assignee <agentIdentityId>           │
│       --role "Storage Blob Data Reader" --scope <data store>         │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.4 Azure Pipeline YAML (illustrative)

```yaml
# azure-pipelines.yml
trigger: [ main ]

variables:
  azureSubscription: 'sc-foundry-prod-wif'   # ARM service connection (WIF)
  resourceGroup: 'rg-foundry-prod'
  foundryProject: '/subscriptions/$(subId)/resourceGroups/$(resourceGroup)/providers/Microsoft.CognitiveServices/accounts/$(account)/projects/$(project)'

stages:
- stage: Provision
  jobs:
  - job: bicep
    pool: { vmImage: ubuntu-latest }
    steps:
    - task: AzureCLI@2
      inputs:
        azureSubscription: $(azureSubscription)
        scriptType: bash
        addSpnToEnvironment: true                     # exposes idToken / WIF
        scriptLocation: inlineScript
        inlineScript: |
          az deployment group create \
            -g $(resourceGroup) \
            -f infra/main.bicep \
            -p @infra/main.parameters.prod.json

- stage: PublishAgent
  dependsOn: Provision
  jobs:
  - job: deploy
    pool: { vmImage: ubuntu-latest }
    steps:
    - task: AzureCLI@2
      inputs:
        azureSubscription: $(azureSubscription)
        scriptType: bash
        scriptLocation: inlineScript
        inlineScript: |
          # Build + push container image (hosted agent)
          az acr login --name $(acrName)
          docker build -t $(acrName).azurecr.io/sales-agent:$(Build.BuildId) ./agent
          docker push $(acrName).azurecr.io/sales-agent:$(Build.BuildId)

          # Publish the agent application (creates a distinct agent identity)
          azd env set IMAGE_TAG $(Build.BuildId)
          azd deploy --no-prompt

          # Look up the new agent identity ID from the agent application JSON view
          AGENT_ID=$(az resource show \
            --ids $(agentApplicationResourceId) \
            --api-version 2025-09-01 \
            --query 'properties.agentIdentity.principalId' -o tsv)

          # Grant the *agent identity* the data roles it needs at runtime
          az role assignment create \
            --assignee-object-id $AGENT_ID \
            --assignee-principal-type ServicePrincipal \
            --role "Azure AI User" \
            --scope $(foundryProject)

          az role assignment create \
            --assignee-object-id $AGENT_ID \
            --assignee-principal-type ServicePrincipal \
            --role "Storage Blob Data Reader" \
            --scope $(targetStorageAccountId)
```

Key points:

1. `azureSubscription` references a service connection configured for **WIF (manual UAMI or automatic SP)** — no PAT, no secret in pipeline variables[^4][^21].
2. `addSpnToEnvironment: true` exposes the federated `idToken` so any inner script (e.g. `azd` or `terraform`) can perform its own `az login --federated-token`[^22].
3. The agent identity is **looked up after publish** because it doesn't exist until the agent application resource is created[^3][^12].
4. Use `--assignee-object-id` + `--assignee-principal-type ServicePrincipal` rather than `--assignee` to avoid Microsoft Graph lookup permissions in the pipeline (the pipeline SP rarely has Graph `Directory.Read.All`).

### 3.5 GitHub Actions equivalent

For GitHub Actions, `azd pipeline config` *does* support WIF natively — it creates a federated credential on the SP it provisions and stores `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (no client secret) in repo secrets[^7][^8]. The same role grants are required.

---

## 4. Bicep for the identity layer

The Azure Verified Module `avm/ptn/ai-ml/ai-foundry` provisions a Foundry account + project with the system‑assigned managed identity, model deployments, and the BYO Storage / Cosmos DB / AI Search resources used by Standard Agent Service[^23]. A trimmed‑down example showing the identity‑relevant pieces:

```bicep
// main.bicep (excerpt)
module foundry 'br/public:avm/ptn/ai-ml/ai-foundry:0.x.x' = {
  name: 'foundry'
  params: {
    baseName: baseName
    aiModelDeployments: [
      { name: 'gpt-4o', model: { format: 'OpenAI', name: 'gpt-4o', version: '2024-11-20' }, sku: { name: 'Standard', capacity: 10 } }
    ]
    // SMI is on by default; UMI optional
  }
}

// Grant the project MI the data roles for BYO storage
resource projectMiBlobContrib 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, foundry.outputs.projectPrincipalId, 'BlobDataContrib')
  scope: storage
  properties: {
    principalId: foundry.outputs.projectPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe' /* Storage Blob Data Contributor */)
  }
}

// Grant the pipeline UAMI Azure AI Project Manager so it can publish hosted agents
resource pipelineProjMgr 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(foundry.outputs.projectId, pipelineUamiPrincipalId, 'AIProjectManager')
  scope: resourceGroup()
  properties: {
    principalId: pipelineUamiPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'eadc314b-1a2d-4efa-be10-5d325db5065e' /* Azure AI Project Manager — verify with az role definition list */)
  }
}
```

The agent identity itself is **created out‑of‑band by Foundry** when the first agent / agent application is created, so its role assignments are typically scripted post‑deploy in the pipeline (§3.4) rather than declared in Bicep. There are full reference templates for both **basic** and **standard (BYO + private network)** in the [microsoft-foundry/foundry-samples](https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure) repo[^24].

---

## 5. azd in the loop

The Azure Developer CLI's AI agent extension (`azd ai agent`, ≥ 0.1.27‑preview) is the lowest‑friction path:

* `azd up` provisions the Foundry account + project + ACR + App Insights, runs the pre‑provision hook to materialise `AI_PROJECT_DEPLOYMENTS`/`AI_PROJECT_CONNECTIONS`/`ENABLE_HOSTED_AGENTS`, builds and pushes the container, and publishes the agent application[^25].
* It **automatically assigns `Azure AI User`** to the platform‑created shared agent identity for unpublished agents[^26][^12].
* It **does not** assign Container Registry, Application Insights, or custom downstream roles — you still need Bicep / `az role assignment create` for those[^26][^11].
* Required CI principal role for `azd up` to succeed: `Azure AI Project Manager` on the project (or `Owner` on the RG)[^12].

---

## 6. Common failure modes (what shows up in pipelines)

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `AuthorizationFailed` during `azd up` | Pipeline SP lacks `Contributor` and/or `RBAC Administrator` on RG | Add both at RG scope[^15][^27] |
| `AcrPullUnauthorized` at agent runtime | Project managed identity not granted `Container Registry Repository Reader`/`AcrPull` on ACR | Add role; ACR must be reachable over public endpoint for hosted agents today[^11][^12] |
| Agent in playground works, breaks after publish | After publish, **distinct** agent identity replaces shared identity; old role grants don't carry over | Re‑run role assignments against the new `agentIdentityId` after `azd deploy`[^3] |
| Tool call returns 401 even with correct role | Wrong **audience** on the connection (used MCP server URL instead of resource id) | Set `audience` to canonical resource id (`https://storage.azure.com`, etc.)[^1] |
| `az devops` can't create WIF service connection | Pipeline identity lacks `Microsoft.Authorization/roleAssignments/write` at intended scope | Have an Owner pre‑create the SC, or use the "manual" WIF flow with a UAMI[^21] |
| `azd pipeline config --provider azdo --auth-type federated` errors | OIDC/federated not supported via `azd` for Azure DevOps yet | Use GitHub Actions, or post‑process the SC to WIF in the portal[^7][^8] |
| `403` from agent calling Foundry account model | Agent identity missing `Azure AI User` on the *project* (and account) | `az role assignment create --assignee <agentIdentityId> --role "Azure AI User" --scope <project>`[^12] |

For tool‑specific troubleshooting, see the Foundry MCP and A2A authentication reference pages[^1][^28].

---

## 7. Security hardening checklist for production agent DevOps

1. **No client secrets anywhere.** Use WIF on the pipeline → Azure boundary, FIC blueprint credentials inside Foundry (default), and managed identity / agent identity for all data plane calls[^2][^4].
2. **Publish before granting wide data‑plane roles.** Grant only `Azure AI User` to the shared project identity; reserve the Storage / Cosmos / Logic Apps roles for distinct published agent identities so a draft agent can't reach production data[^3].
3. **Scope role assignments narrowly.** Resource‑level scope (e.g. one storage account) over RG scope; never subscription‑wide for tool data roles[^29].
4. **Apply Conditional Access to the agent identity blueprint.** The Microsoft Entra admin center → **Agent ID → All agent identities** view supports Conditional Access, identity protection, and governance over agent SPs[^30].
5. **Audit `agentIdentityId` reassignments.** Treat publishing an agent as a release event — fail the pipeline if the post‑publish role assignment step is skipped.
6. **Separate environments by Foundry project.** Projects are the unit of isolation for files, threads, and search indexes; use one project per environment so that dev agents cannot read prod threads[^31].
7. **Enable private networking for Standard agents** (`Microsoft.App/environments` delegated subnet, private endpoints on Storage/Cosmos/AI Search). Note the current limitation that the **ACR holding the hosted agent image must remain public‑reachable**[^32][^12].

---

## 8. Confidence assessment

| Area | Confidence | Notes |
|------|-----------|-------|
| Foundry agent identity model (blueprint, agent identity, FIC chain) | **High** — sourced directly from the canonical concept doc | Microsoft Entra Agent ID is in **preview**; APIs/IDs (e.g. role definition IDs in §4) may shift before GA[^2]. |
| Required RBAC roles for hosted agents | **High** — sourced from the official Hosted Agent Permissions Reference | Some roles (e.g. `Container Registry Repository Reader`) are newer replacements for `AcrPull`; both work today[^11]. |
| Azure DevOps WIF for ARM service connections | **High** — current GA feature on Azure DevOps Services | The **`AzureCLI@2`** task with `addSpnToEnvironment: true` is the supported way to surface the federated token to inline scripts[^4][^22]. |
| `azd pipeline config` Azure DevOps OIDC limitation | **High** — explicitly documented in the `azd` FAQ and pipeline‑config reference | This may change in future `azd` releases; verify against the current FAQ when implementing[^7][^8]. |
| Bicep examples in §4 | **Medium** — distilled from AVM module README and Foundry samples; role IDs (e.g. for *Azure AI Project Manager*) should be confirmed against `az role definition list --name "Azure AI Project Manager"` because role GUIDs occasionally change between previews[^14][^23]. |
| End‑to‑end pipeline YAML in §3.4 | **Medium** — illustrative, not executed against a live tenant | The exact API version and JSON path used to fetch `agentIdentity.principalId` from an agent application resource depend on the current `Microsoft.CognitiveServices` API; validate with `az resource show … --debug` before relying on it[^3]. |

Where I had to combine multiple sources (e.g. the post‑publish role reassignment step in the pipeline), the synthesis is explicit and grounded in the cited docs but not lifted from a single end‑to‑end Microsoft sample. There is **no canonical Microsoft "Foundry Agent Service + Azure DevOps WIF" tutorial as of this writing** — production teams typically combine the Foundry permissions reference[^11], the Azure DevOps WIF docs[^4][^21], and the `azd` agent extension[^25].

---

## Footnotes

[^1]: *Agent identity concepts in Microsoft Foundry — How agent identities work in Foundry / Runtime token exchange / audience table.* [`learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#how-agent-identities-work-in-foundry`](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#how-agent-identities-work-in-foundry)
[^2]: *Agent identity concepts — Key concepts (agent identity, blueprint, federated identity credentials).* [`learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#key-concepts`](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#key-concepts)
[^3]: *Agent identity concepts — Tool authentication / Assign permissions to the agent identity / "Repeat these role assignments for the new identity".* [`learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#tool-authentication`](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#tool-authentication)
[^4]: *Workload identity federation for Azure service connection (Azure Pipelines).* [`learn.microsoft.com/azure/devops/pipelines/release/configure-workload-identity`](https://learn.microsoft.com/azure/devops/pipelines/release/configure-workload-identity)
[^5]: *Agent2Agent (A2A) authentication — Microsoft Entra ID authentication / Agent identity / Foundry project managed identity.* [`learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication`](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-to-agent-authentication#microsoft-entra-id-authentication)
[^6]: *Connect agents to OpenAPI tools — Authenticate by using managed identity (Microsoft Entra ID).* [`learn.microsoft.com/azure/foundry/agents/how-to/tools/openapi#authenticate-by-using-managed-identity-microsoft-entra-id`](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/openapi#authenticate-by-using-managed-identity-microsoft-entra-id)
[^7]: *Azure Developer CLI tooling and environment FAQ — "What is OpenID Connect (OIDC), and is it supported?" — OIDC is the default for GitHub Actions and Azure Pipelines YAML, but `--auth-type federated` against Azure DevOps "results in an error".* [`learn.microsoft.com/azure/developer/azure-developer-cli/tooling-environment-faq#pipeline-configuration`](https://learn.microsoft.com/azure/developer/azure-developer-cli/tooling-environment-faq#pipeline-configuration)
[^8]: *Explore Azure Developer CLI support for CI/CD pipelines — Azure Pipelines: "Uses client credentials for authentication (OIDC not currently supported). Requires a Personal Access Token (PAT)."* [`learn.microsoft.com/azure/developer/azure-developer-cli/configure-devops-pipeline`](https://learn.microsoft.com/azure/developer/azure-developer-cli/configure-devops-pipeline)
[^9]: *Create a GitHub Actions CI/CD pipeline using the Azure Developer CLI — `azd pipeline config` defaults to OIDC for GitHub.* [`learn.microsoft.com/azure/developer/azure-developer-cli/pipeline-github-actions`](https://learn.microsoft.com/azure/developer/azure-developer-cli/pipeline-github-actions#create-a-pipeline-using-github-actions)
[^10]: *Secure OpenAPI endpoints for Foundry Agent Service — Find your Microsoft Foundry project's managed identity IDs.* [`learn.microsoft.com/azure/app-service/configure-authentication-ai-foundry-openapi-tool#find-your-microsoft-foundry-projects-managed-identity-ids`](https://learn.microsoft.com/azure/app-service/configure-authentication-ai-foundry-openapi-tool#find-your-microsoft-foundry-project's-managed-identity-ids)
[^11]: *Hosted agent permissions reference — Hosted agent solution architecture / Required Azure resources / Azure resource setup.* [`learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions`](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions)
[^12]: *Deploy a hosted agent — Required permissions ("Azure AI Project Manager at project scope … platform creates a dedicated Entra agent identity for each hosted agent at deploy time").* [`learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent#prerequisites`](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent#prerequisites)
[^13]: *Role-based access control for Microsoft Foundry — Notes and limitations ("Azure Owner and Contributor roles only include management permissions, and not development permissions").* [`learn.microsoft.com/azure/foundry/concepts/rbac-foundry#notes-and-limitations`](https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry#notes-and-limitations)
[^14]: *Quickstart: Set up your first Foundry resource — Built-in Azure RBAC developer roles for Foundry (Azure AI User / Project Manager / Account Owner / Owner).* [`learn.microsoft.com/azure/ai-services/multi-service-resource#grant-or-obtain-developer-permissions`](https://learn.microsoft.com/azure/ai-services/multi-service-resource#grant-or-obtain-developer-permissions)
[^15]: *Set up your environment — Required permissions table (Account Owner / RBAC Administrator / Azure AI User).* [`learn.microsoft.com/azure/foundry/agents/environment-setup`](https://learn.microsoft.com/azure/foundry/agents/environment-setup)
[^16]: *Quickstart: Deploy your first hosted agent (azd) — Troubleshooting "AcrPullUnauthorized: Grant AcrPull role to the project's managed identity on the container registry".* [`learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent#clean-up-resources`](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent#clean-up-resources)
[^17]: *Hosted agent permissions reference — Agent observability (Monitoring Reader on App Insights, Log Analytics Reader on workspace).* [`learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions#agent-observability`](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions#agent-observability)
[^18]: *Set up standard agent resources — Phase 3 / Phase 5 (project managed identity role assignments on Cosmos DB, Storage, AI Search).* [`learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup#provision-resources-step-by-step`](https://learn.microsoft.com/azure/foundry/agents/concepts/standard-agent-setup#provision-resources-step-by-step)
[^19]: *Connect an Azure AI Search index to Foundry agents — Setup, Keyless authentication: assign Search Index Data Contributor and Search Service Contributor to the project managed identity.* [`learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search#setup`](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/ai-search#setup)
[^20]: *Workload identity federation for Azure Pipelines public preview (announcement / overview).* [`learn.microsoft.com/azure/devops/release-notes/2024/sprint-237-update`](https://learn.microsoft.com/azure/devops/release-notes/2024/sprint-237-update) (referenced in the Microsoft Learn search index for "Workload identity federation for Azure Pipelines public preview").
[^21]: *Manually set an Azure Resource Manager workload identity service connection — UAMI flow with FIC subject `sc://<org>/<project>/<connection>`.* [`learn.microsoft.com/azure/devops/pipelines/release/configure-workload-identity-manual`](https://learn.microsoft.com/azure/devops/pipelines/release/configure-workload-identity-manual)
[^22]: *AzureCLI@2 task — `addSpnToEnvironment` exposes `idToken`, `servicePrincipalId`, and `tenantId` to inner scripts so they can perform their own federated `az login`.* [`learn.microsoft.com/azure/devops/pipelines/tasks/reference/azure-cli-v2`](https://learn.microsoft.com/azure/devops/pipelines/tasks/reference/azure-cli-v2)
[^23]: *Azure Verified Module — `avm/ptn/ai-ml/ai-foundry`: Bicep usage examples (account + project + Standard Agent Services + WAF‑aligned private networking).* [`github.com/Azure/bicep-registry-modules/tree/main/avm/ptn/ai-ml/ai-foundry`](https://github.com/Azure/bicep-registry-modules/tree/main/avm/ptn/ai-ml/ai-foundry)
[^24]: *Foundry samples — `microsoft-foundry/foundry-samples` infrastructure (private‑network standard agent, BYO VNet).* [`github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure`](https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure)
[^25]: *Deploy an agent to Microsoft Foundry with the Azure Developer CLI AI agent extension — `azd up` orchestration, identity and security.* [`learn.microsoft.com/azure/developer/azure-developer-cli/extensions/azure-ai-foundry-extension`](https://learn.microsoft.com/azure/developer/azure-developer-cli/extensions/azure-ai-foundry-extension#set-up-and-deploy-an-agent)
[^26]: *Agent identity concepts — Automation and deployment tooling ("azd does not configure Container Registry, Application Insights, or custom resource permissions").* [`learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#automation-and-deployment-tooling`](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#automation-and-deployment-tooling)
[^27]: *Quickstart: Deploy your first hosted agent — Troubleshooting "AuthorizationFailed during provisioning: Request Contributor role on your subscription or resource group".* [`learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent#clean-up-resources`](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent#clean-up-resources)
[^28]: *Set up MCP server authentication — Use agent identity authentication (preview).* [`learn.microsoft.com/azure/foundry/agents/how-to/mcp-authentication#use-agent-identity-authentication-preview`](https://learn.microsoft.com/azure/foundry/agents/how-to/mcp-authentication#use-agent-identity-authentication-preview)
[^29]: *Agent identity concepts — Security considerations ("Prefer narrow scopes (resource or resource group) over subscription-wide access").* [`learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#security-considerations`](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#security-considerations)
[^30]: *Agent identity concepts — Manage agent identities ("Microsoft Entra admin center → Entra ID → Agent ID → All agent identities").* [`learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#manage-agent-identities`](https://learn.microsoft.com/azure/foundry/agents/concepts/agent-identity#manage-agent-identities)
[^31]: *Set up your environment — "Data is isolated between projects. Agents in one project cannot access resources from another."* [`learn.microsoft.com/azure/foundry/agents/environment-setup#set-up-your-agent-environment`](https://learn.microsoft.com/azure/foundry/agents/environment-setup#set-up-your-agent-environment)
[^32]: *Set up private networking for Foundry Agent Service — Configure a network‑secured environment / Limitations (ACR must remain public‑reachable for hosted agents).* [`learn.microsoft.com/azure/foundry/agents/how-to/virtual-networks#configure-a-network-secured-environment`](https://learn.microsoft.com/azure/foundry/agents/how-to/virtual-networks#configure-a-network-secured-environment)
