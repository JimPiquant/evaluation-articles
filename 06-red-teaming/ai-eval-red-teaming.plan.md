# Article Plan: Red Teaming with PyRIT and Foundry

> Part 6 of 6 in the AI evaluation pipeline series for the Azure Architecture Center.

## Purpose

Give developers and security engineers a hands-on guide to adversarial testing of AI applications using Microsoft's red teaming tools — the Foundry AI Red Teaming Agent for automated scanning and PyRIT for custom adversarial probing. This article covers how red teaming complements safety evaluation, the automated scanning workflow, attack strategies, agentic risk testing, and how to integrate red teaming into a continuous security cadence. Readers should finish the article able to run red teaming scans against their AI applications and agents.

## Audience

Software developers and security engineers responsible for AI application security. Assumes familiarity with:
- AI application or agent architecture
- Basic security testing concepts
- Python development
- The concepts from the [overview article](../01-pipeline-overview/ai-eval-pipeline-overview.md)
- Safety evaluators from [article 5](../05-safety-evaluations/ai-eval-safety.plan.md)

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
| 5 | [Safety Evaluations](../05-safety-evaluations/ai-eval-safety.plan.md) | Planned |
| **6** | **Red Teaming with PyRIT and Foundry** (this article) | **Planned** |

## Outline

### 1. Introduction

- What is AI red teaming and how it differs from traditional security red teaming
- Red teaming vs safety evaluation: safety evaluators assess known risk categories with structured datasets; red teaming probes for unknown vulnerabilities through adversarial simulation
- The NIST framework alignment: Govern → Map → Measure → Manage
- "Shift left" with automated red teaming: catch safety issues in development, not production
- What this article covers: Foundry AI Red Teaming Agent (automated) and PyRIT (custom/advanced)

### 2. The AI Red Teaming Agent

Overview of the Foundry AI Red Teaming Agent (preview):

#### How it works

- Three-phase approach: automated scanning → evaluation and scoring → reporting and logging
- Curated seed prompts per risk category
- Attack strategies from PyRIT applied as conversions to bypass safety alignments
- Fine-tuned adversarial LLM for simulating attacks
- Key metric: **Attack Success Rate (ASR)** = successful attacks / total attacks

**Diagram**: Red teaming workflow — seed prompts → attack strategy conversion → target AI system → safety evaluation → ASR score

#### Supported risk categories

| Risk category | Targets | Local/Cloud | Description |
|---------------|---------|-------------|-------------|
| Hateful and Unfair Content | Models + agents | Both | Bias and discrimination |
| Sexual Content | Models + agents | Both | Explicit or inappropriate sexual content |
| Violent Content | Models + agents | Both | Physical harm, weapons, incitement |
| Self-Harm Content | Models + agents | Both | Self-harm promotion or instructions |
| Protected Materials | Models + agents | Both | Copyrighted content |
| Code Vulnerability | Models + agents | Both | Security vulnerabilities in generated code |
| Ungrounded Attributes | Models + agents | Both | Fabricated personal attribute inferences |
| Prohibited Actions | Agents only | Cloud only | Policy-violating behaviors |
| Sensitive Data Leakage | Agents only | Cloud only | Exposure of sensitive information |
| Task Adherence | Agents only | Cloud only | Failure to follow assigned task rules |

#### Running automated scans

- Prerequisites: Foundry project, target AI system (model endpoint or agent)
- Configuration: risk categories, attack strategies, number of probes
- Local red teaming vs cloud red teaming
- Region support for cloud red teaming: East US 2, France Central, Sweden Central, Switzerland West, US North Central
- Interpreting the scorecard: ASR per category, attack strategy effectiveness

Code sample: running an automated red teaming scan

### 3. Agentic red teaming

Deep dive into agent-specific adversarial testing:

#### Sensitive Data Leakage testing
- Uses synthetic sensitive data and mock tools
- Generates scenarios prompting the agent to divulge information
- ASR measures format-level leaks via pattern matching
- Limitations: single-turn, English-only, synthetic data only

#### Prohibited Actions testing
- Dynamic adversarial prompts based on user-provided policies
- Three action categories: prohibited (never allowed), high-risk (needs human-in-the-loop), irreversible (needs disclosure + confirmation)
- Uses agent's tool descriptions to craft targeted probes
- Important: organizations must customize the default prohibited actions taxonomy to their own regulatory context

#### Task Adherence testing
- Probes three dimensions: goal achievement, rule compliance, procedural discipline
- Generates representative and adversarial agentic trajectories
- Tests both ordinary and edge-case scenarios

#### Indirect Prompt Injection (XPIA) testing
- Tests whether agents can be manipulated by malicious instructions hidden in external data sources
- Synthetic benign queries + mock tool outputs with injected attack placeholders
- Measures ASR using agentic risk categories (prohibited actions, data leakage, task adherence)

#### Supported agents and tools
- Supported: Foundry hosted prompt agents, container agents
- Not supported: workflow agents, non-Foundry agents, non-Azure tools, function tools, browser automation, connected agents, computer use
- Safety controls: cloud red teaming redacts harmful inputs, transient agent runs prevent data logging

### 4. Attack strategies

Catalog of PyRIT attack strategies available in the AI Red Teaming Agent:

#### Encoding and obfuscation strategies
- Base64, Binary, ROT13, Caesar, Atbash, Morse, URL encoding
- Leetspeak, ASCII art, ASCII smuggler, Unicode confusable, Unicode substitution
- Diacritic addition, character spacing, character swapping, tense changing

#### Structural strategies
- Flip (reverse characters)
- StringJoin (concatenation)
- SuffixAppend (adversarial suffix)
- ANSI attack (escape sequences)

#### Conversational strategies
- Jailbreak (UPIA — user-injected prompt attacks)
- Indirect Jailbreak (XPIA — injected in tool outputs / context)
- Multi-turn (context accumulation across turns)
- Crescendo (gradual escalation over successive turns)

Table: strategy name, description, best for which risk categories

### 5. PyRIT: custom adversarial testing

For organizations that need testing beyond what the automated agent provides:

#### What is PyRIT
- Python Risk Identification Tool — Microsoft's open-source red teaming framework
- Complements the Foundry AI Red Teaming Agent with custom orchestration
- When to use PyRIT directly: custom attack scenarios, non-Foundry targets, advanced multi-turn strategies, integration with existing security testing pipelines

#### Key concepts
- **Orchestrators**: manage the flow of adversarial probing (single-turn, multi-turn, crescendo, tree-of-attacks)
- **Targets**: the AI system under test (HTTP endpoints, Azure OpenAI, Foundry agents)
- **Converters**: transform attack prompts using encoding/obfuscation strategies
- **Scorers**: evaluate whether attacks succeeded (safety evaluators, custom classifiers)

#### Getting started with PyRIT
- Installation: `pip install pyrit`
- Basic single-turn attack example
- Multi-turn orchestration example
- Custom converter example

Code samples:
- Basic PyRIT scan against an Azure OpenAI endpoint
- Multi-turn crescendo attack with scoring

### 6. Red teaming in the development lifecycle

Positioning red teaming across the delivery lifecycle:

- **Design phase**: model selection — run red teaming scans against candidate models to compare safety postures
- **Development phase**: run local red teaming after safety evaluators pass to discover adversarial gaps
- **Pre-deployment phase**: full cloud red teaming scan as a pre-production gate
- **Post-deployment phase**: scheduled continuous red teaming on synthetic adversarial data

#### Cadence recommendations
- Run red teaming after every significant model, prompt, or tool change
- Schedule periodic scans (monthly or quarterly) even without changes — new attack strategies emerge
- Increase frequency for high-risk applications

