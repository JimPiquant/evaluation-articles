# Article Plan: Quality and RAG Evaluators Deep Dive

> Part 3 of 6 in the AI evaluation pipeline series for the Azure Architecture Center.

## Purpose

Give developers a hands-on, implementation-ready guide to Microsoft Foundry's quality and RAG evaluators. This article covers every evaluator in these categories — what it measures, when to use it, how to configure it, and how to interpret and act on results. It also covers golden dataset design for RAG workloads, threshold-tuning strategies, custom evaluators for domain-specific quality criteria, and how to wire quality gates into CI/CD. Readers should finish the article able to evaluate any RAG application end-to-end.

## Audience

Software developers building RAG applications on Azure. Assumes familiarity with:
- RAG architecture basics (retrieval → augmentation → generation)
- Python development
- The concepts from the [overview article](ai-eval-pipeline-overview.md) (evaluation types, environment progression, evaluator categories)

This article includes code samples — it is aimed at practitioners, not leaders.

## Series context

This article is part of a cross-documentation-set series on AI evaluation:

- The **strategy guide** ([ai-eval-strategy-guide.md](ai-eval-strategy-guide.md)) targets the **Cloud Adoption Framework (CAF)** — strategic guidance for IT leaders and architects.
- The **AAC articles** (including this article) target the **Azure Architecture Center (AAC)** AI & ML section — architecture guidance and hands-on implementation.

### AAC article series

| # | Article | Status |
|---|---------|--------|
| 1 | [Building AI Evaluation Pipelines on Azure](ai-eval-pipeline-overview.md) | Published |
| 2 | [Reference Architecture for Agent Evaluation](ai-eval-ref-architecture.md) | Draft |
| **3** | **Quality and RAG Evaluators Deep Dive** (this article) | **Draft** |
| 4 | Agent Evaluators Deep Dive | Planned |
| 5 | Safety Evaluations | Planned |
| 6 | Red Teaming with PyRIT and Foundry | Planned |

## Outline

### 1. Introduction

- Relationship to the overview article — this is the hands-on companion for quality and RAG evaluation
- The problem: RAG applications fail in ways that are invisible without systematic evaluation — hallucination, irrelevant retrieval, incomplete answers, poor writing quality
- What this article covers vs what it doesn't (agent evaluators → article 4, safety → article 5)
- The scenario used throughout: evaluating a knowledge-base Q&A application that retrieves product documentation to answer customer questions

### 2. Evaluator catalog: quality and RAG

A reference section covering every evaluator in the general-purpose, RAG, and textual similarity categories. For each evaluator: what it measures, required inputs, scoring scale, when to use it, and what it doesn't catch.

#### General-purpose evaluators

| Evaluator | Measures | Required inputs | Scale | Use when |
|-----------|----------|-----------------|-------|----------|
| **Coherence** | Logical flow and organization of ideas | `query`, `response` | 1–5 | Responses need to be well-structured and logically connected |
| **Fluency** | Grammatical accuracy and readability | `response` | 1–5 | Responses need to be grammatically correct and readable |

- These are the baseline — run on every AI application, not just RAG
- Use together for a complete picture of writing quality
- Note: LLM-as-judge, English-language only, model inference cost per call

#### RAG evaluators

| Evaluator | Category | Measures | Required inputs | Scale | Use when |
|-----------|----------|----------|-----------------|-------|----------|
| **Groundedness** | System | Response aligns with context, no fabrication (precision) | `response`, `context`; `query` recommended | 1–5 | Always — the core RAG metric |
| **Groundedness Pro** (preview) | System | Strict groundedness via Azure AI Content Safety | `query`, `response`, `context` | Boolean | Need strict binary pass/fail, willing to use safety service |
| **Relevance** | System | Response accurately addresses the query | `query`, `response` | 1–5 | Always — ensures responses answer what was asked |
| **Response Completeness** (preview) | System | Response covers all critical info from ground truth (recall) | `ground_truth`, `response` | 1–5 | Have ground truth answers and need recall measurement |
| **Retrieval** | Process | Retrieved context chunks are relevant to the query | `query`, `context` | 1–5 | Assessing retrieval quality without ground truth labels |
| **Document Retrieval** | Process | Search quality metrics against ground truth labels | `retrieval_ground_truth`, `retrieved_documents` | Composite (NDCG, Fidelity, XDCG, Max Relevance, Holes) | Have query relevance labels, optimizing search parameters |

- Explain precision vs recall framing: Groundedness = precision (nothing fabricated), Response Completeness = recall (nothing missing)
- Explain system vs process distinction: system evaluators assess the final response, process evaluators assess the retrieval step
- Groundedness Pro vs Groundedness: trade-offs (stricter but binary, uses safety service, no score granularity)

#### Textual similarity evaluators

