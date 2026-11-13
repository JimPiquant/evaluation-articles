import copy
import uuid
from datetime import datetime, timezone

from .app import run_candidate
from .checks import evaluate_record
from .common import REPORT_SCHEMA, implementation_digest
from .data import load_inputs


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def summarize(items, evaluator_names, expected_count):
    summary = {}
    for name in evaluator_names:
        results = [item.get("evaluations", {}).get(name, {}) for item in items]
        evaluated = sum(result.get("status") == "completed" for result in results)
        passed = sum(result.get("status") == "completed" and result.get("passed") is True for result in results)
        failed = evaluated - passed
        skipped = sum(result.get("status") == "skipped" for result in results)
        errors = len(results) - evaluated - skipped
        summary[name] = {
            "expected": expected_count, "evaluated": evaluated, "passed": passed,
            "failed": failed, "skipped": skipped, "errors": errors,
            "pass_rate": passed / evaluated if evaluated else None,
        }
    return summary


def build_report(candidate="baseline", split=None, recordings=None):
    policy, cases, fixtures, provenance = load_inputs(split)
    if candidate not in policy["candidates"]:
        raise ValueError("Candidate must be registered with an explicit version in policy.json")
    if recordings is not None:
        if not isinstance(recordings, list):
            raise ValueError("Recordings must be a JSON array")
        ids = [record.get("item_id") for record in recordings if isinstance(record, dict)]
        if len(ids) != len(recordings) or len(set(ids)) != len(ids) or set(ids) != {case["id"] for case in cases}:
            raise ValueError("Recordings must cover every selected case exactly once")
        by_id = {record["item_id"]: record for record in recordings}
    started = timestamp()
    items = []
    evaluator_names = list(policy["evaluators"])
    for case in cases:
        item = {
            "item_id": case["id"], "query": case["query"], "tags": case["tags"],
            "expected": copy.deepcopy(case["expected"]),
            "status": "error", "error": None, "record": None, "evaluations": {},
        }
        try:
            record = (
                copy.deepcopy(by_id[case["id"]]) if recordings is not None
                else run_candidate(candidate, case["request"], case["id"], fixtures)
            )
            item["record"] = record
            if record.get("actual_version") != policy["candidates"][candidate]:
                raise ValueError("Missing or wrong observed actual_version")
            item["evaluations"] = evaluate_record(record, case, fixtures)
            item["status"] = "completed"
        except (ValueError, TypeError, KeyError) as exc:
            item["error"] = str(exc)
            item["evaluations"] = {
                name: {"status": "error", "score": None, "passed": None, "reason": str(exc)}
                for name in evaluator_names
            }
        items.append(item)
    provenance.update({
        "candidate": candidate,
        "expected_version": policy["candidates"][candidate],
        "actual_versions": sorted({
            item["record"]["actual_version"] for item in items
            if isinstance(item.get("record"), dict) and isinstance(item["record"].get("actual_version"), str)
        }),
        "implementation_sha256": implementation_digest(),
    })
    completed = sum(item["status"] == "completed" for item in items)
    return {
        "schema_version": REPORT_SCHEMA,
        "kind": "offline-deterministic",
        "run_id": str(uuid.uuid4()),
        "status": "completed" if completed == len(cases) else "error",
        "started_at": started, "completed_at": timestamp(),
        "provenance": provenance,
        "required_evaluators": evaluator_names,
        "expected_item_count": len(cases),
        "evaluated_item_count": completed,
        "items": items,
        "summary": summarize(items, evaluator_names, len(cases)),
    }
