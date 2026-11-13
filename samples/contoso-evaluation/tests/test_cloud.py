import copy
from pathlib import Path
import shutil
from types import SimpleNamespace
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from contoso.cloud import execute_cloud, recorded_rows, request_spec, validate_cloud_outputs
from contoso.common import read_json
from contoso.gating import validate_report
from contoso.results import build_report


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def time(self):
        return self.now

    def sleep(self, delay):
        self.now += delay


class FakePage:
    def __init__(self, pages, index=0, fail_next=False):
        self.pages = pages
        self.index = index
        self.data = pages[index]
        self.fail_next = fail_next

    def has_next_page(self):
        return self.index + 1 < len(self.pages)

    def get_next_page(self):
        if self.fail_next:
            raise ConnectionError("second page failed")
        return FakePage(self.pages, self.index + 1)


class FakeClient:
    def __init__(self, rows, statuses=("completed",), fail_next=False):
        self.statuses = list(statuses)
        self.create_calls = 0
        self.run_create_calls = 0
        self.retrieve_calls = 0
        self.run_data = {
            "id": "run-test", "eval_id": "eval-test", "status": "completed",
            "error": None, "report_url": "https://example.invalid/report",
            "result_counts": {"total": len(rows), "passed": len(rows), "failed": 0, "errored": 0},
            "per_testing_criteria_results": [{"testing_criteria": "groundedness", "passed": len(rows), "failed": 0}],
        }
        self.items = [
            {
                "id": "output-" + str(index), "eval_id": "eval-test", "run_id": "run-test",
                "datasource_item": copy.deepcopy(row), "status": "pass",
                "results": [{"name": "groundedness", "score": 4.0, "passed": True, "label": "pass"}],
                "sample": None,
            }
            for index, row in enumerate(rows)
        ]
        pages = [self.items[:4], self.items[4:]]
        self.evals = SimpleNamespace(
            create=self.create,
            runs=SimpleNamespace(
                create=self.create_run, retrieve=self.retrieve,
                output_items=SimpleNamespace(list=lambda **kwargs: FakePage(pages, fail_next=fail_next)),
            ),
        )

    def create(self, **kwargs):
        self.create_calls += 1
        self.request = kwargs
        return {"id": "eval-test"}

    def create_run(self, **kwargs):
        self.run_create_calls += 1
        return {**self.run_data, "status": "queued"}

    def retrieve(self, **kwargs):
        self.retrieve_calls += 1
        status = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
        return {**self.run_data, "status": status}


class CloudLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.report = build_report()
        self.rows = recorded_rows(self.report)
        self.workspace = Path("samples/contoso-evaluation/.test-output") / str(uuid.uuid4())
        self.workspace.mkdir(parents=True)
        self.output = self.workspace / "cloud.json"

    def tearDown(self):
        shutil.rmtree(self.workspace)

    def execute(self, client, **kwargs):
        return execute_cloud(
            client, self.report, "recording-digest", self.output, "judge-test",
            packages={"test-package": "1"}, environment={"project_endpoint": "https://example.invalid/api/projects/test"},
            **kwargs,
        )

    def evidence(self, client):
        return {
            "eval_id": "eval-test", "run_id": "run-test",
            "raw_run": copy.deepcopy(client.run_data),
            "raw_output_items": copy.deepcopy(client.items),
        }

    def test_all_pages_and_all_required_counts_are_retained(self):
        client = FakeClient(self.rows, statuses=("queued", "in_progress", "completed"))
        clock = FakeClock()
        result = self.execute(client, clock=clock.time, sleep=clock.sleep)
        saved = read_json(self.output)
        self.assertEqual(saved, result)
        self.assertEqual(result["eval_id"], "eval-test")
        self.assertEqual(result["run_id"], "run-test")
        self.assertEqual(result["pages_retrieved"], 2)
        self.assertEqual(len(result["raw_output_items"]), 8)
        self.assertTrue(result["all_results_retrieved"])
        self.assertEqual(result["summary"]["groundedness"]["evaluated"], 8)
        self.assertTrue(validate_report(result), "Cloud scores cannot masquerade as an offline gate result")
        self.assertEqual(client.run_create_calls, 1)

    def test_timeout_is_bounded_retains_ids_and_resume_does_not_resubmit(self):
        client = FakeClient(self.rows, statuses=("in_progress",))
        clock = FakeClock()
        with self.assertRaises(TimeoutError):
            self.execute(client, timeout=10, poll_interval=5, clock=clock.time, sleep=clock.sleep)
        saved = read_json(self.output)
        self.assertEqual(clock.now, 10)
        self.assertEqual(client.retrieve_calls, 2)
        self.assertEqual(saved["eval_id"], "eval-test")
        self.assertEqual(saved["run_id"], "run-test")
        self.assertFalse(saved["all_results_retrieved"])
        self.assertEqual(saved["packages"], {"test-package": "1"})
        resumed = FakeClient(self.rows)
        result = self.execute(resumed, resume=saved)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(resumed.create_calls, 0)
        self.assertEqual(resumed.run_create_calls, 0)
        self.assertEqual(len(result["previous_attempts"]), 1)
        self.assertEqual(result["previous_attempts"][0]["status"], "error")

    def test_failed_canceled_and_unknown_status_never_succeed(self):
        for status in ("failed", "canceled", "cancelled", "skipped", "unexpected"):
            with self.subTest(status=status):
                client = FakeClient(self.rows, statuses=(status,))
                with self.assertRaises((RuntimeError, ValueError)):
                    self.execute(client)
                saved = read_json(self.output)
                self.assertEqual(saved["status"], "error")
                self.assertEqual(saved["run_id"], "run-test")
                self.assertIsNone(saved["summary"])
                self.assertEqual(saved["raw_run"]["status"], status)

    def test_page_failure_preserves_first_page_and_is_not_complete(self):
        client = FakeClient(self.rows, fail_next=True)
        with self.assertRaises(ConnectionError):
            self.execute(client)
        saved = read_json(self.output)
        self.assertEqual(saved["status"], "error")
        self.assertEqual(len(saved["raw_output_items"]), 4)
        self.assertEqual(saved["pages_retrieved"], 1)
        self.assertFalse(saved["all_results_retrieved"])
        self.assertIsNone(saved["summary"])

    def test_recorded_response_not_ground_truth_or_self_context_is_sent(self):
        bad = build_report("regressed")
        rows = recorded_rows(bad)
        first = rows[0]
        self.assertIn("90 days", first["response"])
        self.assertIn("30 days", first["context"])
        self.assertNotEqual(first["response"], first["context"])
        spec = request_spec(rows, "judge-test")
        self.assertEqual(spec["testing_criteria"][0]["initialization_parameters"], {"deployment_name": "judge-test"})
        self.assertEqual(spec["data_source"]["type"], "jsonl")
        self.assertNotIn("model", spec["data_source"], "This is not a live application target")

    def test_missing_duplicate_errors_skips_nan_and_wrong_version_fail_closed(self):
        client = FakeClient(self.rows)
        mutations = [
            lambda e: e["raw_output_items"].pop(),
            lambda e: e["raw_output_items"].clear(),
            lambda e: e["raw_output_items"][0].update(status="skipped"),
            lambda e: e["raw_output_items"][0].update(error={"message": "failed"}),
            lambda e: e["raw_output_items"][0]["results"].clear(),
            lambda e: e["raw_output_items"][0]["results"][0].update(score=None),
            lambda e: e["raw_output_items"][0]["results"][0].update(score=float("nan")),
            lambda e: e["raw_output_items"][0]["results"][0].update(score=True),
            lambda e: e["raw_output_items"][0]["results"][0].update(passed=None),
            lambda e: e["raw_output_items"][0]["results"][0].update(status="skipped"),
            lambda e: e["raw_output_items"][0]["results"][0].update(error={"message": "failed"}),
            lambda e: e["raw_output_items"][0]["datasource_item"].pop("actual_version"),
            lambda e: e["raw_output_items"][0]["datasource_item"].update(actual_version="wrong"),
            lambda e: e["raw_output_items"][0].update(datasource_item=copy.deepcopy(e["raw_output_items"][1]["datasource_item"])),
            lambda e: e["raw_output_items"][0].update(eval_id="wrong"),
            lambda e: e["raw_run"]["result_counts"].pop("errored"),
            lambda e: e["raw_run"]["result_counts"].update(errored=1),
            lambda e: e["raw_run"]["result_counts"].update(total=0),
            lambda e: e["raw_run"]["per_testing_criteria_results"].clear(),
            lambda e: e["raw_run"]["per_testing_criteria_results"][0].update(passed=7),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index):
                evidence = self.evidence(client)
                mutation(evidence)
                with self.assertRaises(ValueError):
                    validate_cloud_outputs(evidence, self.rows)

    def test_failed_quality_label_is_advisory_not_a_completion_error(self):
        client = FakeClient(self.rows)
        client.items[0]["status"] = "fail"
        client.items[0]["results"][0].update(score=1.0, passed=False, label="fail")
        client.run_data["result_counts"].update(passed=7, failed=1)
        client.run_data["per_testing_criteria_results"][0].update(passed=7, failed=1)
        result = self.execute(client)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["summary"]["groundedness"]["failed"], 1)
        self.assertEqual(result["summary"]["groundedness"]["pass_rate"], 7 / 8)

    def test_evaluation_id_survives_run_creation_transport_failure(self):
        client = FakeClient(self.rows)

        def failure(**kwargs):
            raise ConnectionError("run creation failed")

        client.evals.runs.create = failure
        with self.assertRaises(ConnectionError):
            self.execute(client)
        saved = read_json(self.output)
        self.assertEqual(saved["eval_id"], "eval-test")
        self.assertIsNone(saved["run_id"])
        self.assertEqual(saved["status"], "error")

    def test_invalid_polling_configuration_never_submits(self):
        for value in (0, -1, float("nan"), float("inf")):
            with self.subTest(value=value):
                client = FakeClient(self.rows)
                with self.assertRaises(ValueError):
                    self.execute(client, timeout=value)
                self.assertEqual(client.create_calls, 0)
                with self.assertRaises(ValueError):
                    self.execute(client, poll_interval=value)
                self.assertEqual(client.create_calls, 0)

    def test_resume_rejects_wrong_input_without_overwriting_evidence(self):
        client = FakeClient(self.rows)
        result = self.execute(client)
        mismatched = copy.deepcopy(result)
        mismatched["input_sha256"] = "wrong"
        with self.assertRaises(ValueError):
            self.execute(FakeClient(self.rows), resume=mismatched)
        self.assertEqual(read_json(self.output), result)
