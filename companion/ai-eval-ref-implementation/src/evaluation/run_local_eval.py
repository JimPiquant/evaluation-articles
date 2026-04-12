"""
Local Evaluation Script — Development Workflow

Run evaluators locally against the tiny development dataset using the
azure-ai-evaluation SDK. Use this for rapid iteration during development.

Usage:
    python run_local_eval.py
"""

import os
import sys
from pathlib import Path
from pprint import pprint

import pandas as pd
from azure.ai.evaluation import (
    CoherenceEvaluator,
    FluencyEvaluator,
    GroundednessEvaluator,
    RelevanceEvaluator,
    ViolenceEvaluator,
    evaluate,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

# Model configuration for AI-assisted evaluators (quality + agent evaluators)
model_config = {
    "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
    "azure_deployment": os.environ.get("EVALUATION_MODEL", "gpt-4o"),
    "api_version": "2024-06-01",
}

# Azure AI project for safety evaluators (uses Foundry hosted models)
azure_ai_project = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
DATASET_PATH = REPO_ROOT / "datasets" / "golden_set_tiny.jsonl"


def run_local_evaluation():
    """Run a local evaluation with quality and safety evaluators."""

    print(f"Running local evaluation on: {DATASET_PATH}")
    print(f"Judge model: {model_config['azure_deployment']}")
    print()

    result = evaluate(
        data=str(DATASET_PATH),
        evaluators={
            "coherence": CoherenceEvaluator(model_config=model_config),
            "fluency": FluencyEvaluator(model_config=model_config),
            "groundedness": GroundednessEvaluator(model_config=model_config),
            "relevance": RelevanceEvaluator(model_config=model_config),
            "violence": ViolenceEvaluator(azure_ai_project=azure_ai_project),
        },
        evaluator_config={
            "coherence": {
                "column_mapping": {
                    "query": "${data.query}",
                    "response": "${data.ground_truth}",
                },
            },
            "fluency": {
                "column_mapping": {
                    "response": "${data.ground_truth}",
                },
            },
            "groundedness": {
                "column_mapping": {
                    "query": "${data.query}",
                    "response": "${data.ground_truth}",
                    "context": "${data.ground_truth}",
                },
            },
            "relevance": {
                "column_mapping": {
                    "query": "${data.query}",
                    "response": "${data.ground_truth}",
                },
            },
            "violence": {
                "column_mapping": {
                    "query": "${data.query}",
                    "response": "${data.ground_truth}",
                },
            },
        },
        azure_ai_project=azure_ai_project,
        output_path="./local_eval_results.json",
    )

    # Display results
    print("=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print()

    pprint(result["metrics"])
    print()

    tabular = pd.DataFrame(result.get("rows"))
    print(tabular.to_string(index=False))

    if result.get("studio_url"):
        print(f"\nView in Foundry portal: {result['studio_url']}")

    return result


if __name__ == "__main__":
    import contextlib
    import multiprocessing

    with contextlib.suppress(RuntimeError):
        multiprocessing.set_start_method("spawn", force=True)

    run_local_evaluation()
