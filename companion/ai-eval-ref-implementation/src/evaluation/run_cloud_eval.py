"""
Cloud Evaluation Script — Test / Production Workflow

Run agent evaluations in the cloud using the Foundry SDK (azure-ai-projects 2.x).
This submits an evaluation job to Foundry that invokes the agent, runs evaluators,
and stores results in the Foundry portal.

Usage:
    python run_cloud_eval.py
"""

import os
import time

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai.types.eval_create_params import DataSourceConfigCustom

load_dotenv()

# Configuration
endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_deployment = os.environ.get("EVALUATION_MODEL", "gpt-4o")
agent_name = os.environ.get("AGENT_NAME", "Contoso-Support-Agent")
agent_version = os.environ.get("AGENT_VERSION", "1")


def run_cloud_evaluation():
    """Run a cloud evaluation of the agent using the Foundry SDK."""

    # Create project client
    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Get OpenAI client for evaluation API
    client = project_client.get_openai_client()

    # Define input data schema
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "ground_truth": {"type": "string"},
            },
            "required": ["query"],
        },
        include_sample_schema=True,
    )

    # Define input messages template
    input_messages = {
        "type": "template",
        "template": [
            {
                "type": "message",
                "role": "user",
                "content": {
                    "type": "input_text",
                    "text": "{{item.query}}",
                },
            },
        ],
    }

    # Agent target configuration
    target = {
        "type": "azure_ai_agent",
        "name": agent_name,
        "version": agent_version,
    }

    # Define evaluators (testing criteria)
    testing_criteria = [
        # System evaluators (preview)
        {
            "type": "azure_ai_evaluator",
            "name": "task_adherence",
            "evaluator_name": "builtin.task_adherence",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "task_completion",
            "evaluator_name": "builtin.task_completion",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "intent_resolution",
            "evaluator_name": "builtin.intent_resolution",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        # Process evaluators
        {
            "type": "azure_ai_evaluator",
            "name": "tool_call_accuracy",
            "evaluator_name": "builtin.tool_call_accuracy",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "tool_selection",
            "evaluator_name": "builtin.tool_selection",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
        # Safety evaluators
        {
            "type": "azure_ai_evaluator",
            "name": "violence",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "hate_unfairness",
            "evaluator_name": "builtin.hate_unfairness",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        # Quality evaluators
        {
            "type": "azure_ai_evaluator",
            "name": "coherence",
            "evaluator_name": "builtin.coherence",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
    ]

    # Upload dataset
    print("Uploading evaluation dataset...")
    dataset_file = project_client.datasets.upload_file(
        name="contoso-agent-golden-set",
        file_path="datasets/golden_set_v1.jsonl",
    )
    print(f"Dataset uploaded: {dataset_file.name} (version: {dataset_file.version})")

    # Create evaluation
    print("Creating evaluation...")
    evaluation = client.evals.create(
        name="Contoso Agent Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created: {evaluation.id}")

    # Create evaluation run with agent target
    print("Starting evaluation run...")
    eval_run = client.evals.runs.create(
        eval_id=evaluation.id,
        name="contoso-agent-eval-run",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {
                "type": "file_id",
                "id": dataset_file.id,
            },
            "input_messages": input_messages,
            "target": target,
        },
    )
    print(f"Evaluation run created: {eval_run.id}")

    # Poll for completion
    while eval_run.status in ("running", "queued"):
        print(f"  Status: {eval_run.status}...")
        time.sleep(10)
        eval_run = client.evals.runs.retrieve(eval_id=evaluation.id, run_id=eval_run.id)

    print(f"\nEvaluation run completed: {eval_run.status}")

    if eval_run.status == "completed":
        print(f"Result counts: {eval_run.result_counts}")
        # Retrieve output items for detailed results
        output_items = client.evals.runs.output_items.list(
            eval_id=evaluation.id, run_id=eval_run.id
        )
        for item in output_items:
            print(f"\n  Query: {item.sample.get('query', 'N/A')[:80]}")
            for result in item.results:
                status = "✓" if result.get("passed") else "✗"
                print(f"    {status} {result['name']}: {result.get('label', result.get('score', 'N/A'))}")

        print(f"\nView full report: {eval_run.report_url}")
    else:
        print(f"Evaluation failed: {eval_run.error}")

    # Clean up
    client.evals.delete(evaluation.id)
    print("Evaluation deleted.")


if __name__ == "__main__":
    run_cloud_evaluation()
