from .checks import evaluate_record
from .common import REPORT_SCHEMA, assert_finite, implementation_digest, nonempty, number
from .data import load_inputs
from .results import summarize


def validate_report(report, expected_candidate=None, enforce_thresholds=True):
    """Verify trusted inputs, every required result, and recomputed aggregates."""
    failures = []
    try:
        assert_finite(report)
        if not isinstance(report, dict):
            raise ValueError("Report must be an object")
        if report.get("schema_version") != REPORT_SCHEMA or report.get("kind") != "offline-deterministic":
            raise ValueError("Unsupported report contract; cloud evidence is not an offline gate input")
        if report.get("status") != "completed":
            raise ValueError("Run is missing, incomplete or errored")
        for key in ("run_id", "started_at", "completed_at"):
            if not nonempty(report.get(key)):
                raise ValueError("Missing run identity or timestamps")
        provenance = report.get("provenance", {})
        policy, cases, fixtures, trusted = load_inputs()
        candidate = provenance.get("candidate")
        if candidate not in policy["candidates"] or (expected_candidate is not None and candidate != expected_candidate):
            raise ValueError("Wrong or unregistered candidate")
        version = policy["candidates"][candidate]
        if provenance.get("expected_version") != version or provenance.get("actual_versions") != [version]:
            raise ValueError("Missing or wrong version attribution")
        for field in ("dataset", "fixtures", "policy"):
            if provenance.get(field) != trusted[field]:
                raise ValueError("Wrong, stale or incomplete " + field + " provenance")
        if provenance.get("implementation_sha256") != implementation_digest():
            raise ValueError("Evidence was not produced by this implementation revision")
        required = list(policy["evaluators"])
        if report.get("required_evaluators") != required:
            raise ValueError("Required evaluator set is incomplete or unexpected")
        count = len(cases)
        for key in ("expected_item_count", "evaluated_item_count"):
            if type(report.get(key)) is not int or report[key] != count or count == 0:
                raise ValueError("Missing or incomplete item coverage")
        items = report.get("items")
        if not isinstance(items, list) or len(items) != count:
            raise ValueError("Per-item evidence is missing or incomplete")
        ids = [item.get("item_id") for item in items if isinstance(item, dict)]
        if len(ids) != count or len(set(ids)) != count or set(ids) != {case["id"] for case in cases}:
            raise ValueError("Duplicate, missing or unknown case IDs")
        cases_by_id = {case["id"]: case for case in cases}
        for item in items:
            item_id = item["item_id"]
            case = cases_by_id[item_id]
            if item.get("status") != "completed" or item.get("error") is not None:
                raise ValueError(item_id + ": item skipped, incomplete or errored")
            for key in ("query", "tags", "expected"):
                if item.get(key) != case[key]:
                    raise ValueError(item_id + ": oracle/query/tags differ from the trusted dataset")
            record = item.get("record")
            if not isinstance(record, dict) or record.get("actual_version") != version:
                raise ValueError(item_id + ": missing or wrong observed actual_version")
            evaluations = item.get("evaluations", {})
            if set(evaluations) != set(required):
                raise ValueError(item_id + ": every required evaluator must run")
            recomputed = evaluate_record(record, case, fixtures)
            for name in required:
                result = evaluations[name]
                if not isinstance(result, dict):
                    raise ValueError(item_id + "/" + name + ": missing result")
                if (
                    result.get("status") != "completed" or result.get("error")
                    or not number(result.get("score")) or result["score"] not in (0.0, 1.0)
                    or type(result.get("passed")) is not bool or not nonempty(result.get("reason"))
                ):
                    raise ValueError(item_id + "/" + name + ": skipped, errored or invalid result")
                if result != recomputed[name]:
                    raise ValueError(item_id + "/" + name + ": result disagrees with recorded evidence")
        summary = report.get("summary", {})
        if set(summary) != set(required):
            raise ValueError("All required evaluator aggregates must be present")
        recomputed_summary = summarize(items, required, count)
        for name in required:
            aggregate = summary[name]
            if not isinstance(aggregate, dict):
                raise ValueError(name + ": missing aggregate")
            for field in ("expected", "evaluated", "passed", "failed", "skipped", "errors"):
                value = aggregate.get(field)
                if type(value) is not int or value < 0:
                    raise ValueError(name + ": invalid count " + field)
            if (
                aggregate["expected"] != count or aggregate["evaluated"] != count
                or aggregate["skipped"] != 0 or aggregate["errors"] != 0
                or not number(aggregate.get("pass_rate"))
                or aggregate != recomputed_summary[name]
            ):
                raise ValueError(name + ": missing, inconsistent or incomplete coverage/counts")
            threshold = policy["evaluators"][name]["min_pass_rate"]
            if enforce_thresholds and aggregate["pass_rate"] < threshold:
                failed_ids = [item["item_id"] for item in items if not item["evaluations"][name]["passed"]]
                failures.append(
                    name + ": " + str(aggregate["pass_rate"]) + " < " + str(threshold)
                    + "; failed items: " + ", ".join(failed_ids)
                )
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        failures.append(str(exc))
    return failures
