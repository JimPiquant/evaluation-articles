# Project Scope — AI Evaluation Articles Series

## Purpose

This repository produces a series of practitioner-oriented articles on AI evaluation for applications built with Microsoft Foundry on Azure. The series spans strategic guidance for IT leaders through hands-on implementation guides for developers and security engineers.

The goal is to give readers a clear, end-to-end understanding of how to design, implement, and operate evaluation pipelines — from organizational strategy down to specific evaluator configuration and CI/CD integration.

## Target publications

| Layer | Publication target | Audience |
|-------|--------------------|----------|
| Strategy | Cloud Adoption Framework (CAF) | IT leaders, architects, program managers |
| Implementation | Azure Architecture Center (AAC) | Software developers, DevOps engineers, security engineers |

## Article inventory

| # | Title | Audience | Target | Status |
|---|-------|----------|--------|--------|
| 00 | AI Evaluation Strategy for Technical Leaders | IT leaders & architects | CAF | Draft (~85%) |
| 01 | Building AI Evaluation Pipelines on Azure | Developers & architects | AAC | Complete |
| 02 | Reference Architecture for Agent Evaluation | Developers & DevOps | AAC | Complete |
| 03 | Quality and RAG Evaluators Deep Dive | Developers (RAG apps) | AAC | Planned (outline done) |
| 04 | Agent Evaluators Deep Dive | Developers (agentic apps) | AAC | Planned (outline done) |
| 05 | Safety Evaluations | Developers & security engineers | AAC | Planned (outline done) |
| 06 | Red Teaming with PyRIT and Foundry | Developers & security engineers | AAC | Planned (outline done) |
| 07 | Deploying Microsoft Foundry Agents — | Architects  | AAC | WIP |
| 08 | Deploying Microsoft Foundry IQ  — | Architects | AAC | To Do |
| 09 | Deploying Microsoft Foundry Tool Setup  — | Architects | AAC | To Do |

## Series structure

```
┌──────────────────────────────────────────────────────────────────┐
│ STRATEGY LAYER  (CAF — IT Leaders & Architects)                  │
│   Article 00: AI Evaluation Strategy                             │
│   Article 07: Deploying Foundry Agents                           │
└──────────────────────────────────────────────────────────────────┘
                              ↕
┌──────────────────────────────────────────────────────────────────┐
│ IMPLEMENTATION LAYER  (AAC — Developers & Engineers)             │
│   Article 01: Pipeline Overview (foundational)                   │
│   Article 02: Reference Architecture + companion repo            │
│   Articles 03–06: Deep dives (quality/RAG, agents, safety,       │
│                    red teaming)                                   │
└──────────────────────────────────────────────────────────────────┘
```

- **Strategy articles** (00, 07) target non-developers. No code samples; focus on decision frameworks, governance, and organizational guidance.
- **Implementation articles** (01–06) target developers. Include concrete code examples, evaluator configurations, and CI/CD integration patterns.
- **Article 02** includes a companion reference implementation (`02-ref-architecture/companion/`) with deployable Bicep, Python scripts, sample datasets, and CI/CD workflows.

## Running scenario

Articles 02–06 share a common scenario — **Contoso Support Agent** — a Microsoft Foundry Agent with search, CRM lookup, and ticketing tools. This scenario provides continuity across the deep-dive articles.

## Cross-article consistency requirements

| Concern | Convention |
|---------|------------|
| Product naming | "Microsoft Foundry" (not "Azure AI Foundry" or "Azure AI Studio") |
| Preview flags | Clearly mark preview features (hosted agents, workflow agents, agent evaluators, custom evaluators, cloud evaluations) |
| Environment model | Three-stage: **dev** (fast local feedback) → **test** (scale + CI/CD gates) → **prod** (continuous monitoring) |
| References | Source-backed claims; include URLs to Microsoft Learn or GitHub |
| Evaluation categories | Response quality, task completion, safety/content risk, adversarial resilience |
| Tone | Practitioner-to-practitioner — peer sharing experience, not textbook or marketing |

## Repository conventions

- Each article is a single Markdown file: `<article-name>.md`
- Every article has a companion plan file: `<article-name>.plan.md`
- Plan files must include: purpose, audience, outline, references
- No article drafting before its plan file is created and reviewed
- Diagrams use Mermaid syntax (rendered via `mermaid.lua` Pandoc filter)
- DOCX generation via `generate-docx.sh` (Pandoc pipeline)

## Companion implementation (Article 02)

Located at `02-ref-architecture/companion/ai-eval-ref-implementation/`:

| Component | Contents |
|-----------|----------|
| `src/agent/` | Agent definition and tool implementations (Python) |
| `src/evaluation/` | Local eval, cloud eval, evaluator config, gate checks (Python) |
| `datasets/` | Golden datasets (tiny dev set, full test set, safety probes) in JSONL |
| `infra/` | Bicep modules for Foundry project, model deployments, monitoring |
| `docs/` | Getting-started guide |

## What is out of scope

- Building a runnable application or service (this is a content repository)
- IaC walkthrough companion article (referenced in Article 07 — deferred)
- Evaluator SDK development or contribution


