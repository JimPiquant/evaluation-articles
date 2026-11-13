import copy
import inspect
import json
from importlib.metadata import version
import time

from .common import ROOT, assert_finite, nonempty, number, read_json, write_json
from .gating import validate_report
from .results import timestamp


CLOUD_SCHEMA = "contoso.cloud-evaluation/1"
CRITERIA = ["groundedness"]


def recorded_rows(report):
    failures = validate_report(report, enforce_thresholds=False)
    if failures:
        raise ValueError("Invalid offline recording contract: " + "; ".join(failures))
    return [
        {
            "item_id": item["item_id"],
            "query": item["query"],
            "response": item["record"]["response"],
            "context": json.dumps(item["record"]["context"], sort_keys=True, ensure_ascii=False),
            "actual_version": item["record"]["actual_version"],
        }
        for item in report["items"]
    ]


def request_spec(rows, judge_deployment):
    if not nonempty(judge_deployment):
        raise ValueError("An explicit judge deployment is required")
    fields = ("item_id", "query", "response", "context", "actual_version")
    return {
        "data_source_config": {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {key: {"type": "string"} for key in fields},
                "required": list(fields),
            },
            "include_sample_schema": False,
        },
        "testing_criteria": [{
            "type": "azure_ai_evaluator",
            "name": "groundedness",
            "evaluator_name": "builtin.groundedness",
            "initialization_parameters": {"deployment_name": judge_deployment},
            "data_mapping": {
                "query": "{{item.query}}", "response": "{{item.response}}",
                "context": "{{item.context}}",
            },
        }],
        "data_source": {
            "type": "jsonl",
            "source": {"type": "file_content", "content": [{"item": row} for row in rows]},
        },
    }


def sdk_request(spec):
    # Imports stay optional: offline evaluation and mocked lifecycle tests need no SDK.
    from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
    from openai.types.eval_create_params import DataSourceConfigCustom
    from openai.types.evals.create_eval_jsonl_run_data_source_param import (
        CreateEvalJSONLRunDataSourceParam, SourceFileContent, SourceFileContentContent,
    )

    return {
        "data_source_config": DataSourceConfigCustom(**spec["data_source_config"]),
        "testing_criteria": [TestingCriterionAzureAIEvaluator(**criterion) for criterion in spec["testing_criteria"]],
        "data_source": CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[SourceFileContentContent(**item) for item in spec["data_source"]["source"]["content"]],
            ),
        ),
    }


