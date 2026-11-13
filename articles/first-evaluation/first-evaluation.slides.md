---
title: "Run your first evaluation"
subtitle: "E02 | Hands-on lab | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Learn the whole loop

- Generate an observed result
- Inspect independent evidence
- Apply policy
- Explain a pass and a failure

# Know the sample boundary

- Working local fixture tools
- Deterministic outcome checks
- No model-judged quality or safety
- No deployed production agent

::: notes
Run from the repository root. Offline fixture execution has no cloud charges.
Use samples/contoso-evaluation/README.md for exact optional cloud setup.
:::

# Run the baseline

```bash
python3 samples/contoso-evaluation/run.py \
  --candidate baseline --output build/baseline.json
python3 samples/contoso-evaluation/gate.py build/baseline.json
```

# Inspect a case

- Actual response and tool result
- Independent context/expected outcome
- Observed version
- Required checks and scored coverage

# Make failure visible

```bash
python3 samples/contoso-evaluation/run.py \
  --candidate regressed --output build/regressed.json
python3 samples/contoso-evaluation/gate.py build/regressed.json
```

The gate must return nonzero.

# Add Foundry deliberately

- Approved project, data, judge deployment
- Compatible SDK generation and dependency pins
- Actual recorded response, not reference
- Complete results and retained run IDs

::: notes
Cloud path is optional and needs live validation in an authorized environment:
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation
:::

# Lab completion

- Explain the regression using evidence
- Reject missing required results
- Propose a useful business rubric
- State what the fixture cannot prove

# Grounding and next path

[SDK setup](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation)

[Results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)

[Portal workflow](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app)

[Official samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations)

Next: E03 datasets; E07 results.
