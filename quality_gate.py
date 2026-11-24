"""Offline, deterministic RAG release gate; no provider calls."""
import argparse
import json
import math
import sys
from pathlib import Path


def normalized(value):
    if not isinstance(value, str):
        raise ValueError("text fields must be strings")
    return " ".join(value.casefold().split())


def strings(value, name, nonempty=False):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{name} must contain nonblank strings")
    if nonempty and not value:
        raise ValueError(f"{name} must not be empty")
    return value


def index_rows(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("input must be a nonempty array")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise ValueError("each row requires a nonblank string id")
        if row["id"] in result:
            raise ValueError(f"duplicate case id: {row['id']}")
        result[row["id"]] = row
    return result


def evaluate(cases, predictions, *, k=3, min_recall=0.90, min_pass_rate=1.0, max_p95_ms=1500):
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    for name, value in (("min_recall", min_recall), ("min_pass_rate", min_pass_rate)):
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be in [0,1]")
    if not math.isfinite(max_p95_ms) or max_p95_ms <= 0:
        raise ValueError("max_p95_ms must be positive and finite")
    references = index_rows(cases)
    actual = index_rows(predictions)
    if references.keys() != actual.keys():
        raise ValueError(f"case mismatch: missing={sorted(references.keys()-actual.keys())}, extra={sorted(actual.keys()-references.keys())}")
    outcomes = []
    latencies = []
    for case_id, case in references.items():
        prediction = actual[case_id]
        expected = set(strings(case.get("expected_sources"), "expected_sources", True))
        retrieved = strings(prediction.get("retrieved_sources"), "retrieved_sources")
        required = strings(case.get("required_phrases"), "required_phrases", True)
        forbidden = strings(case.get("forbidden_phrases", []), "forbidden_phrases")
        answer = normalized(prediction.get("answer"))
        latency = prediction.get("latency_ms")
        if isinstance(latency, bool) or not isinstance(latency, (int, float)) or not math.isfinite(latency) or latency < 0:
            raise ValueError(f"{case_id}: invalid latency_ms")
        latencies.append(latency)
        recall = len(expected.intersection(retrieved[:k])) / len(expected)
        missing = [phrase for phrase in required if normalized(phrase) not in answer]
        blocked = [phrase for phrase in forbidden if normalized(phrase) in answer]
        outcomes.append({
            "id": case_id, "recall_at_k": recall, "missing_phrases": missing,
            "forbidden_matches": blocked, "passed": recall == 1 and not missing and not blocked,
            "latency_ms": latency,
        })
    mean_recall = sum(row["recall_at_k"] for row in outcomes) / len(outcomes)
    pass_rate = sum(row["passed"] for row in outcomes) / len(outcomes)
    p95 = sorted(latencies)[math.ceil(0.95 * len(latencies)) - 1]
    checks = {
        "recall": mean_recall >= min_recall,
        "case_pass_rate": pass_rate >= min_pass_rate,
        "latency": p95 <= max_p95_ms,
        "no_forbidden_matches": not any(row["forbidden_matches"] for row in outcomes),
    }
    return {
        "passed": all(checks.values()), "case_count": len(outcomes), "k": k,
        "mean_recall_at_k": mean_recall, "case_pass_rate": pass_rate,
        "p95_latency_ms": p95, "checks": checks, "cases": outcomes,
        "thresholds": {"min_recall": min_recall, "min_pass_rate": min_pass_rate, "max_p95_ms": max_p95_ms},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--min-recall", type=float, default=0.90)
    parser.add_argument("--min-pass-rate", type=float, default=1.0)
    parser.add_argument("--max-p95-ms", type=float, default=1500)
    args = parser.parse_args(argv)
    try:
        report = evaluate(
            json.loads(args.cases.read_text(encoding="utf-8")),
            json.loads(args.predictions.read_text(encoding="utf-8")),
            k=args.k, min_recall=args.min_recall,
            min_pass_rate=args.min_pass_rate, max_p95_ms=args.max_p95_ms,
        )
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, TypeError) as exc:
        print(f"Invalid evaluation input: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({key: val for key, val in report.items() if key != "cases"}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