def installed_packages():
    pins = {}
    for line in (ROOT / "requirements-cloud.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            package, expected_version = line.split("==")
            observed = version(package)
            if observed != expected_version:
                raise ValueError(package + ": expected tested pin " + expected_version + ", installed " + observed)
            pins[package] = observed
    return pins


def sdk_smoke():
    packages = installed_packages()
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from openai.resources.evals.evals import Evals
    from openai.resources.evals.runs.runs import Runs
    from openai.resources.evals.runs.output_items import OutputItems

    if not callable(AIProjectClient.get_openai_client) or not callable(DefaultAzureCredential):
        raise ValueError("Missing project client or credential type")
    for cls, method, required in (
        (Evals, "create", {"data_source_config", "testing_criteria"}),
        (Runs, "create", {"eval_id", "data_source"}),
        (Runs, "retrieve", {"eval_id", "run_id", "timeout"}),
        (OutputItems, "list", {"eval_id", "run_id", "timeout"}),
    ):
        if not required.issubset(inspect.signature(getattr(cls, method)).parameters):
            raise ValueError("Incompatible API signature: " + cls.__name__ + "." + method)
    spec = request_spec([{
        "item_id": "smoke", "query": "Policy?", "response": "30 days.",
        "context": "Fixture policy allows 30 days.", "actual_version": "smoke/1",
    }], "offline-smoke-judge")
    if sdk_request(spec) != spec:
        raise ValueError("SDK request types changed the expected wire shape")
    transport = sdk_transport_smoke()
    return {
        "status": "passed", "packages": packages,
        "mock_transport": transport,
        "validation": "imports, signatures, request types and mock HTTP pagination; no credentials or network calls",
    }


def sdk_transport_smoke():
    import httpx
    from openai import OpenAI

    rows = [
        {
            "item_id": "smoke-" + str(index), "query": "Return policy?",
            "response": "30 days.", "context": "The fixture return window is 30 days.",
            "actual_version": "smoke/1",
        }
        for index in range(2)
    ]
    spec = sdk_request(request_spec(rows, "offline-smoke-judge"))
    run_data = {
        "id": "run-smoke", "eval_id": "eval-smoke", "status": "completed",
        "result_counts": {"total": 2, "passed": 2, "failed": 0, "errored": 0},
        "per_testing_criteria_results": [{"testing_criteria": "groundedness", "passed": 2, "failed": 0}],
        "error": None, "report_url": "https://example.invalid/report",
    }
    items = [
        {
            "id": "output-" + str(index), "eval_id": "eval-smoke", "run_id": "run-smoke",
            "datasource_item": row, "datasource_item_id": index,
            "status": "pass", "sample": None,
            "results": [{"name": "groundedness", "score": 4.0, "passed": True, "label": "pass"}],
        }
        for index, row in enumerate(rows)
    ]
    requests = []

    def handle(request):
        requests.append((request.method, request.url.path))
        if request.method == "POST" and request.url.path == "/v1/evals":
            body = json.loads(request.content)
            if body["testing_criteria"] != spec["testing_criteria"]:
                raise ValueError("SDK transformed the evaluator wire shape")
            return httpx.Response(200, json={"id": "eval-smoke", **body})
        if request.method == "POST" and request.url.path == "/v1/evals/eval-smoke/runs":
            if json.loads(request.content)["data_source"] != spec["data_source"]:
                raise ValueError("SDK transformed the inline source wire shape")
            return httpx.Response(200, json=run_data)
        if request.method == "GET" and request.url.path == "/v1/evals/eval-smoke/runs/run-smoke":
            return httpx.Response(200, json=run_data)
        if request.method == "GET" and request.url.path == "/v1/evals/eval-smoke/runs/run-smoke/output_items":
            second_page = request.url.params.get("after") == "output-0"
            index = 1 if second_page else 0
            return httpx.Response(200, json={
                "object": "list", "data": [items[index]], "has_more": not second_page,
                "first_id": items[index]["id"], "last_id": items[index]["id"],
            })
        raise ValueError("Unexpected mock request")

    with (
        httpx.Client(transport=httpx.MockTransport(handle), trust_env=False) as transport,
        OpenAI(
            api_key="offline-smoke-not-a-credential", base_url="https://example.invalid/v1",
            http_client=transport, max_retries=0, timeout=1.0,
        ) as client,
    ):
        evaluation = client.evals.create(
            data_source_config=spec["data_source_config"], testing_criteria=spec["testing_criteria"],
        )
        run = client.evals.runs.create(eval_id=evaluation.id, data_source=spec["data_source"])
        run = client.evals.runs.retrieve(eval_id=evaluation.id, run_id=run.id)
        page = client.evals.runs.output_items.list(eval_id=evaluation.id, run_id=run.id)
        output_items = [as_data(item) for item in page]
        evidence = {
            "eval_id": evaluation.id, "run_id": run.id,
            "raw_run": as_data(run), "raw_output_items": output_items,
        }
        validate_cloud_outputs(evidence, rows)
    if len(output_items) != 2 or len(requests) != 5:
        raise ValueError("SDK smoke did not retrieve both pages")
    return {"requests": len(requests), "output_items": len(output_items), "pages": 2}


def as_data(value):
    if isinstance(value, dict):
        data = copy.deepcopy(value)
    else:
        data = value.model_dump(mode="json")
    assert_finite(data)
    return data


def validate_cloud_outputs(evidence, rows):
    assert_finite(evidence)
    expected = {row["item_id"]: row for row in rows}
    items = evidence["raw_output_items"]
    if not expected or len(items) != len(expected):
        raise ValueError("Cloud item coverage is zero or incomplete")
    seen = set()
    output_ids = set()
    results_by_criterion = {name: [] for name in CRITERIA}
    row_passes = []
    for item in items:
        if not isinstance(item, dict) or not nonempty(item.get("id")) or item["id"] in output_ids:
            raise ValueError("Missing or duplicate cloud output item ID")
        output_ids.add(item["id"])
        if item.get("eval_id") != evidence["eval_id"] or item.get("run_id") != evidence["run_id"]:
            raise ValueError("Cloud result belongs to a different evaluation/run")
        if item.get("status") not in ("pass", "fail") or item.get("error"):
            raise ValueError("Cloud output item is skipped, errored or incomplete")
        sample = item.get("sample")
        if isinstance(sample, dict) and sample.get("error"):
            raise ValueError("Cloud sample has an error")
        source = item.get("datasource_item", {})
        # Accept a direct item or the explicit inline-source envelope, not an index-based guess.
        if isinstance(source, dict) and set(source) == {"item"}:
            source = source["item"]
        item_id = source.get("item_id") if isinstance(source, dict) else None
        if item_id not in expected or item_id in seen:
            raise ValueError("Unknown, duplicate or unattributed cloud source item")
        seen.add(item_id)
        if any(source.get(key) != value for key, value in expected[item_id].items()):
            raise ValueError(item_id + ": cloud data/version differs from the submitted recording")
        results = item.get("results")
        if not isinstance(results, list) or len(results) != len(CRITERIA):
            raise ValueError(item_id + ": missing required evaluator results")
        names = [result.get("name") for result in results if isinstance(result, dict)]
        if len(names) != len(CRITERIA) or set(names) != set(CRITERIA):
            raise ValueError(item_id + ": wrong or skipped evaluator set")
        for result in results:
            if (
                result.get("error") or result.get("skipped")
                or result.get("status") not in (None, "completed", "pass", "fail")
                or not number(result.get("score")) or not 1 <= result["score"] <= 5
                or type(result.get("passed")) is not bool
            ):
                raise ValueError(item_id + ": invalid, skipped or errored groundedness result")
            if result.get("label") not in (None, "pass" if result["passed"] else "fail"):
                raise ValueError(item_id + ": inconsistent evaluator label")
            if result.get("status") in ("pass", "fail") and result["status"] != ("pass" if result["passed"] else "fail"):
                raise ValueError(item_id + ": inconsistent evaluator status")
            results_by_criterion[result["name"]].append(result["passed"])
        passed = all(result["passed"] for result in results)
        if item["status"] != ("pass" if passed else "fail"):
            raise ValueError(item_id + ": output-item status disagrees with evaluator results")
        row_passes.append(passed)
    if seen != set(expected):
        raise ValueError("Cloud results do not cover every submitted case")
    run = evidence["raw_run"]
    counts = run.get("result_counts", {})
    for key in ("total", "passed", "failed", "errored"):
        if type(counts.get(key)) is not int or counts[key] < 0:
            raise ValueError("Missing or invalid cloud run count: " + key)
    if counts != {
        "total": len(rows), "passed": sum(row_passes),
        "failed": len(rows) - sum(row_passes), "errored": 0,
    }:
        raise ValueError("Cloud run counts disagree with per-item evidence")
    aggregate_rows = run.get("per_testing_criteria_results")
    if not isinstance(aggregate_rows, list) or len(aggregate_rows) != len(CRITERIA):
        raise ValueError("Missing all-required cloud evaluator counts")
    aggregate_names = set()
    summary = {}
    for aggregate in aggregate_rows:
        name = aggregate.get("testing_criteria") or aggregate.get("name")
        if name not in results_by_criterion or name in aggregate_names:
            raise ValueError("Duplicate or unknown cloud evaluator aggregate")
        aggregate_names.add(name)
        if aggregate.get("testing_criteria") and aggregate.get("name") and aggregate["testing_criteria"] != aggregate["name"]:
            raise ValueError("Conflicting cloud evaluator aggregate names")
        passed = sum(results_by_criterion[name])
        failed = len(rows) - passed
        if (
            type(aggregate.get("passed")) is not int or type(aggregate.get("failed")) is not int
            or aggregate["passed"] != passed or aggregate["failed"] != failed
            or aggregate.get("skipped", 0) != 0 or aggregate.get("errors", 0) != 0
            or aggregate.get("errored", 0) != 0
        ):
            raise ValueError("Cloud evaluator counts disagree with detailed results")
        for field in ("skipped", "errors", "errored"):
            if field in aggregate and (type(aggregate[field]) is not int or aggregate[field] != 0):
                raise ValueError("Cloud evaluator reports skipped/errored items or invalid counts")
        summary[name] = {
            "expected": len(rows), "evaluated": len(rows), "passed": passed, "failed": failed,
            "skipped": 0, "errors": 0, "pass_rate": passed / len(rows),
        }
    return summary


def execute_cloud(
    client, report, input_sha256, output, judge_deployment, timeout=600.0,
    poll_interval=5.0, resume=None, clock=time.monotonic, sleep=time.sleep, typed_spec=None,
    packages=None, environment=None,
):
    rows = recorded_rows(report)
    if not number(timeout) or timeout <= 0 or not number(poll_interval) or poll_interval <= 0:
        raise ValueError("Polling timeout and interval must be finite positive numbers")
    spec = request_spec(rows, judge_deployment)
    metadata = {
        "candidate": report["provenance"]["candidate"],
        "actual_version": report["provenance"]["actual_versions"][0],
        "dataset_sha256": report["provenance"]["dataset"]["sha256"],
        "recording_sha256": input_sha256,
    }
    evidence = {
        "schema_version": CLOUD_SCHEMA, "kind": "cloud-recorded-output-advisory",
        "status": "preparing", "started_at": timestamp(),
        "input_sha256": input_sha256, "metadata": metadata,
        "request": spec, "eval_id": None, "run_id": None,
        "raw_evaluation": None, "raw_run": None, "raw_output_items": [],
        "pages_retrieved": 0, "all_results_retrieved": False,
        "summary": None, "error": None,
        "packages": packages, "environment": environment,
        "implementation_validation": "imports/types/mock-transport; not live-cloud-validated",
    }
    if resume is not None:
        if (
            resume.get("schema_version") != CLOUD_SCHEMA or resume.get("input_sha256") != input_sha256
            or resume.get("metadata") != metadata or resume.get("request") != spec
            or resume.get("environment") != environment
            or not nonempty(resume.get("eval_id")) or not nonempty(resume.get("run_id"))
        ):
            raise ValueError("Resume requires matching input, request, evaluation ID and run ID")
        previous = {key: value for key, value in resume.items() if key != "previous_attempts"}
        evidence["previous_attempts"] = resume.get("previous_attempts", []) + [previous]
        for key in ("eval_id", "run_id", "raw_evaluation"):
            evidence[key] = resume[key]
    write_json(output, evidence)
    deadline = clock() + timeout

    def remaining():
        left = deadline - clock()
        if left <= 0:
            raise TimeoutError("Cloud deadline reached; the remote run is retained and may still incur cost")
        return min(30.0, left)

    try:
        request = typed_spec or spec
        if resume is None:
            evaluation = client.evals.create(
                name="contoso-recorded-outputs", metadata=metadata,
                data_source_config=request["data_source_config"],
                testing_criteria=request["testing_criteria"], timeout=remaining(),
            )
            evidence["eval_id"] = evaluation.get("id") if isinstance(evaluation, dict) else getattr(evaluation, "id", None)
            write_json(output, evidence)
            evidence["raw_evaluation"] = as_data(evaluation)
            evidence["eval_id"] = evidence["raw_evaluation"].get("id")
            if not nonempty(evidence["eval_id"]):
                raise ValueError("Cloud evaluation creation did not return an ID")
            evidence["status"] = "evaluation-created"
            write_json(output, evidence)
            run = client.evals.runs.create(
                eval_id=evidence["eval_id"], name="contoso-recorded-run",
                metadata=metadata, data_source=request["data_source"], timeout=remaining(),
            )
            evidence["run_id"] = run.get("id") if isinstance(run, dict) else getattr(run, "id", None)
            write_json(output, evidence)
            evidence["raw_run"] = as_data(run)
            evidence["run_id"] = evidence["raw_run"].get("id")
            if not nonempty(evidence["run_id"]):
                raise ValueError("Cloud run creation did not return an ID")
            evidence["status"] = "submitted"
            write_json(output, evidence)
        while True:
            run = client.evals.runs.retrieve(
                eval_id=evidence["eval_id"], run_id=evidence["run_id"], timeout=remaining(),
            )
            raw_run = as_data(run)
            if raw_run.get("id") != evidence["run_id"] or raw_run.get("eval_id") != evidence["eval_id"]:
                raise ValueError("Cloud retrieval returned the wrong evaluation/run")
            evidence["raw_run"] = raw_run
            evidence["status"] = raw_run.get("status")
            write_json(output, evidence)
            if evidence["status"] in ("completed", "failed", "canceled", "cancelled"):
                break
            if evidence["status"] not in ("queued", "in_progress"):
                raise ValueError("Unknown cloud run status: " + str(evidence["status"]))
            sleep(min(poll_interval, remaining()))
        page = client.evals.runs.output_items.list(
            eval_id=evidence["eval_id"], run_id=evidence["run_id"],
            order="asc", limit=100, timeout=remaining(),
        )
        page_signatures = set()
        while True:
            remaining()
            page_items = [as_data(item) for item in page.data]
            signature = tuple(item.get("id") for item in page_items)
            evidence["raw_output_items"].extend(page_items)
            evidence["pages_retrieved"] += 1
            write_json(output, evidence)
            if signature in page_signatures and page.has_next_page():
                raise ValueError("Cloud pagination repeated a page")
            page_signatures.add(signature)
            if not page.has_next_page():
                break
            remaining()
            page = page.get_next_page()
        evidence["all_results_retrieved"] = True
        write_json(output, evidence)
        if evidence["status"] != "completed" or evidence["raw_run"].get("error"):
            raise RuntimeError("Cloud run ended in " + str(evidence["status"]) + "; inspect raw_run.error")
        evidence["summary"] = validate_cloud_outputs(evidence, rows)
        evidence["completed_at"] = timestamp()
        write_json(output, evidence)
        return evidence
    except Exception as exc:
        # Preserve IDs and partial pages on transport, service, schema or timeout failures.
        evidence["status"] = "error"
        evidence["error"] = type(exc).__name__ + ": " + str(exc)
        evidence["completed_at"] = timestamp()
        write_json(output, evidence)
        raise