| Evaluator | Measures | Required inputs | Type |
|-----------|----------|-----------------|------|
| **Similarity** | AI-assisted semantic similarity | `response`, `ground_truth` | AI-assisted (1–5) |
| **F1 Score** | Token overlap precision/recall | `response`, `ground_truth` | Deterministic |
| **BLEU** | N-gram overlap (translation quality) | `response`, `ground_truth` | Deterministic |
| **GLEU** | Sentence-level n-gram overlap | `response`, `ground_truth` | Deterministic |
| **ROUGE** | Recall-oriented n-gram overlap | `response`, `ground_truth` | Deterministic |
| **METEOR** | N-gram overlap with ordering | `response`, `ground_truth` | Deterministic |

- When to use: comparing model outputs to known-good reference answers
- Trade-offs: deterministic metrics are fast and cheap but miss semantic equivalence; Similarity uses an LLM judge and captures meaning but costs more
- Practical guidance: use F1 Score or ROUGE as a cheap regression check; use Similarity when semantic equivalence matters

### 3. Choosing your evaluator stack

Decision framework for selecting which evaluators to run based on application type and available data:

- **Minimum viable RAG evaluation**: Groundedness + Relevance + Coherence + Fluency
- **Full RAG evaluation** (with ground truth): add Response Completeness + Retrieval + F1 Score or Similarity
- **RAG with retrieval optimization**: add Document Retrieval for parameter sweep
- **High-stakes RAG** (healthcare, finance, legal): add Groundedness Pro + safety evaluators (→ article 5)

**Diagram**: Evaluator selection decision tree — "Do you have ground truth?" → "Is retrieval quality a concern?" → recommended stack

### 4. Golden dataset design for RAG

- **Dataset schema**: JSONL format with `query`, `context`, `response`, `ground_truth` fields
- **Which fields you need**: depends on evaluator stack (table mapping evaluators → required fields)
- **Sourcing evaluation data**:
  - Manual curation from real user queries and expert-written answers
  - Production traffic sampling (with PII scrubbing)
  - Synthetic generation with LLMs (useful for bootstrapping, not a replacement for real data)
- **Coverage categories**: happy path, multi-chunk retrieval, edge cases (ambiguous queries, no-context scenarios, out-of-scope queries)
- **Dataset sizing**: 10–20 rows for dev iteration, 100+ rows for CI/CD gates (statistical confidence)
- **Versioning**: Git-tracked JSONL, semantic naming (`golden_set_v1.jsonl`)
- **Context field formatting**: single string with `\n\n` separators for multi-chunk retrieval
- **Ground truth for Document Retrieval**: query relevance labels format (`document_id` + `query_relevance_label`)

Code sample: example golden dataset JSONL (5–10 rows covering different scenarios)

### 5. Running evaluations: local development

Step-by-step guide using `azure-ai-evaluation` SDK for fast local iteration:

- Installing the SDK (`pip install azure-ai-evaluation`)
- Evaluator instantiation with `model_config`
- Running `evaluate()` on the dev dataset
- Interpreting the tabular results and per-row scores
- Iterating: what to do when scores are low (adjust prompts, improve retrieval, add context)

Code sample: `run_quality_eval_local.py` — complete script running Coherence, Fluency, Groundedness, Relevance against a JSONL dataset

### 6. Running evaluations: cloud (Foundry SDK)

Step-by-step guide using `azure-ai-projects` 2.x for cloud evaluations:

- Setting up the project client and OpenAI client
- Defining `DataSourceConfigCustom` with your schema
- Configuring `testing_criteria` with evaluator data mappings
- Running the evaluation and polling for results
- Viewing results in the Foundry portal
- When to use cloud eval vs local eval

Code sample: `run_quality_eval_cloud.py` — complete script running RAG evaluators via the cloud API

### 7. Threshold tuning and gate criteria

- **Default thresholds**: 1–5 scale, pass at ≥ 3 (Foundry default)
- **Why defaults aren't enough**: domain-specific quality bars, user expectations, regulatory requirements
- **Tuning methodology**:
  1. Baseline: run evaluators on your golden dataset, observe score distribution
  2. Calibrate: compare low-scoring rows to human judgment — does a "3" feel acceptable for your use case?
  3. Adjust: raise thresholds for high-stakes evaluators (e.g., Groundedness ≥ 4 for medical applications)
  4. Set gate criteria: minimum pass rate across the dataset (e.g., 90% of rows must pass Groundedness)
- **Gate criteria patterns**:
  - Per-metric minimum average score (e.g., average Groundedness ≥ 3.5)
  - Per-metric minimum pass rate (e.g., ≥ 90% of rows pass at threshold 3)
  - Zero-tolerance for specific failures (e.g., no Groundedness score below 2)
- **Avoiding score inflation**: judge model selection matters — document which judge model you use and keep it consistent

Table: Recommended starting thresholds by application risk level (low/medium/high)

### 8. Custom evaluators for RAG

When built-in evaluators don't cover your domain-specific criteria:

- **Code-based evaluators**: deterministic logic, no LLM cost
  - Example: citation format checker (does the response include proper source references?)
  - Example: response length validator (within acceptable bounds for your UI?)
  - Runtime constraints: 256 KB code, 2 min timeout, no network access, available packages (numpy, pandas, scikit-learn, nltk, etc.)
- **Prompt-based evaluators**: LLM-as-judge for subjective criteria
  - Example: domain terminology accuracy (does the response use correct medical/legal/financial terms?)
  - Example: brand tone evaluator (does the response match your organization's communication style?)
  - Scoring methods: ordinal (1–5), continuous (0.0–1.0), binary (true/false)
- **Creating and registering custom evaluators via SDK** (`project_client.beta.evaluators.create_version`)
- **Using custom evaluators in evaluation runs** (same `testing_criteria` pattern as built-in)

Code samples:
- Code-based evaluator: citation format checker
- Prompt-based evaluator: domain terminology accuracy scorer

### 9. CI/CD integration

Wiring quality evaluations into your deployment pipeline:

- **GitHub Actions**: using `azure-ai-evaluation` in a workflow
  - Trigger on PR for fast feedback
  - Trigger on push to main for gate enforcement
  - Parsing evaluation results and failing the workflow on threshold violations
- **Azure DevOps**: evaluation task integration (link to docs)
- **Gate logic**: which evaluators block merge vs which are advisory
- **Cost management**: running fewer evaluators on PR (Groundedness + Relevance) vs full suite on main

Code sample: GitHub Actions workflow snippet for RAG evaluation gate

### 10. Interpreting results and debugging failures

Practical guidance for acting on evaluation results:

- **Low Groundedness scores**: the model is hallucinating — improve context quality, add retrieval filters, tighten system prompts
- **Low Relevance scores**: responses don't address the query — check retrieval relevance, adjust query routing, improve system prompt instructions
- **Low Retrieval scores**: the retrieval step is returning irrelevant chunks — tune search parameters, adjust chunk sizes, improve embeddings
- **Low Coherence/Fluency**: writing quality issues — adjust system prompt tone/style instructions, consider a different model
- **Disagreement between Groundedness and Response Completeness**: precision-recall trade-off — the model is either too conservative (grounded but incomplete) or too expansive (complete but ungrounded)
- **Document Retrieval optimization**: using NDCG and Fidelity metrics to run parameter sweeps across search configurations

### 11. Where to go next

- [Agent Evaluators Deep Dive](article 4) — evaluating tool use, task completion, and multi-step reasoning
- [Safety Evaluations](article 5) — content risk scoring and safety gates
- [Red Teaming](article 6) — adversarial testing with PyRIT and the Foundry AI Red Teaming Agent
- [Reference Architecture](ai-eval-ref-architecture.md) — full working implementation with infrastructure and CI/CD

## Diagrams to create

1. **Evaluator selection decision tree** — flowchart guiding evaluator stack selection based on application type, available data, and risk level
2. **RAG evaluation data flow** — query → retrieval → context → generation → response → evaluators (showing which evaluator assesses which stage)
3. **Precision vs recall in RAG evaluation** — visual showing Groundedness (precision) and Response Completeness (recall) as complementary metrics
4. **Threshold tuning workflow** — baseline → calibrate → adjust → gate

## References

- Built-in evaluators overview: https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators
- General-purpose evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/general-purpose-evaluators
- RAG evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators
- Textual similarity evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/textual-similarity-evaluators
- Custom evaluators: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators
- Cloud evaluation SDK: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation
- azure-ai-projects SDK evaluator samples: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations
- Groundedness sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_groundedness.py
- Relevance sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_relevance.py
- Response completeness sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_response_completeness.py
- Coherence sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_coherence.py
- Fluency sample: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_fluency.py
- Optimize agentic RAG: https://aka.ms/optimize-agentic-rag-blog
- Azure DevOps evaluation task: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/run-evaluations-azure-devops
- Overview article (series part 1): ai-eval-pipeline-overview.md
- Reference architecture (series part 2): ai-eval-ref-architecture.md

## Notes

- Use "Microsoft Foundry" branding consistently
- Flag preview status clearly for: Groundedness Pro, Response Completeness, custom evaluators, cloud evaluations
- Code samples should use `azure-ai-projects` 2.x for cloud evaluations and `azure-ai-evaluation` for local execution — be explicit about which SDK is used where
- Judge model recommendation: `gpt-5-mini` for best balance of performance and cost (per Microsoft docs)
- All evaluators in this article use LLM-as-judge except the deterministic textual similarity metrics (F1, BLEU, GLEU, ROUGE, METEOR) and Document Retrieval
- English-language only for Coherence and Fluency — note this limitation
- Mermaid diagrams should use consistent `classDef` styling from the overview article
- The running scenario (product documentation Q&A) should be used for all code samples to maintain continuity
- Keep code samples self-contained enough to understand in the article; reference SDK samples for complete implementations
