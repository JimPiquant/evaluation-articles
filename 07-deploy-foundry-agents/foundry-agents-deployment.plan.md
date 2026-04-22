# Article Plan: Deploying Microsoft Foundry Agents — A Leader's Guide

> Companion to the AI evaluation series. Targets architects and IT leaders making
> deployment-shape decisions for Microsoft Foundry Agent Service.

## Purpose

Help architects and IT decision makers choose the right Foundry agent type for a
workload and understand what it takes to deploy it securely on Azure. The article
focuses on **deployment shape** — agent type selection, dependent platform services,
environment topology, and especially **private networking** — rather than on building
agent logic. It is a strategic-guidance piece, not a tutorial.

## Audience

- Solution architects, cloud architects, platform leads, and IT decision makers
  evaluating or standardizing on **Microsoft Foundry Agent Service**.
- Assumes Azure platform fluency (subscriptions, regions, RBAC, VNets, private
  endpoints, private DNS) but **no agent-development experience** required.
- **No code samples.** Code-first / IaC walkthroughs are deferred to a future
  developer-focused companion article.

## Series context

This article complements the existing AI-evaluation series in this repository by
covering the **deployment and platform** dimension that the evaluation articles
intentionally do not address. The promotion gates and reference architectures in the
evaluation series assume an agent has been deployed; this article describes how that
deployment is shaped and constrained.

| Article | Audience | Status |
|---------|----------|--------|
| [AI Evaluation Strategy for Technical Leaders](../00-strategy-guide-caf/ai-eval-strategy-guide.md) | IT leaders & architects | Draft |
| [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md) | Developers & architects | Published |
| [Reference Architecture for Agent Evaluation](../02-ref-architecture/ai-eval-ref-architecture.md) | Developers & DevOps | Draft |
| **Deploying Microsoft Foundry Agents — A Leader's Guide** ← this article | Architects & IT leaders | Planned |

## Outline

### 1. Introduction
- What "deploying a Foundry agent" actually means: a managed runtime backed by
  customer-owned data resources, not a single VM or container.
- Why deployment choices belong on the leadership agenda — cost envelope, regional and
  regulatory fit, network blast radius, and preview-feature risk are all decided
  before the first agent ships.

### 2. The three Foundry agent types
- **Prompt agents** — declarative single agents (model + instructions + tools), defined
  in the portal or via API/SDK. Best for prototyping and simple internal tools.
- **Workflow agents (preview)** — declarative orchestration of branching logic,
  human-in-the-loop steps, and multi-agent coordination. Authored visually in the
  portal or in YAML.
- **Hosted agents (preview)** — code-based agents (Agent Framework, LangGraph, custom
  code) packaged as containers and run on the Agent Service runtime.
- **Comparison table** (no code): code required, hosting model, orchestration scope,
  preview status, typical use cases, who owns what.
- **Decision flow diagram**: workload signals → recommended agent type.

### 3. Deployment models per agent type
- **Prompt agents**: portal/SDK definition, versioning, publish lifecycle; nothing to
  containerize.
- **Workflow agents**: portal authoring, YAML/VS Code authoring, publish lifecycle,
  preview caveats.
- **Hosted agents**: container build → Azure Container Registry → deploy via VS Code
  extension or `azd`; what Foundry manages (runtime, scaling, identity) versus what
  the customer owns (image, code, dependencies, observability hooks).
- **Shared platform dependencies** for all three: Foundry account/project, model
  deployments, Azure Storage, Azure Cosmos DB, Azure AI Search, Log Analytics,
  optional ACR.

### 4. Environments and lifecycle
- Dev / test / prod separation patterns: project-per-environment versus
  resource-per-environment, and the trade-offs (blast radius, cost, RBAC complexity).
- Promotion path: where the evaluation gates from the rest of this series plug in
  before production.
- Diagram: environment progression with evaluation hand-off.

### 5. Private networking for Foundry Agent Service *(headline section)*
- **Why network isolation matters**: regulated data, deny-by-default egress, controlled
  east-west traffic for Foundry's dependent data resources.
- **Standard Setup with private networking** — what it provisions:
  - VNet (or BYO VNet); **agent subnet delegated to `Microsoft.App/environments`**;
    private endpoint subnet.
  - Private endpoints for **Foundry, Azure AI Search, Azure Storage, Azure Cosmos DB**.
  - Required private DNS zones: `privatelink.cognitiveservices.azure.com`,
    `privatelink.openai.azure.com`, `privatelink.services.ai.azure.com`,
    `privatelink.search.windows.net`, `privatelink.documents.azure.com`,
    `privatelink.blob.core.windows.net`, `privatelink.file.core.windows.net`.
  - Public network access **disabled by default** on all dependent resources.
- **Architecture diagram**: BYO VNet topology with agent subnet, PE subnet, private
  DNS, on-prem connectivity options.
