# AI Evaluation Pipeline — Reference Implementation

> Companion repository for [AI Evaluation Pipeline: Reference Architecture for Agent Evaluation](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/ai-eval-ref-architecture) (Azure Architecture Center).

This repository provides a working implementation of an AI evaluation pipeline for a Microsoft Foundry Agent. It demonstrates how to evaluate a customer-support agent across development, test, and production environments using the Foundry evaluation SDK, GitHub Actions CI/CD, and Bicep infrastructure-as-code.

## What's included

| Directory | Contents |
|-----------|----------|
| `infra/` | Bicep templates for Foundry project, model deployments, and monitoring |
| `src/agent/` | Agent definition and tool specifications |
| `src/evaluation/` | Python scripts for local and cloud evaluation |
| `datasets/` | Versioned golden datasets (JSONL) for agent evaluation |
| `.github/workflows/` | GitHub Actions for PR gates and scheduled evaluations |

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Golden     │────▶│  Evaluation      │────▶│  Gate Decision  │
│  Dataset    │     │  Pipeline        │     │  (pass / fail)  │
│  (JSONL)    │     │  (SDK + Action)  │     │                 │
└─────────────┘     └──────────────────┘     └─────────────────┘
                           │
                    ┌──────┴──────┐
                    │   Foundry   │
                    │   Agent     │
                    │  (target)   │
                    └─────────────┘
```

## Prerequisites

- Azure subscription with permissions to create Foundry resources
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) — fast Python package and environment manager
- Azure CLI (`az`) installed and authenticated
- GitHub account (for CI/CD workflows)

## Quick start

### 1. Deploy infrastructure

```bash
az deployment group create \
  --resource-group <your-rg> \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam
```

### 2. Create a virtual environment and install dependencies

```bash
uv venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r src/requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your Foundry project endpoint, model deployment names, and agent ID
```

### 4. Run a local evaluation (development)

```bash
python src/evaluation/run_local_eval.py
```

### 5. Run a cloud evaluation

```bash
python src/evaluation/run_cloud_eval.py
```

### 6. Set up CI/CD

See [docs/getting-started.md](docs/getting-started.md) for GitHub Actions OIDC configuration and workflow setup.

## Project structure

```
├── infra/
│   ├── main.bicep                    # Orchestrator module
│   ├── modules/
│   │   ├── foundry-project.bicep     # Foundry hub + project
│   │   ├── model-deployment.bicep    # Agent model + judge model deployments
│   │   └── monitoring.bicep          # Log Analytics workspace + alerts
│   └── parameters/
│       ├── dev.bicepparam            # Development environment
│       ├── test.bicepparam           # Test / staging environment
│       └── prod.bicepparam           # Production environment
├── src/
│   ├── agent/
│   │   ├── agent_definition.py       # Contoso Support Agent setup
│   │   └── tools.py                  # Tool definitions (search, order lookup, ticketing)
│   ├── evaluation/
│   │   ├── run_local_eval.py         # Local evaluation (dev workflow)
│   │   ├── run_cloud_eval.py         # Cloud evaluation (Foundry SDK)
│   │   ├── evaluator_config.py       # Evaluator selection and thresholds
│   │   └── gate_check.py            # Gate logic: pass/fail from evaluation scores
│   └── requirements.txt
├── datasets/
│   ├── golden_set_v1.jsonl           # Full golden dataset (100+ examples)
│   ├── golden_set_tiny.jsonl         # Small dev dataset (15 examples)
│   └── safety_probes.jsonl           # Safety-focused test cases
├── .github/
│   └── workflows/
│       ├── evaluate-on-pr.yml        # PR gate: evaluate on pull request
│       └── evaluate-scheduled.yml    # Scheduled: periodic full evaluation
└── docs/
    └── getting-started.md            # Setup guide for CI/CD and OIDC
```

## Evaluators used

### System evaluators (preview)
- **Task Adherence** — Does the agent follow its instructions and constraints?
- **Task Completion** — Does the agent fully complete the requested task?
- **Intent Resolution** — Does the agent correctly identify the user's intent?

### Process evaluators
- **Tool Call Accuracy** — Does the agent call the right tools with correct parameters?
- **Tool Selection** — Does the agent select the necessary tools without redundancy?
- **Tool Output Utilization** — Does the agent correctly use tool results?
- **Tool Call Success** — Do tool calls execute without errors?

### Safety evaluators
- Violence, Hate/Unfairness, Sexual, Self-Harm
- XPIA (indirect prompt injection attack)

### Quality evaluators
- Coherence, Fluency, Groundedness

## Related resources

- [Building AI Evaluation Pipelines on Azure](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/ai-eval-pipeline-overview) — Series overview (Part 1)
- [Microsoft Foundry documentation](https://learn.microsoft.com/en-us/azure/foundry/)
- [Agent evaluators reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- [Cloud evaluation SDK](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation)
- [GitHub Action for agent evals](https://github.com/microsoft/ai-agent-evals)

## License

MIT