**Diagram**: Red teaming touchpoints across the delivery lifecycle

### 7. Interpreting results and taking action

- **Reading the scorecard**: ASR per risk category, per attack strategy
- **Triaging findings**: not all successful attacks are equal — severity matters
- **Common mitigations**:
  - Safety system messages (link to templates)
  - Azure AI Content Safety filters (runtime protection)
  - Foundry Control Plane guardrails (for agents)
  - Prompt hardening against indirect injection
  - Tool-level access controls for agents
- **Re-testing after mitigation**: run the same scan to verify ASR reduction
- **False positives**: red teaming uses generative models for ASR scoring — always review results before acting

### 8. Known limitations

- Synthetic data only — not representative of real-world data distributions
- Mock tools retrieve synthetic data only, don't mock tool behaviors
- No fully locked-down sandboxing — adversarial testing is controlled to avoid real-world impact
- Adversarial population only — no observational population
- Non-deterministic scoring — false positives are possible
- English-only for most attack strategies and risk categories
- Single-turn for agent-specific risks (sensitive data leakage, prohibited actions)

### 9. Where to go next

- [Safety Evaluations](../05-safety-evaluations/) — structured safety evaluation (run before red teaming)
- [Agent Evaluators](../04-agent-evaluators/) — functional evaluation of agent task completion and tool use
- [Reference Architecture](../02-ref-architecture/ai-eval-ref-architecture.md) — full working implementation
- Microsoft AI Red Team blog posts for manual red teaming guidance

## Diagrams to create

1. **Red teaming workflow** — seed prompts → attack strategy → target → evaluation → ASR scorecard
2. **Red teaming in the delivery lifecycle** — design → dev → pre-deployment → post-deployment touchpoints
3. **Attack strategy categories** — visual grouping: encoding/obfuscation, structural, conversational
4. **Red teaming vs safety evaluation** — complementary roles: known risks (safety eval) vs unknown risks (red teaming)

## References

- AI Red Teaming Agent: https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent
- Run scans with AI Red Teaming Agent: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-scans-ai-red-teaming-agent
- Run Red Teaming Agent locally: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-red-teaming-agent-local
- PyRIT GitHub repository: https://github.com/Azure/PyRIT
- PyRIT documentation: https://azure.github.io/PyRIT/
- Risk and safety evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators
- Safety evaluations transparency note: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/safety-evaluations-transparency-note
- Azure AI Content Safety: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
- Safety system message templates: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/safety-system-message-templates
- Foundry Control Plane: https://learn.microsoft.com/en-us/azure/foundry/control-plane/overview
- Planning red teaming for LLMs: https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/red-teaming
- Three takeaways from red teaming 100 AI products: https://www.microsoft.com/security/blog/2025/01/13/3-takeaways-from-red-teaming-100-generative-ai-products/
- Microsoft AI Red Team blog: https://www.microsoft.com/security/blog/2023/08/07/microsoft-ai-red-team-building-future-of-safer-ai/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- Overview article (series part 1): ../01-pipeline-overview/ai-eval-pipeline-overview.md
- Reference architecture (series part 2): ../02-ref-architecture/ai-eval-ref-architecture.md

## Notes

- Use "Microsoft Foundry" branding consistently
- AI Red Teaming Agent is preview — flag clearly throughout
- Cloud red teaming region limitations are critical — call out supported regions early
- Attack strategies come from PyRIT — credit clearly
- The prohibited actions taxonomy disclaimer is important — organizations must customize to their own regulatory context
- Distinguish between automated red teaming (AI Red Teaming Agent) and manual/custom red teaming (PyRIT) — both have a role
- Known limitations should be prominently placed, not buried — readers need to understand what red teaming can and cannot tell them
- Harmful content in examples should be minimized — use the "how to loot a bank" example from the docs as illustration, but avoid creating new harmful example prompts
- Mermaid diagrams should use consistent `classDef` styling from the overview article
