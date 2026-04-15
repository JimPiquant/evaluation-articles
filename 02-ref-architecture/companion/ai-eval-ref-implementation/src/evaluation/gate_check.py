"""
Gate Check — Evaluate Pass/Fail from Evaluation Results

Reads evaluation results and determines whether the pipeline gate
should pass or fail based on configured thresholds.

Usage:
    python gate_check.py ./local_eval_results.json
"""

import json
import sys

from evaluator_config import GATE_CRITERIA


def check_gate(results_path: str) -> bool:
    """Check evaluation results against gate criteria.

    Returns True if all gates pass, False if any gate fails.
    """
    with open(results_path) as f:
        results = json.load(f)

    metrics = results.get("metrics", {})
    passed = True

    print("=" * 60)
    print("GATE CHECK RESULTS")
    print("=" * 60)

    for evaluator_name, criteria in GATE_CRITERIA.items():
        if "min_pass_rate" in criteria:
            metric_key = f"{evaluator_name}.pass_rate"
            actual = metrics.get(metric_key)
            if actual is None:
                print(f"  ⚠ {evaluator_name}: metric not found ({metric_key})")
                continue
            threshold = criteria["min_pass_rate"]
            gate_passed = actual >= threshold
            status = "✓" if gate_passed else "✗"
            print(f"  {status} {evaluator_name}: pass_rate={actual:.2%} (threshold={threshold:.0%})")
            if not gate_passed:
                passed = False

        elif "max_defect_rate" in criteria:
            metric_key = f"{evaluator_name}.defect_rate"
            actual = metrics.get(metric_key, 0)
            threshold = criteria["max_defect_rate"]
            gate_passed = actual <= threshold
            status = "✓" if gate_passed else "✗"
            print(f"  {status} {evaluator_name}: defect_rate={actual:.2%} (max={threshold:.0%})")
            if not gate_passed:
                passed = False

        elif "min_average_score" in criteria:
            metric_key = f"{evaluator_name}.score"
            actual = metrics.get(metric_key)
            if actual is None:
                print(f"  ⚠ {evaluator_name}: metric not found ({metric_key})")
                continue
            threshold = criteria["min_average_score"]
            gate_passed = actual >= threshold
            status = "✓" if gate_passed else "✗"
            print(f"  {status} {evaluator_name}: avg_score={actual:.2f} (threshold={threshold:.1f})")
            if not gate_passed:
                passed = False

    print()
    if passed:
        print("✓ ALL GATES PASSED")
    else:
        print("✗ GATE CHECK FAILED — blocking promotion")

    return passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gate_check.py <results_path>")
        sys.exit(1)

    gate_passed = check_gate(sys.argv[1])
    sys.exit(0 if gate_passed else 1)
