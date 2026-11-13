#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from contoso.cloud import (
    execute_cloud, installed_packages, recorded_rows, request_spec, sdk_request, sdk_smoke,
)
from contoso.common import digest, read_json


def main():
    parser = argparse.ArgumentParser(description="Optional Foundry judging of recorded outputs; no agent provisioning.")
    parser.add_argument("--check-sdk", action="store_true", help="Imports/types only; no credentials or network.")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--endpoint", default=os.environ.get("AZURE_AI_PROJECT_ENDPOINT"))
    parser.add_argument("--judge-deployment", default=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME"))
    parser.add_argument("--allow-upload", action="store_true", help="Explicitly consent to upload recorded data and incur evaluation costs.")
    parser.add_argument("--resume", action="store_true", help="Use IDs in the existing output; never submit a second run.")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--poll-interval", type=float, default=5.0)
    args = parser.parse_args()
    if args.check_sdk:
        try:
            print(json.dumps(sdk_smoke(), indent=2))
            return 0
        except (ImportError, ValueError) as exc:
            print("SDK smoke failed: " + str(exc))
            return 2
    if not args.input or not args.output or not args.allow_upload:
        parser.error("--input, --output and explicit --allow-upload are required")
    if args.input.resolve() == args.output.resolve():
        parser.error("Input and output must be different files")
    endpoint = urlparse(args.endpoint or "")
    if (
        endpoint.scheme != "https" or not endpoint.hostname
        or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment
        or not endpoint.path.startswith("/api/projects/")
        or not endpoint.path[len("/api/projects/"):].strip("/")
    ):
        parser.error("Provide a valid HTTPS Foundry project endpoint without credentials/query parameters")
    if not args.judge_deployment:
        parser.error("An explicit --judge-deployment (or AZURE_AI_MODEL_DEPLOYMENT_NAME) is required")
    if args.output.exists() and not args.resume:
        parser.error("Output already exists; choose a new file or --resume to preserve remote IDs")
    try:
        packages = installed_packages()
        report = read_json(args.input)
        request = sdk_request(request_spec(recorded_rows(report), args.judge_deployment))
        prior = read_json(args.output) if args.resume else None
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=args.endpoint, credential=credential) as project,
            project.get_openai_client(max_retries=0, timeout=30.0) as client,
        ):
            result = execute_cloud(
                client, report, digest(args.input), args.output, args.judge_deployment,
                args.timeout, args.poll_interval, resume=prior, typed_spec=request,
                packages=packages, environment={"project_endpoint": args.endpoint},
            )
        print("Recorded-output judging completed. All pages retained in " + str(args.output))
        print("Cloud scores are advisory; gate.py accepts offline evidence only.")
        return 0
    except Exception as exc:
        print("Cloud evaluation failed: " + type(exc).__name__ + ": " + str(exc))
        print("Retain the output and remote IDs. No evaluation/run is deleted or canceled automatically.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
