# Article Plan: Building AI Evaluation Pipelines on Azure

> Part 1 of a series on AI evaluation pipelines for the Azure Architecture Center (AI & ML section).

## Purpose

Introduce software development teams to AI evaluation pipelines — what they are, why they matter, the taxonomy of evaluation types available in Microsoft Foundry, and how to structure evaluation across dev, test, and production environments. This article serves as the navigational entry point for deeper articles in the series.

## Audience

Software developers and architects who build or oversee AI applications on Azure. Assumes familiarity with Azure and basic AI/ML concepts but not necessarily with evaluation tooling. This is the overview article — no code samples. Code examples are covered in the follow-on deep-dive articles.

## Series context

This article is part of a cross-documentation-set series on AI evaluation:

- The **strategy guide** ([ai-eval-strategy-guide.md](../00-strategy-guide/ai-eval-strategy-guide.md)) targets the **Cloud Adoption Framework (CAF)** — strategic guidance for IT leaders and architects designing their evaluation approach.
- The **AAC articles** (this article and the deep dives below) target the **Azure Architecture Center (AAC)** AI & ML section — architecture guidance and hands-on implementation for developers, architects, and DevOps engineers.

### AAC article series

| # | Article | Audience | Status |
|---|---------|----------|--------|
| 1 | **[Building AI Evaluation Pipelines on Azure](ai-eval-pipeline-overview.md)** ← this article | Developers & architects | Published |
| 2 | [Reference Architecture for Agent Evaluation](../02-ref-architecture/ai-eval-ref-architecture.md) | Developers & DevOps | Draft |
| 3 | Quality and RAG Evaluators Deep Dive | Developers | Planned |
| 4 | Agent Evaluators Deep Dive | Developers | Planned |
| 5 | Safety Evaluations | Developers & security | Planned |
| 6 | Red Teaming with PyRIT and Foundry | Developers & security | Planned |

### CAF companion

| Article | Audience | Status |
|---------|----------|--------|
| [AI Evaluation Strategy for Technical Leaders](../00-strategy-guide/ai-eval-strategy-guide.md) | IT leaders & architects | Draft |

## Outline

### 1. Introduction
- What is an AI evaluation pipeline and why you need one
- The gap between "works in a notebook" and "safe to ship"
- Evaluation vs testing: how evaluation pipelines complement (not replace) traditional software testing

### 2. Reference architecture: evaluation pipeline
- **Diagram**: high-level architecture showing all major components and control points
- Key architectural components:
  - **Evaluation dataset** — golden datasets, versioning, representative data requirements
  - **Target under test** — model endpoint, RAG application, or agent
  - **Evaluator layer** — built-in, custom, and safety evaluators running against the target
  - **Result store and observability** — where scores land, how they're tracked over time
  - **Decision gate** — automated thresholds + human review; not all promotions are fully automated
  - **Promotion path** — how artifacts move from dev through test to production
- Where evaluations run: cloud (Foundry evaluation service) vs local (SDK)
- Security and governance: project vs resource boundaries, RBAC, region and preview considerations

### 3. Evaluation types: a decision framework
- Framed as a decision matrix, not a glossary — each type answers: what failure does it catch, when to use it, what it doesn't catch, and which pipeline stage it belongs in
- **Model / quality evaluations** — coherence, fluency, groundedness, relevance
- **RAG evaluations** — retrieval quality, document grounding, response completeness
- **Agent evaluations** — task adherence, tool call accuracy, intent resolution, task completion
- **Safety evaluations** — content risks (hate, violence, sexual, self-harm), code vulnerability, protected materials, ungrounded attributes
- **Red teaming** — adversarial probing, PyRIT attack strategies, Foundry AI Red Teaming Agent
- Recommended evaluator stacks by application type (RAG apps, agents, general) — which combinations cover which failure modes
- **Diagram**: Foundry evaluation ecosystem — built-in evaluators, custom evaluators, graders, safety service, red teaming agent and how they relate

### 4. Microsoft Foundry evaluation tooling
- Built-in evaluators catalog (overview, not exhaustive — link to deep-dive articles)
- Custom evaluators (code-based, prompt-based)
- Azure OpenAI graders
- Evaluation SDK: `azure-ai-projects` 2.x (new Foundry SDK) with fallback to `azure-ai-evaluation` for local and CI/CD scenarios

### 5. Environment guidance: dev → test → prod
- **Development**: rapid iteration with local evaluations, small datasets, fast feedback loops
- **Test / staging**: cloud evaluations at scale, full evaluator suites, CI/CD gate integration, statistical confidence
- **Production**: continuous evaluation, monitoring, observability, incident response
- **Diagram**: environment progression with evaluation checkpoints at each stage

### 6. Where to go next
- Links to the other articles in the series and the CAF strategy guide

## References

- Microsoft Foundry documentation (ground truth): https://learn.microsoft.com/en-us/azure/foundry/
- Built-in evaluators reference: https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators
- Risk and safety evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators
- Agent evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators
- Custom evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators
- Run evaluations in the cloud (Foundry SDK): https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation
- Continuously evaluate agents: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/continuous-evaluation
- AI Red Teaming Agent (preview): https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent
- Run AI Red Teaming Agent locally: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-red-teaming-agent-local
- Observability in generative AI: https://learn.microsoft.com/en-us/azure/foundry/concepts/observability
- Azure AI security best practices: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/ai/platform/security
- Azure Architecture Center AI & ML: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/
- Evaluation in Azure DevOps: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-evaluations-azure-devops
- PyRIT (Python Risk Identification Tool): https://github.com/Azure/PyRIT
- azure-ai-projects SDK samples: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations

## Diagrams to create

1. **High-level evaluation pipeline** — data → evaluators → scores → decision gate
2. **Environment progression** — dev (local/fast) → test (cloud/scale) → prod (continuous/monitor)
3. **Foundry evaluation ecosystem** — relationship between built-in evaluators, custom evaluators, graders, safety service, and red teaming agent

## Notes

- Use "Microsoft Foundry" consistently — verify latest branding at time of writing
- Flag preview status clearly for: AI Red Teaming Agent, agent evaluators, custom evaluators, continuous evaluation
- AAC format: architecture-focused, diagram-heavy, guidance over tutorial
- SDK: prefer `azure-ai-projects` 2.x for cloud evaluations; mention `azure-ai-evaluation` for local execution and CI/CD automation
