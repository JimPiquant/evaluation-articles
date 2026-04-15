# Article Plan: Agent Evaluators Deep Dive

> Part 4 of 6 in the AI evaluation pipeline series for the Azure Architecture Center.

## Purpose

Give developers a hands-on guide to Microsoft Foundry's agent evaluators — the evaluators designed specifically for agentic workflows where an AI reasons through intents, calls tools, and orchestrates multi-step tasks. This article covers every agent evaluator, the system-vs-process evaluation framework, conversation and tool-call data formats, threshold tuning for agent-specific metrics, and how to wire agent evaluation into CI/CD. Readers should finish the article able to evaluate any Foundry agent end-to-end.

## Audience

Software developers building AI agent applications on Azure. Assumes familiarity with:
- Agent architecture basics (reasoning → tool calls → responses)
- The OpenAI function-calling schema
- Python development
- The concepts from the [overview article](../01-pipeline-overview/ai-eval-pipeline-overview.md) (evaluation types, environment progression)
- Optionally, the [reference architecture](../02-ref-architecture/ai-eval-ref-architecture.md) for a concrete implementation example

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
| **4** | **Agent Evaluators Deep Dive** (this article) | **Planned** |
| 5 | Safety Evaluations | Planned |
| 6 | Red Teaming with PyRIT and Foundry | Planned |

## Outline

### 1. Introduction

- Relationship to the overview and reference architecture articles
- Why agents need their own evaluators: multi-step reasoning, tool use, and task completion are fundamentally different from single-turn Q&A
- The two evaluation lenses: **system evaluation** (did the agent complete the task?) and **process evaluation** (did it use the right tools correctly along the way?)
- The scenario used throughout: evaluating a customer-support agent with tools (search_knowledge_base, lookup_order, create_ticket)

### 2. Evaluator catalog: agent evaluators

A reference section covering every agent evaluator. For each: what it measures, required inputs, scoring, preview status, and when to use it.

#### System evaluators (end-to-end outcomes)

| Evaluator | Measures | Required inputs | Output | Preview? |
|-----------|----------|-----------------|--------|----------|
| **Task Completion** | Agent completed the requested task with a usable deliverable | `query`, `response` | Pass/Fail | Yes |
| **Task Adherence** | Agent follows system instructions, rules, and constraints | `query`, `response` | Pass/Fail | Yes |
| **Intent Resolution** | Agent correctly identifies and addresses user intent | `query`, `response` | Pass/Fail (1–5 scale, thresholded) | Yes |
| **Task Navigation Efficiency** | Agent's action sequence matches expected optimal path | `actions`, `expected_actions` | Pass/Fail | No |

- Task Navigation Efficiency is unique: deterministic, requires ground truth action sequences, supports three matching modes (exact_match, in_order_match, any_order_match)
- System evaluators apply to the orchestrator agent in multi-agent systems
- RAG evaluators (Relevance, Groundedness) can also be applied to agent textual outputs

#### Process evaluators (step-by-step tool use)

| Evaluator | Measures | Required inputs | Output | Preview? |
|-----------|----------|-----------------|--------|----------|
| **Tool Call Accuracy** | Overall tool call quality (selection + parameters + efficiency) | `query`, `response`, `tool_definitions` | Pass/Fail (1–5 scale, thresholded) | No |
| **Tool Selection** | Correct tool chosen without unnecessary extras | `query`, `response`, `tool_definitions` | Pass/Fail | No |
| **Tool Input Accuracy** | All parameters correct (grounding, type, format, completeness, appropriateness) | `query`, `response`, `tool_definitions` | Pass/Fail | No |
| **Tool Output Utilization** | Agent correctly interprets and uses tool results | `query`, `response`, `tool_definitions` | Pass/Fail | No |
| **Tool Call Success** | Tool calls executed without technical failures | `response` | Pass/Fail | No |

- Tool Call Accuracy is the "umbrella" process evaluator — use it for overall assessment, drill into specific evaluators to diagnose failures
- Tool Input Accuracy has six strict sub-criteria — useful for catching subtle parameter errors

### 3. Data formats for agent evaluation

Agent evaluation requires structured conversation data. This section covers each format in detail:

#### Simple format
- `query` (string) + `response` (string) — for system evaluators that don't need tool call detail
- Example: `{"query": "Book a flight to Paris", "response": "I've booked flight AF123 departing Monday 9am"}`

#### Conversation array format
- `query` (array of messages) + `response` (array of messages including tool calls)
- Follows the OpenAI message schema: `role` (system, user, assistant, tool), `content` (text or tool_call/tool_result objects)
- System message is optional but important for Task Adherence and Task Completion
- Example with multi-turn tool calls

#### Tool definitions format
- JSON array following OpenAI function-calling schema
- Each tool: `type: "function"`, `function: {name, description, parameters}`
- Required for all process evaluators

#### Expected actions format (Task Navigation Efficiency)
- `actions`: list of message objects representing agent's actual steps
- `expected_actions`: ground truth optimal path
- Matching modes: exact_match, in_order_match, any_order_match

Code sample: complete JSONL dataset with all formats (5–10 rows)

### 4. Choosing your evaluator stack

Decision framework for agent evaluation:

- **Minimum viable agent evaluation**: Task Completion + Tool Call Accuracy + Coherence
- **Full agent evaluation**: add Task Adherence + Intent Resolution + Tool Selection + Tool Output Utilization + Tool Call Success
- **Regression testing**: add Task Navigation Efficiency with ground truth action sequences
- **Agent + RAG hybrid**: add Groundedness + Relevance from the RAG evaluators
- **High-stakes agents**: add safety evaluators (→ article 5) + Prohibited Actions + Sensitive Data Leakage

