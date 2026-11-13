# Article Plan: CI/CD for Microsoft Foundry Tools

> Part of the Microsoft Foundry deployment series, targeting the Azure Architecture Center (AI & ML section). Companion to the agent deployment and evaluation pipeline articles.

## Purpose

Give software developers and architects a practical end-to-end guide for delivering Microsoft Foundry tools through GitHub-based CI/CD pipelines. The article covers the full lifecycle — from repository structure and source-of-truth conventions, through build and validation, evaluation gates, packaging, and versioned deployment to Foundry environments — using GitHub Actions as the automation backbone. Developer-focused sections include concrete workflow examples; architect-facing sections focus on strategy, governance, and promotion policy without code samples.

## Audience

- **Primary**: Software developers who build and maintain Foundry tools (MCP server tools, function-calling tools, hosted tool containers).
- **Secondary**: Software architects designing and governing tool delivery pipelines at scale across multiple teams or environments.
- Assumes familiarity with:
  - Azure resource management and RBAC
  - GitHub Actions basics
  - Python or TypeScript development
  - The concepts from the [evaluation pipeline overview](../01-pipeline-overview/ai-eval-pipeline-overview.md) (evaluation types, environment progression, quality gates)

Developer sections include code and workflow YAML samples. Architect sections are prose-only.

## Series context

