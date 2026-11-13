# Article Plan: Safety Evaluations

> Part 5 of 6 in the AI evaluation pipeline series for the Azure Architecture Center.

## Purpose

Give developers a hands-on guide to Microsoft Foundry's risk and safety evaluators — the evaluators that detect harmful, biased, vulnerable, or policy-violating content in AI outputs. This article covers every safety evaluator, severity scales, content risk categories, agent-specific safety evaluators, threshold configuration, and how to build safety gates into CI/CD pipelines. Readers should finish the article able to implement comprehensive safety evaluation for any AI application or agent.

## Audience

Software developers and security engineers building AI applications on Azure. Assumes familiarity with:
- Basic AI application architecture (model endpoints, RAG apps, or agents)
- Python development
- The concepts from the [overview article](../01-pipeline-overview/ai-eval-pipeline-overview.md)

This article includes code samples — it is aimed at practitioners, not leaders.

## Series context

This article is part of a cross-documentation-set series on AI evaluation:

- The **strategy guide** ([ai-eval-strategy-guide.md](../00-strategy-guide-caf/ai-eval-strategy-guide.md)) targets the **Cloud Adoption Framework (CAF)** — strategic guidance for IT leaders and architects.
- The **AAC articles** (including this article) target the **Azure Architecture Center (AAC)** AI & ML section — architecture guidance and hands-on implementation.

### AAC article series

| # | Article | Status |
|---|---------|--------|
| 1 | [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md) | Published |
| 2 | [Reference Architecture for Agent Evaluation](../02-ref-architecture/ai-eval-ref-architecture.md) | Draft |
| 3 | [Quality and RAG Evaluators Deep Dive](../03-quality-rag/ai-eval-quality-rag.plan.md) | Planned |
| 4 | [Agent Evaluators Deep Dive](../04-agent-evaluators/ai-eval-agent-evaluators.plan.md) | Planned |
| **5** | **Safety Evaluations** (this article) | **Planned** |
| 6 | Red Teaming with PyRIT and Foundry | Planned |

## Outline

### 1. Introduction

- Why safety evaluation is non-negotiable for AI applications
- The difference between safety evaluation and quality evaluation: quality asks "is this a good answer?", safety asks "is this answer harmful?"
- Safety evaluation applies to all AI applications — not just agents
- What this article covers vs what it doesn't (red teaming / adversarial testing → article 6)
- The scenario: evaluating safety across a customer-support agent and a knowledge-base RAG application

### 2. Evaluator catalog: risk and safety

A reference section covering every safety evaluator. For each: what it detects, required inputs, scoring, and when to use it.

#### Content safety evaluators (0–7 severity scale)

| Evaluator | Detects | Applies to | Required inputs |
|-----------|---------|------------|-----------------|
| **Violence** | Violent or threatening language | Models + agents | `query`, `response` |
| **Sexual** | Sexual or explicit content | Models + agents | `query`, `response` |
| **Self-Harm** | Self-harm promotion or description | Models + agents | `query`, `response` |
| **Hate and Unfairness** | Biased, discriminatory, or hateful content | Models + agents | `query`, `response` |

- All four use the Foundry Evaluation service (hosted safety models), not your own LLM judge
- No `deployment_name` required — unlike quality evaluators
- 0–7 severity scale with four bands: Very Low (0–1), Low (2–3), Medium (4–5), High (6–7)
- Default threshold: 3 (fail at severity > 3)

#### Severity scale deep dive

Detailed tables for each content category showing what content falls into each severity band:
- Violence severity levels (0–7)
- Sexual content severity levels (0–7)
- Self-harm severity levels (0–7)
- Hate and unfairness severity levels (0–7)

#### Specialized safety evaluators

| Evaluator | Detects | Applies to | Required inputs | Output |
|-----------|---------|------------|-----------------|--------|
| **Protected Materials** | Copyrighted content (lyrics, recipes, articles) | Models + agents | `query`, `response` | Pass/Fail |
| **Code Vulnerability** | Security vulnerabilities in generated code | Models + agents | `query`, `response` | Pass/Fail |
| **Ungrounded Attributes** | Fabricated inferences about personal attributes | Models + agents | `query`, `response`, `context` | Pass/Fail |
| **Indirect Attack (XPIA)** | Indirect jailbreak via injected context | Models only | `query`, `response` | Pass/Fail |

