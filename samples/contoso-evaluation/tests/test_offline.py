import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from contoso.app import FixtureTools, run_candidate
from contoso.checks import evaluate_record
from contoso.common import parse_json, read_json
from contoso.data import load_inputs
from contoso.gating import validate_report
from contoso.results import build_report


class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = build_report()

    def assert_rejected(self, mutation):
        report = copy.deepcopy(self.baseline)
        mutation(report)
        self.assertTrue(validate_report(report), "Malformed evidence must not pass")

    def test_baseline_and_regression_detect_real_failures(self):
        self.assertEqual(validate_report(self.baseline), [])
        bad = build_report("regressed")
        self.assertEqual(bad["status"], "completed")
        failures = validate_report(bad)
        self.assertTrue(any("response_assertions" in failure for failure in failures))
        self.assertTrue(any("ticket_state" in failure for failure in failures))
        by_id = {item["item_id"]: item for item in bad["items"]}
        self.assertFalse(by_id["reg-returns"]["evaluations"]["response_assertions"]["passed"])
        self.assertFalse(by_id["reg-order"]["evaluations"]["expected_outcome"]["passed"])
        ticket = by_id["reg-ticket"]
        self.assertEqual(ticket["record"]["state"]["tickets"], [])
        self.assertFalse(ticket["evaluations"]["tool_contract"]["passed"])
        self.assertFalse(ticket["evaluations"]["ticket_state"]["passed"])

    def test_dataset_splits_are_disjoint_and_baseline_runs_all(self):
        sets = []
        for split, count in (("development", 3), ("regression", 8), ("holdout", 3)):
            policy, cases, _, _ = load_inputs(split)
            self.assertEqual(len(cases), count)
            sets.append({case["id"] for case in cases})
            report = build_report(split=split)
            self.assertEqual(report["evaluated_item_count"], count)
            for item in report["items"]:
                self.assertEqual(set(item["evaluations"]), set(policy["evaluators"]))
                self.assertTrue(all(result["passed"] for result in item["evaluations"].values()))
            if split != "regression":
                self.assertTrue(validate_report(report), "A development subset cannot satisfy the release gate")
        self.assertFalse(sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])

    def test_default_split_comes_from_the_central_policy(self):
        def policy_override(path):
            data = read_json(path)
            if path.name == "policy.json":
                data["release_split"] = "development"
            return data

        with patch("contoso.data.read_json", side_effect=policy_override):
            report = build_report()
            self.assertEqual(report["provenance"]["dataset"]["split"], "development")
            self.assertEqual(report["expected_item_count"], 3)
            self.assertEqual(validate_report(report), [])

    def test_empty_missing_and_incomplete_evidence_fails_closed(self):
        for value in ({}, {"summary": {}}, None, [], {"status": "completed"}):
            with self.subTest(value=value):
                self.assertTrue(validate_report(value))
        for field in (
            "schema_version", "status", "provenance", "items", "summary",
            "required_evaluators", "evaluated_item_count", "expected_item_count",
        ):
            with self.subTest(field=field):
                self.assert_rejected(lambda r: r.pop(field))
        self.assert_rejected(lambda r: r.update(items=[]))
        self.assert_rejected(lambda r: r.update(evaluated_item_count=0, expected_item_count=0))
        self.assert_rejected(lambda r: r["items"].pop())
        self.assert_rejected(lambda r: r["items"].append(copy.deepcopy(r["items"][0])))
        self.assert_rejected(lambda r: r["items"][0].update(item_id=r["items"][1]["item_id"]))
        self.assert_rejected(lambda r: r["items"][0]["evaluations"].pop("ticket_state"))
        self.assert_rejected(lambda r: r["summary"].pop("ticket_state"))
        self.assert_rejected(lambda r: r.update(required_evaluators=["response_assertions"]))

    def test_skips_errors_and_nonfinite_results_are_never_success(self):
        for status in ("skipped", "error", "queued", "canceled", None):
            with self.subTest(status=status):
                self.assert_rejected(lambda r: r.update(status=status))
                self.assert_rejected(lambda r: r["items"][0]["evaluations"]["tool_contract"].update(status=status))
        for score in (float("nan"), float("inf"), float("-inf"), None, "1.0", True):
            with self.subTest(score=score):
                self.assert_rejected(lambda r: r["items"][0]["evaluations"]["tool_contract"].update(score=score))
                self.assert_rejected(lambda r: r["summary"]["tool_contract"].update(pass_rate=score))
        for count in (0, 7, 9, -1, True, 8.0, None):
            with self.subTest(count=count):
                self.assert_rejected(lambda r: r["summary"]["ticket_state"].update(evaluated=count))
        self.assert_rejected(lambda r: r["items"][0]["evaluations"]["tool_contract"].update(error="judge failed"))
        self.assert_rejected(lambda r: r["summary"]["tool_contract"].update(skipped=1))
        self.assert_rejected(lambda r: r["summary"]["tool_contract"].update(errors=1))

    def test_versions_are_observed_not_substituted(self):
        self.assertTrue(validate_report(self.baseline, expected_candidate="regressed"))
        for value in (None, "", "contoso-support/unknown", "contoso-support/1.1.0-regressed"):
            with self.subTest(version=value):
                self.assert_rejected(lambda r: r["items"][0]["record"].update(actual_version=value))
                self.assert_rejected(lambda r: r["provenance"].update(expected_version=value))
        self.assert_rejected(lambda r: r["items"][0]["record"].pop("actual_version"))
        self.assert_rejected(lambda r: r["provenance"].pop("actual_versions"))
        records = [copy.deepcopy(item["record"]) for item in self.baseline["items"]]
        records[0].pop("actual_version")
        report = build_report(recordings=records)
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["summary"]["tool_contract"]["errors"], 1)
        self.assertEqual(report["summary"]["tool_contract"]["evaluated"], 7)
        self.assertTrue(validate_report(report))

    def test_aggregate_or_oracle_tampering_does_not_mask_failures(self):
        bad = build_report("regressed")
        bad["summary"] = copy.deepcopy(self.baseline["summary"])
        self.assertTrue(validate_report(bad))
        self.assert_rejected(lambda r: r["items"][0]["expected"]["response_contains"].clear())
        self.assert_rejected(lambda r: r["provenance"]["dataset"].update(sha256="stale"))
        self.assert_rejected(lambda r: r["provenance"].update(implementation_sha256="stale"))
        self.assert_rejected(lambda r: r["items"][0]["record"].update(response="Unused items: 90 days."))

    def test_independent_context_and_fabricated_tool_results_fail(self):
        policy, cases, fixtures, _ = load_inputs()
        case = cases[0]
        record = run_candidate("baseline", case["request"], case["id"], fixtures)
        self.assertTrue(all(result["passed"] for result in evaluate_record(record, case, fixtures).values()))
        record["context"] = [{"source": "response", "id": "self", "content": record["response"]}]
        self.assertFalse(evaluate_record(record, case, fixtures)["fixture_context"]["passed"])
        record["trace"][0]["result"]["documents"][0]["text"] = "Returns are allowed for 90 days."
        self.assertFalse(evaluate_record(record, case, fixtures)["tool_contract"]["passed"])

    def test_tools_enforce_authorization_consent_and_real_ticket_state(self):
        _, _, fixtures, _ = load_inputs()
        tools = FixtureTools(fixtures)
        denied = tools.lookup_order("ORD-2001", "C-001")
        self.assertEqual(denied, {"code": "access_denied"})
        self.assertNotIn("tracking", denied)
        self.assertEqual(tools.create_ticket("ORD-2001", "C-001", "Help", True), denied)
        self.assertEqual(tools.create_ticket("ORD-9999", "C-001", "Help", True), {"code": "not_found"})
        self.assertEqual(tools.create_ticket("ORD-1001", "C-001", "Help", False), {"code": "consent_required"})
        self.assertEqual(tools.tickets, [])
        with self.assertRaises(ValueError):
            tools.create_ticket("ORD-1001", "C-001", "Help", 1)
        created = tools.create_ticket("ORD-1001", "C-001", "Help", True)
        self.assertEqual(created["ticket"], tools.tickets[0])
        self.assertEqual(FixtureTools(fixtures).tickets, [], "No cross-case state leakage")

    def test_external_records_require_exact_ids_and_errors_keep_all_results(self):
        records = [copy.deepcopy(item["record"]) for item in self.baseline["items"]]
        self.assertEqual(validate_report(build_report(recordings=records)), [])
        with self.assertRaises(ValueError):
            build_report(recordings=records[:-1])
        with self.assertRaises(ValueError):
            build_report(recordings=records + [records[0]])
        with patch("contoso.results.run_candidate", side_effect=ValueError("tool failure")):
            report = build_report()
        self.assertEqual(len(report["items"]), 8)
        self.assertEqual(report["summary"]["expected_outcome"]["errors"], 8)
        self.assertEqual(report["summary"]["expected_outcome"]["evaluated"], 0)
        self.assertIsNone(report["summary"]["expected_outcome"]["pass_rate"])
        self.assertTrue(validate_report(report))

    def test_strict_json_rejects_duplicate_keys_nan_and_overflow(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1e999}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_json(text)


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.output = Path("samples/contoso-evaluation/.test-output") / str(uuid.uuid4())
        self.output.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.output)

    def invoke(self, script, *arguments):
        return subprocess.run(
            [sys.executable, str(ROOT / script), *map(str, arguments)],
            text=True, capture_output=True, check=False,
        )

    def test_exact_runner_and_gate_exit_contract(self):
        for candidate, gate_status in (("baseline", 0), ("regressed", 1)):
            with self.subTest(candidate=candidate):
                path = self.output / (candidate + ".json")
                run = self.invoke("run.py", "--candidate", candidate, "--output", path)
                self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
                gate = self.invoke("gate.py", path)
                self.assertEqual(gate.returncode, gate_status, gate.stderr + gate.stdout)
                self.assertEqual(json.loads(gate.stdout)["decision"], "pass" if gate_status == 0 else "fail")
        missing = self.invoke("gate.py", self.output / "missing.json")
        self.assertNotEqual(missing.returncode, 0)

    def test_invalid_input_replaces_stale_success_with_error_evidence(self):
        output = self.output / "result.json"
        self.assertEqual(self.invoke("run.py", "--candidate", "baseline", "--output", output).returncode, 0)
        records = self.output / "invalid-records.json"
        records.write_text('{"incomplete":true}', encoding="utf-8")
        run = self.invoke("run.py", "--candidate", "baseline", "--records", records, "--output", output)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(json.loads(output.read_text())["status"], "error")
        self.assertNotEqual(self.invoke("gate.py", output).returncode, 0)