| Article | Audience | Status |
|---------|----------|--------|
| [AI Evaluation Strategy for Technical Leaders](../00-strategy-guide-caf/ai-eval-strategy-guide.md) | IT leaders & architects | Draft |
| [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md) | Developers & architects | Published |
| [Reference Architecture for Agent Evaluation](../02-ref-architecture/ai-eval-ref-architecture.md) | Developers & DevOps | Draft |
| [Deploying Microsoft Foundry Agents — A Leader's Guide](../07-deploy-foundry-agents/foundry-agents-deployment.md) | Architects & IT leaders | Draft |
| [Deploying Foundry Hosted Agents — A Developer's Guide](../07-deploy-foundry-agents/hosted-agents-developer-guide.md) | Developers & platform engineers | Planned |
| **CI/CD for Microsoft Foundry Tools** ← this article | Developers & architects | Planned |

## Outline

### 1. Introduction

- What Foundry tools are: MCP server tools and function-calling tools used by Microsoft Foundry agents.
- Why tools need their own CI/CD pipeline: they are independently versioned, cross-cutting dependencies used by multiple agents; a broken or regressed tool cascades across every agent that depends on it.
- What this article covers and what is out of scope (agent deployment shape, network topology — see the leader's guide; evaluation deep dives — see evaluation series).
- The end-to-end pipeline at a glance (developer narrative summary; diagram deferred to §2).

### 2. Repository structure and source-of-truth conventions *(architecture focus)*

- **Source of truth** for Foundry tool definitions: every tool is defined and versioned in Git; no manual portal edits to production.
- Recommended directory layout for a tool repository (or tool sub-directory in a monorepo): `tools/<tool-name>/`, `tools/<tool-name>/openapi.yaml` or `tool_spec.json`, `tools/<tool-name>/src/`, `tools/<tool-name>/tests/`, `tools/<tool-name>/Dockerfile` (for hosted tools).
- Mono-repo vs multi-repo trade-offs: governance simplicity vs team autonomy, atomic cross-tool changes vs independent release cadences.
- Branching strategy aligned to environment promotion: `main` tracks production; feature branches → PR → merge triggers the CI pipeline; environment tags (`v1.2.0`) trigger the CD pipeline.
- Diagram: repository layout and branching model.

### 3. Tool definition formats *(developer focus)*

- **MCP tools**: `tools/mcp-server/` with `pyproject.toml` or `package.json`, source, and a `tool_manifest.json` describing the server endpoint and capabilities.
- **Function-calling tools**: `openapi.yaml` (or `tool_spec.json`) that conforms to the Foundry tool schema; the spec is the contract, the implementation is behind it.
- Versioning: semantic versioning (`MAJOR.MINOR.PATCH`) tied to Git tags; `MAJOR` bump = breaking change in tool schema.
- Environment configuration: tool connection strings and endpoints stored as GitHub Actions secrets and environment variables; no secrets in source.
- Schema authoring tips: field descriptions as documentation (agents and evaluators both read them), required vs optional parameters, error response shapes.

### 4. Build and validation pipeline *(developer focus, with GitHub Actions YAML)*

- **Linting and static analysis**: `ruff` for Python tool implementations; `eslint` for TypeScript/Node MCP servers; `yamllint` for OpenAPI/tool-spec YAML.
- **Schema validation**: validate `openapi.yaml` against the OpenAPI 3.x spec (`spectral lint`); validate `tool_spec.json` against the Foundry tool definition JSON schema.
- **Unit tests**: fast, offline tests for the tool business logic using `pytest` (Python) or `jest` (TypeScript); mock the Azure SDK and downstream services.
- **Security scanning**: `bandit` (Python) or `semgrep` for common vulnerabilities; dependency audit with `pip-audit` or `npm audit`.
- Workflow: `.github/workflows/tool-ci.yml` — triggered on PR; runs lint → schema validation → unit tests → security scan in a single job with early exit on failure.
- Code snippet: `tool-ci.yml` — full workflow with checkout, Python/Node setup, caching, lint, schema validation, test, and security scan steps.
- Keeping CI fast: target < 3 minutes total; defer integration tests to the evaluation gate (§5).

### 5. Evaluation gates before promotion *(developer focus, with GitHub Actions YAML)*

- Why evaluation gates belong between CI and CD: unit tests verify correctness; evaluation gates verify that the tool *behaves correctly when an agent uses it* — catching semantic regressions that unit tests cannot.
- Gate strategy by environment:
  - **Dev → Test**: lightweight eval on a small golden dataset; focus on tool call accuracy and output schema conformance.
  - **Test → Prod**: full evaluator suite (tool call accuracy, tool selection, tool output utilization, safety); statistical confidence required; human review for borderline results.
- Running the evaluation gate:
  - Use the `microsoft/ai-agent-evals` GitHub Action (or the `azure-ai-evaluation` SDK directly for custom gates).
  - Target agent calls the tool under test; evaluators score the tool calls and outputs.
  - Gate blocks promotion if any metric falls below threshold.
- Linking to the evaluation series: cross-references to [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md) for evaluator catalog and threshold guidance.
- Code snippet: `tool-eval-gate.yml` — workflow that checks out the golden dataset, runs the evaluation Action against the tool endpoint, reads the summary report, and fails the job if thresholds are not met.
- Handling evaluation flakiness: retry strategy, minimum sample size, confidence interval guidance.

### 6. Packaging and versioning *(developer focus, with GitHub Actions YAML)*

- **MCP server tools (hosted)**: build a container image; tag with the semantic version and the Git commit SHA; push to Azure Container Registry.
- **Function-calling tools (non-hosted)**: the artifact is the validated OpenAPI/tool-spec file plus any deployment configuration; package as a versioned release asset.
- Container image hygiene: distroless or minimal base images, non-root user, no secrets baked in.
- Artifact storage: ACR for images; GitHub Release assets or Azure Blob for spec files; use immutable tags for production images (`v1.2.0`, not `latest`).
- Code snippet: `tool-package.yml` — workflow step sequence: Docker build → tag with `${{ github.ref_name }}` and `${{ github.sha }}` → `az acr login` → `docker push`.

### 7. Deployment to Foundry environments *(developer focus, with GitHub Actions YAML)*

- **OIDC / federated credentials** for GitHub Actions → Azure: no long-lived secrets; the workflow identity authenticates via a federated credential on an Azure app registration or managed identity.
  - Step-by-step setup: create an app registration, add a federated credential for the GitHub repo + environment + branch, grant `Azure AI Developer` and `AcrPush` roles.
  - Workflow snippet: `azure/login@v2` with `client-id`, `tenant-id`, `subscription-id`; confirm no `client-secret` in use.
- **Environment-specific deployment jobs**: use GitHub Actions environments (`dev`, `test`, `prod`) with environment protection rules.
  - `dev`: auto-deploy on merge to `main`; no approval gate.
  - `test`: deploy after dev smoke tests pass; optional manual approval.
  - `prod`: deploy after evaluation gate passes; required reviewer approval + deployment protection rules.
- **Deploying the tool to Foundry**:
  - For hosted MCP tools: patch the tool connection in the Foundry project via `az ai` CLI or the `azure-ai-projects` Python SDK; update the container image tag to the new version.
  - For function-calling tools: register or update the tool definition in the Foundry project by uploading the validated OpenAPI/spec file via the SDK.
- Code snippet: `tool-cd.yml` — complete CD workflow with OIDC login, environment matrix, deploy steps for both hosted and function-calling paths, and smoke test invocation.
- Idempotency: ensure deploy steps are safe to re-run (use upsert semantics where available).

### 8. Promotion strategy across environments and rollback *(architecture focus)*

- **Promotion criteria** (governance, no code):
  - Dev → Test: all CI checks green; lightweight eval gate passed; no critical security findings.
  - Test → Prod: full evaluation gate passed with statistical confidence; change reviewed and approved; documentation updated.
- **Rollback triggers**: automated alert from post-deployment monitoring (§9); manual trigger by on-call engineer; rollback defined as re-deploying the last known-good image tag or spec version.
- **Blue/green and canary patterns for tools**: because tools are invoked by agents, traffic-shifting a tool version means controlling which agent version calls which tool endpoint; coordinate tool and agent rollouts to avoid version skew.
- **Change management**: all production tool changes flow through pull requests; no direct edits to production tool registrations; break-glass procedure requires post-incident PR.
- Governance diagram: promotion flow with approval gates, evaluation checkpoints, and rollback paths.

### 9. Observability and post-deployment verification *(developer + architecture focus)*

- **Smoke tests post-deploy**: after each environment deployment, invoke the tool directly (or through a test agent) with a small set of known inputs and assert correct outputs; fail the deployment pipeline if smoke tests fail.
- **Tracing and logging**: instrument tool implementations to emit structured logs with a `tool_call_id` correlation key; wire to Application Insights / Log Analytics created alongside the Foundry project.
- **Metrics to track**: tool call latency (p50/p95/p99), error rate, schema validation failure rate, downstream dependency availability.
- **Drift detection**: run the evaluation gate on a schedule (nightly or weekly) against production traffic samples; alert on regression beyond threshold.
- **Foundry observability integration**: link tool traces to agent traces using the Foundry observability features; cross-reference to [Foundry observability docs](https://learn.microsoft.com/en-us/azure/foundry/concepts/observability).
- Code snippet (developer subsection): Application Insights instrumentation pattern for a Python MCP tool server using `opentelemetry-sdk` and `azure-monitor-opentelemetry`.

### 10. Where to go next

- [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md) — evaluation types, evaluator catalog, threshold guidance.
- [Reference Architecture for Agent Evaluation](../02-ref-architecture/ai-eval-ref-architecture.md) — how tools fit in the broader agent evaluation topology.
- [Deploying Microsoft Foundry Agents — A Leader's Guide](../07-deploy-foundry-agents/foundry-agents-deployment.md) — agent deployment shape, private networking, identity governance.
- [Deploying Foundry Hosted Agents — A Developer's Guide](../07-deploy-foundry-agents/hosted-agents-developer-guide.md) — hosted agent deployment with `azd`, versioned endpoints, canary + eval hand-off.
- Microsoft Foundry tools documentation for the current tool schema and SDK reference.

## Diagrams to create

1. **End-to-end CI/CD pipeline** — PR → CI (lint, validate, test, scan) → eval gate → package → CD (dev → test → prod) → monitoring loop.
2. **Repository layout** — directory tree with callouts for tool spec, source, tests, Dockerfile, and CI/CD workflow files.
3. **Promotion flow with gates** — branch/tag events that trigger each stage, approval gates, rollback paths.
4. **Observability topology** — tool trace → Application Insights → Log Analytics → alert → drift detection loop.

## References

- Microsoft Foundry tools overview:
  https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tools-overview
- MCP tools in Microsoft Foundry:
  https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/mcp
- Function tools / OpenAPI tool definition:
  https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/openapi-spec
- GitHub Actions for agent evaluations (`microsoft/ai-agent-evals`):
  https://github.com/microsoft/ai-agent-evals
- Azure Login GitHub Action (OIDC):
  https://github.com/Azure/login
- GitHub Actions OIDC with Azure (federated credentials):
  https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect
- GitHub Actions environments and protection rules:
  https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment
- Azure Container Registry authentication from GitHub Actions:
  https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication-github
- Foundry observability:
  https://learn.microsoft.com/en-us/azure/foundry/concepts/observability
- Azure Monitor OpenTelemetry distro (Python):
  https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python
- OpenAPI Specification 3.x:
  https://spec.openapis.org/oas/v3.1.0
- Spectral (OpenAPI linter):
  https://stoplight.io/open-source/spectral
- pip-audit (Python dependency vulnerability scanner):
  https://pypi.org/project/pip-audit/
- Semantic Versioning:
  https://semver.org/
- Evaluation in Azure DevOps:
  https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-evaluations-azure-devops
- azure-ai-evaluation SDK:
  https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/evaluate-sdk
- azure-ai-projects SDK samples:
  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations

## Notes

- Use **Microsoft Foundry** consistently (not "Azure AI Foundry" or "Azure AI Studio").
- Clearly distinguish **MCP server tools** (code-based, containerized) from **function-calling tools** (OpenAPI-spec-driven, non-hosted) throughout — they have different packaging and deployment paths.
- Flag preview features (hosted MCP tools, agent evaluators, continuous evaluation) on first mention in each section.
- Developer sections (§3–§7, §9 developer subsection) include workflow YAML and code snippets. Architect sections (§2, §8, §9 architecture subsection) are prose-only with diagrams.
- OIDC / federated credentials is the **required** auth pattern for GitHub Actions → Azure. Never recommend long-lived secrets (`client_secret`) for production CI/CD workflows.
- Re-verify all Microsoft Foundry tool schema references and SDK APIs before publication — the tools surface changes rapidly.
- The running scenario throughout is the **Contoso Support Agent** from the evaluation series, specifically its `search_knowledge_base` MCP tool, to maintain cross-article continuity.