**Diagram**: Evaluator selection matrix — system vs process evaluators mapped to failure modes

### 5. Running agent evaluations: local development

Step-by-step guide using `azure-ai-evaluation` SDK:

- Installing the SDK
- Evaluator instantiation with model_config
- Running evaluate() with agent conversation data
- Interpreting results: Pass/Fail, reason fields, threshold-based scores

Code sample: `run_agent_eval_local.py`

### 6. Running agent evaluations: cloud (Foundry SDK)

Step-by-step using `azure-ai-projects` 2.x:

- Agent target evaluation pattern (`azure_ai_agent` target) — the agent runs live during evaluation
- Dataset evaluation pattern — pre-recorded conversations
- Data source configuration with `DataSourceConfigCustom`
- Testing criteria with agent evaluators
- Data mapping syntax: `{{item.field}}` vs `{{sample.output_items}}` vs `{{sample.output_text}}`
- Viewing results in the Foundry portal

Code sample: `run_agent_eval_cloud.py`

### 7. Threshold tuning for agent evaluators

- Default thresholds and scoring behavior
- Binary vs scaled evaluators: Task Completion/Adherence are pure binary; Intent Resolution and Tool Call Accuracy use 1–5 scale thresholded to binary
- Gate criteria patterns for agents:
  - System evaluator minimum pass rates (e.g., Task Completion ≥ 85%, Task Adherence ≥ 90%)
  - Process evaluator minimum pass rates (e.g., Tool Call Accuracy ≥ 85%, Tool Call Success ≥ 95%)
- Tuning methodology: baseline → calibrate against human judgment → adjust

Table: Recommended starting thresholds for agent evaluators

### 8. Continuous evaluation for agents

- Built-in continuous evaluation in Foundry (link to docs)
- How it works: samples production agent conversations, runs evaluators, detects drift
- Configuration and setup
- Quality drift monitoring: tracking scores over time
- Feedback loop: production findings → new golden dataset entries

### 9. Supported tools and limitations

- Supported tools: File Search, Function Tool, MCP, Knowledge-based MCP
- Limited support tools: Azure AI Search, Bing Grounding, Code Interpreter, etc. — which evaluators to avoid
- Multi-agent systems: apply system evaluators to the orchestrator, process evaluators to individual agents
- Judge model recommendation: `gpt-5-mini` for balance of performance and cost

### 10. CI/CD integration for agent evaluation

- GitHub Actions with `microsoft/ai-agent-evals@v3-beta` (recommended path for agents)
- How the action works: invokes the agent, runs evaluators, generates summary report
- Authentication: Azure OIDC with federated credentials
- Gate logic for agent-specific evaluators
- Cost management: which evaluators to run on PR vs full suite on main

Code sample: GitHub Actions workflow for agent evaluation gate

### 11. Where to go next

- [Quality and RAG Evaluators](../03-quality-rag/) — evaluating retrieval and generation quality
- [Safety Evaluations](../05-safety-evaluations/) — content risk scoring, safety gates, agent-specific safety
- [Red Teaming](../06-red-teaming/) — adversarial testing with PyRIT and the Foundry AI Red Teaming Agent
- [Reference Architecture](../02-ref-architecture/ai-eval-ref-architecture.md) — full working implementation

## Diagrams to create

1. **System vs process evaluation** — visual showing the two lenses applied to an agent workflow (intent → reasoning → tool calls → response)
2. **Evaluator coverage map** — which evaluators assess which part of the agent workflow
3. **Data format decision tree** — when to use simple format vs conversation array vs expected actions
4. **Agent evaluation in CI/CD** — GitHub Action flow: trigger → agent invocation → evaluator scoring → gate decision → report

## References

- Agent evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators
- Built-in evaluators overview: https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators
- Cloud evaluation SDK: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation
- Continuous evaluation: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/continuous-evaluation
- GitHub Action for agent evals: https://github.com/microsoft/ai-agent-evals
- Task completion sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_task_completion.py
- Task adherence sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_task_adherence.py
- Task navigation efficiency sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_task_navigation_efficiency.py
- Intent resolution sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_intent_resolution.py
- Tool call accuracy sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_call_accuracy.py
- Tool selection sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_selection.py
- Tool input accuracy sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_input_accuracy.py
- Tool output utilization sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_output_utilization.py
- Tool call success sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_tool_call_success.py
- Azure DevOps evaluation task: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-evaluations-azure-devops
- Overview article (series part 1): ../01-pipeline-overview/ai-eval-pipeline-overview.md
- Reference architecture (series part 2): ../02-ref-architecture/ai-eval-ref-architecture.md

## Notes

- Use "Microsoft Foundry" branding consistently
- Flag preview status: Task Completion, Task Adherence, Intent Resolution are preview; process evaluators are GA
- Code samples should use `azure-ai-projects` 2.x for cloud evaluations and `azure-ai-evaluation` for local — be explicit about which SDK is used where
- Judge model recommendation: `gpt-5-mini` (per Microsoft docs)
- The running scenario (customer-support agent) should match the reference architecture's Contoso Support Agent for continuity
- Supported tools limitation is important — call it out clearly so readers don't hit unexpected failures
- Mermaid diagrams should use consistent `classDef` styling from the overview article