- Code Vulnerability covers: path injection, SQL injection, code injection, tar slip, stack trace exposure, and more (across Python, Java, C++, C#, Go, JavaScript, SQL)
- XPIA detects three attack categories: manipulated content, intrusion, information gathering

#### Agent-specific safety evaluators (preview)

| Evaluator | Detects | Required inputs | Output |
|-----------|---------|-----------------|--------|
| **Prohibited Actions** | Agent performs explicitly disallowed actions | `query`, `response`, `tool_calls` | Pass/Fail |
| **Sensitive Data Leakage** | Agent exposes financial, medical, or personal data | `query`, `response`, `tool_calls` | Pass/Fail |

- Agent-target only — not available for dataset or model evaluations
- Prohibited Actions categories: universally banned, high-risk (needs human authorization), irreversible (needs disclosure + confirmation)
- Sensitive Data Leakage: detects format-level leaks using pattern matching

### 3. Choosing your safety evaluator stack

Decision framework based on application type and risk profile:

- **All AI applications (minimum)**: Violence + Sexual + Self-Harm + Hate/Unfairness
- **Applications generating code**: add Code Vulnerability
- **RAG applications**: add Protected Materials + Ungrounded Attributes + Indirect Attack (XPIA)
- **Agent applications**: add Prohibited Actions + Sensitive Data Leakage
- **Regulated industries**: full stack + lower severity thresholds + zero-tolerance gates

**Diagram**: Safety evaluator selection matrix by application type

### 4. Safety dataset design

- **Content safety probes**: crafting inputs that test safety boundaries without being themselves harmful
  - Ambiguous queries that could elicit unsafe responses
  - Queries that reference sensitive topics in legitimate contexts
  - Edge cases at the boundary of acceptable content
- **Agent safety probes**: scenarios testing prohibited actions and data leakage
  - Requests for unauthorized actions
  - Queries probing for sensitive data exposure
- **Dataset structure**: JSONL with `query`, `response` (and `tool_calls` for agent evaluators)
- **Balance**: mix of benign queries (should pass) and boundary queries (tests safety guardrails)
- **Relationship to red teaming**: safety datasets test known risks; red teaming (article 6) discovers unknown risks

Code sample: example safety evaluation dataset (5–10 rows)

### 5. Running safety evaluations

#### Configuration and execution

- No `deployment_name` needed — safety evaluators use hosted Foundry safety models
- Region requirements: Foundry project must be in a supported region
- Configuration examples for content safety, specialized, and agent-specific evaluators
- Running via `azure-ai-projects` 2.x (cloud) and `azure-ai-evaluation` (local/CI)

#### Interpreting results

- Content safety: severity score (0–7) + pass/fail + reason
- Specialized evaluators: binary pass/fail + reason
- Defect rate: aggregate metric = percentage of responses with undesired content

Code samples:
- Cloud evaluation with safety evaluators
- Local evaluation with safety evaluators

### 6. Threshold configuration and gate criteria

- **Default severity threshold**: 3 (block at > 3)
- **When to lower thresholds**: regulated industries, customer-facing applications, applications targeting vulnerable populations
- **Zero-tolerance patterns**: no responses with severity ≥ Medium for any content category
- **Gate criteria for CI/CD**:
  - Maximum defect rate per category (e.g., 0% for Violence, Sexual, Self-Harm, Hate)
  - Aggregate defect rate across all categories
- **Threshold tuning**: review borderline cases (severity 2–3) with domain experts to calibrate

Table: Recommended safety thresholds by application risk level

### 7. CI/CD integration for safety gates

- Adding safety evaluators to your existing evaluation pipeline
- Safety as a hard gate: block deployment if any content safety threshold is violated
- Combining safety with quality gates: both must pass for promotion
- GitHub Actions configuration for safety evaluation
- Azure DevOps task integration

Code sample: GitHub Actions workflow with safety gate

### 8. Production safety monitoring

- Continuous evaluation for safety drift
- Severity trend monitoring: are safety scores increasing over time?
- Incident response: escalation when severity ≥ threshold
- Safety dashboard: tracking defect rates across categories over time
- Relationship to Azure AI Content Safety filters (runtime protection vs evaluation-time assessment)

### 9. Where to go next

- [Red Teaming with PyRIT and Foundry](../06-red-teaming/) — adversarial testing to discover unknown safety risks
- [Quality and RAG Evaluators](../03-quality-rag/) — evaluating response quality
- [Agent Evaluators](../04-agent-evaluators/) — evaluating agent task completion and tool use
- [Reference Architecture](../02-ref-architecture/ai-eval-ref-architecture.md) — full working implementation

## Diagrams to create

1. **Safety evaluator coverage map** — which evaluators apply to models vs agents vs RAG applications
2. **Severity scale visualization** — 0–7 scale with band labels and example content descriptions
3. **Safety gate in CI/CD** — where safety evaluation sits in the deployment pipeline alongside quality gates
4. **Safety evaluation vs runtime protection** — evaluation (pre-deployment) vs Content Safety filters (runtime)

## References

- Risk and safety evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators
- Built-in evaluators overview: https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators
- Cloud evaluation SDK: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation
- Azure AI Content Safety: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
- Safety system message templates: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/safety-system-message-templates
- Risk and safety evaluator samples: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations
- Safety evaluations transparency note: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/safety-evaluations-transparency-note
- Evaluation regions and limits: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network
- AI Red Teaming Agent: https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent
- Overview article (series part 1): ../01-pipeline-overview/ai-eval-pipeline-overview.md
- Reference architecture (series part 2): ../02-ref-architecture/ai-eval-ref-architecture.md

## Notes

- Use "Microsoft Foundry" branding consistently
- Flag preview status: Prohibited Actions, Sensitive Data Leakage are preview; content safety evaluators are GA
- Safety evaluators use hosted Foundry safety models — no user-provided judge model needed
- Region support is important — call out which regions support safety evaluation
- Severity scale tables contain potentially disturbing content descriptions — include content warnings as the Microsoft docs do
- Agent-specific safety evaluators (Prohibited Actions, Sensitive Data Leakage) are agent-target only — make this limitation very clear
- Distinguish clearly between safety evaluation (assessment) and Content Safety filters (runtime protection) — they are complementary, not redundant
- Mermaid diagrams should use consistent `classDef` styling from the overview article