- **Known limitations and constraints** (presented as up-front design inputs):
  - **Programmatic deployment only** — no Azure portal path. Bicep or Terraform
    templates are required.
  - **RFC1918 subnets only** (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`); public
    address ranges are not supported.
  - **Agent subnet exclusivity** — one Foundry resource per agent subnet.
  - **Subnet sizing** — agent subnet `/24` recommended, `/27` minimum due to the
    `Microsoft.App/environments` delegation.
  - **Region co-location** — Foundry account, project, model deployments, Cosmos DB,
    Storage, AI Search, and managed identity must all live in the same region as the
    VNet.
  - **Capability-host singletons** — only one storage / thread storage / vector store
    connection per capability host; all three BYO resources must be supplied together.
  - **Tool-specific constraints**:
    - Grounding with Bing Search is restricted to a specific region list.
    - The File Search tool does **not** support Azure Blob Storage files in this setup.
  - **Firewall integration** — if Azure Firewall sits on the egress path, allowlist the
    Container Apps managed-identity FQDNs or the `AzureActiveDirectory` service tag,
    and disable TLS inspection on those flows.
  - **Resource provider registration** required up-front: `Microsoft.App`,
    `Microsoft.ContainerService`, `Microsoft.CognitiveServices`,
    `Microsoft.MachineLearningServices`, `Microsoft.Search`, `Microsoft.Storage`,
    `Microsoft.KeyVault`, `Microsoft.Network`, optionally `Microsoft.Bing`.
  - **Teardown ordering** — purge the Foundry resource before deleting the VNet to
    avoid stuck `serviceAssociationLinks`.
- **Access patterns to a private agent**: VPN gateway (P2S/S2S), ExpressRoute, Azure
  Bastion + jump box; portal access only from inside the VNet.

### 6. CI/CD from GitHub against a private Foundry *(new)*
- Why default GitHub-hosted runners cannot reach a private Foundry.
- Three patterns: VNet-injected GitHub-hosted runners (GHEC, `GitHub.Network`
  delegation), self-hosted runners on Azure Container Apps jobs, self-hosted runners
  on VMs/AKS.
- Comparison table; reference topology diagram.
- OIDC federation for the workflow identity; required role assignments.
- Practical guidance and DNS-zone gotchas.

### 7. Security, identity, and governance
- RBAC roles required to **deploy** (Azure AI Account Owner, Role Based Access
  Administrator or Owner) versus to **use** (Azure AI User).
- Managed identity model: how Agent Service connects to BYO Storage, Cosmos DB, and
  AI Search.
- Auditing and observability hooks: Log Analytics, Foundry observability.
- How preview features (workflow agents, hosted agents) change the risk profile and
  what to commit to in production.

### 8. Decision checklist for leaders
A one-page checklist suitable for a design review:
- Agent type for each workload.
- Region (data residency, model availability, Bing region overlap).
- Subscription and project topology (per-env, per-LOB).
- Network model (public, service-endpoint, or private with BYO VNet).
- RBAC structure for build, deploy, and use roles.
- Preview-feature exposure and rollback plan.
- CI/CD runner pattern and OIDC federation for the workflow identity.

### 9. Where to go next
- Future companion article: IaC walkthrough for the private-network Standard Setup
  (Bicep and Terraform).
- Cross-links to the AI evaluation strategy guide and the pipeline overview.

## Diagrams to create

1. **Agent type decision flow** — workload signals → prompt / workflow / hosted.
2. **Deployment topology per agent type** — what Microsoft manages vs. what the
   customer manages.
3. **Private-networking reference topology** — BYO VNet, agent subnet, private endpoint
   subnet, private DNS zones, on-prem connectivity, dependent data resources.
4. **Environment progression** — dev → test → prod with evaluation gate hand-off.

## References

- Foundry Agent Service overview & agent types:
  https://learn.microsoft.com/azure/foundry/agents/overview
- Agent development lifecycle:
  https://learn.microsoft.com/azure/foundry/agents/concepts/development-lifecycle
- Hosted agents concept:
  https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents
- Workflow agents concept:
  https://learn.microsoft.com/azure/foundry/agents/concepts/workflow
- Hosted-agent quickstart (azd):
  https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent-azd
- VS Code hosted-agent workflow authoring:
  https://learn.microsoft.com/azure/foundry/agents/how-to/vs-code-agents-workflow-pro-code
- **Private networking for Foundry Agent Service (primary source for §5)**:
  https://learn.microsoft.com/azure/ai-foundry/agents/how-to/virtual-networks
- Foundry Agent Service FAQ — virtual networking section:
  https://learn.microsoft.com/azure/foundry/agents/faq
- Quotas, limits, regional support:
  https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions
- Container Apps custom virtual networks (subnet sizing & delegation):
  https://learn.microsoft.com/azure/container-apps/custom-virtual-networks
- Container Apps + Azure Firewall (egress allowlist FQDNs):
  https://learn.microsoft.com/azure/container-apps/use-azure-firewall
- Foundry RBAC:
  https://learn.microsoft.com/azure/foundry/concepts/rbac-foundry
- Baseline Foundry chat reference architecture (cross-link, AAC):
  https://learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-azure-ai-foundry-chat
- Bicep sample — private-network standard agent setup:
  https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/15-private-network-standard-agent-setup
- Terraform sample — BYO VNet standard agent setup:
  https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-terraform/15b-private-network-standard-agent-setup-byovnet

## Notes

- Use **Microsoft Foundry Agent Service** consistently. Mention legacy
  "Agents (classic)" only to note its retirement (March 31, 2027) and steer readers
  toward the current service.
- Flag **workflow agents** and **hosted agents** as **preview** every time they appear;
  call out that production commitments should weigh this.
- Re-verify the private-networking Learn page just before publishing — the limitations
  list and region availability change frequently.
- No code samples in this article. Defer Bicep/Terraform/CLI walkthroughs to a future
  developer-focused companion article. This article ends with topology and decision
  guidance only.
