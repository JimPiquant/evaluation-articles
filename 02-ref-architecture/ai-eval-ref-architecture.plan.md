# Article Plan: AI Evaluation Pipeline — Reference Architecture for Agent Evaluation

> Part 2 of 6 in the AI evaluation pipeline series for the Azure Architecture Center.

## Purpose

Provide a concrete, implementable reference architecture for evaluating a Microsoft Foundry Agent across development, test, and production environments. This article bridges the foundational concepts in the [overview article](../01-pipeline-overview/ai-eval-pipeline-overview.md) and a companion GitHub repository containing working code, infrastructure-as-code, and CI/CD pipelines. Readers should be able to deploy the reference implementation and adapt it to their own agent evaluation workflows.

## Audience

Software developers and DevOps engineers building AI agent applications on Azure. Assumes familiarity with:
- Azure resource management and Bicep
- Python development
- GitHub Actions
- The concepts from the overview article (evaluation types, environment progression, evaluator categories)

## Series context

This article is part of a cross-documentation-set series on AI evaluation:

- The **strategy guide** ([ai-eval-strategy-guide.md](../00-strategy-guide-caf/ai-eval-strategy-guide.md)) targets the **Cloud Adoption Framework (CAF)** — strategic guidance for IT leaders and architects.
- The **AAC articles** (including this article) target the **Azure Architecture Center (AAC)** AI & ML section — architecture guidance and hands-on implementation.

### AAC article series

| # | Article | Status |
|---|---------|--------|
| 1 | [Building AI Evaluation Pipelines on Azure](../01-pipeline-overview/ai-eval-pipeline-overview.md) | Published |
| **2** | **Reference Architecture for Agent Evaluation** (this article) | **Draft** |
| 3 | Quality and RAG Evaluators Deep Dive | Planned |
| 4 | Agent Evaluators Deep Dive | Planned |
| 5 | Safety Evaluations | Planned |
| 6 | Red Teaming with PyRIT and Foundry | Planned |

## Outline

### 1. Introduction
- Relationship to the overview article
- The scenario: evaluating a customer-support agent that uses search and CRM tools
- What you'll build — link to companion repo
- Prerequisites (Azure subscription, Foundry project, Python 3.10+, GitHub account)

### 2. Architecture overview
- End-to-end architecture diagram (agent → evaluation pipeline → CI/CD gate → production monitoring)
- Azure resource map diagram (Foundry project, model deployments, GitHub repo, GitHub Actions, Log Analytics)
- How the architecture maps to the overview's environment progression (dev → test → prod)

### 3. The target agent
- Sample agent description: "Contoso Support Agent" with tools (search_knowledge_base, lookup_order, create_ticket)
- Agent definition: model, instructions, tool definitions
- Why agent evaluation needs both system evaluators (end-to-end outcomes) and process evaluators (step-by-step tool use)

### 4. Golden dataset design
- Dataset schema for agent evaluation
  - Simple format: `query` (string) + `ground_truth` (optional)
  - Conversation format: `query` (array with system/user messages) + `response` (array with tool calls)
  - Tool definitions format
  - Expected actions for navigation efficiency
- Coverage categories: happy path, multi-tool, edge cases, adversarial/safety
- Versioning strategy: Git-tracked JSONL, semantic naming (golden_set_v1.jsonl)
- Dev dataset (tiny, 10–20 rows) vs test dataset (full, 100+ rows)

### 5. Evaluator configuration
- System evaluators (preview): task adherence, task completion, intent resolution
- Process evaluators: tool call accuracy, tool selection, tool output utilization, tool call success
- Safety evaluators: violence, hate/unfairness, sexual, self-harm, XPIA
- Quality baseline: coherence, fluency, groundedness
- Threshold table with recommended defaults
- Gate criteria: which evaluators block promotion and at what thresholds

### 6. Development workflow (local evaluation)
- Python script using `azure-ai-evaluation` SDK
- Evaluator instantiation with model_config
- Running `evaluate()` on the tiny dataset
- Interpreting tabular results and metrics
- Code snippet: run_local_eval.py

### 7. CI/CD pipeline (GitHub Actions)
- Workflow file using `microsoft/ai-agent-evals@v3-beta`
- Authentication: Azure OIDC with federated credentials
- Data file configuration (evaluators + queries)
- Trigger on PR and on push to main
- Interpreting the evaluation summary report
- Gate logic: when to block merge
- Code snippet: evaluate-on-pr.yml

### 8. Cloud evaluation (Foundry SDK)
- Python script using `azure-ai-projects` 2.x
- Agent target evaluation pattern (`azure_ai_agent` target)
- Data source configuration with `DataSourceConfigCustom`
- Testing criteria with `azure_ai_evaluator` entries
- Viewing results in the Foundry portal
- When to use cloud eval vs local eval vs GitHub Action
- Code snippet: run_cloud_eval.py

### 9. Production monitoring
- Continuous evaluation for agents (Foundry built-in) — link to docs
- Quality drift monitoring: tracking scores over time
- Safety incident response: escalation when severity ≥ 3
- Feedback loop: production findings → new golden dataset entries → re-evaluation
- Periodic red teaming cadence recommendation

### 10. Infrastructure as code
- Bicep module overview: Foundry project, model deployments (agent + judge), monitoring
- GitHub Actions OIDC setup (app registration, federated credential)
- Environment-specific parameters (dev/test/prod)
- Deployment commands

### 11. Companion repository walkthrough
- Directory layout with explanation
- Getting started steps: clone, deploy infra, configure secrets, run first eval
- Adapting to your own agent

## Diagrams to create

1. **End-to-end reference architecture** — Foundry project with agent, evaluation pipeline, GitHub Actions CI/CD, production monitoring loop. Color-coded by function.
2. **Azure resource map** — which Azure resources are deployed and how they connect.
3. **Evaluation flow** — how a single evaluation run progresses: dataset → agent invocation → evaluator scoring → results → gate decision.
4. **Environment progression** — dev/test/prod with specific tools and evaluators at each stage (builds on overview diagram but adds implementation specifics).

## References

- Microsoft Foundry documentation: https://learn.microsoft.com/en-us/azure/foundry/
- Cloud evaluation SDK: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation
- Agent evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators
- Built-in evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators
- Safety evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators
- Custom evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators
- GitHub Action for agent evals: https://github.com/microsoft/ai-agent-evals
- Azure DevOps evaluation task: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-evaluations-azure-devops
- Continuous evaluation: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/continuous-evaluation
- Foundry observability: https://learn.microsoft.com/en-us/azure/foundry/concepts/observability
- PyRIT: https://github.com/Azure/PyRIT
- azure-ai-projects SDK samples: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations
- Overview article (series part 1): ../01-pipeline-overview/ai-eval-pipeline-overview.md

## Notes

- Use "Microsoft Foundry" branding consistently (not "Azure AI Foundry" or "Azure AI Studio")
- Agent evaluators are preview — flag clearly in text and code
- Cloud evaluations are preview — note in relevant sections
- The `microsoft/ai-agent-evals@v3-beta` GitHub Action is the recommended CI/CD path (handles agent invocation + evaluation + reporting)
- Bicep templates should be functional and deployable, not just illustrative
- Code snippets in the article should be self-contained enough to understand in context; full files live in the companion repo
- Mermaid diagrams use `<br/>` for line breaks, consistent colored `classDef` styling from the overview article
