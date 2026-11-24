import copy
import json
import tempfile
import unittest
from pathlib import Path

from quality_gate import evaluate, main

CASES = [
    {"id": "a", "expected_sources": ["handbook"], "required_phrases": ["30 days"], "forbidden_phrases": ["unlimited"]},
    {"id": "b", "expected_sources": ["policy", "faq"], "required_phrases": ["manager approval"]},
]
GOOD = [
    {"id": "a", "retrieved_sources": ["handbook"], "answer": "Within 30 DAYS.", "latency_ms": 100},
    {"id": "b", "retrieved_sources": ["policy", "faq"], "answer": "Requires manager approval.", "latency_ms": 200},
]


class GateTests(unittest.TestCase):
    def test_success(self):
        report = evaluate(CASES, GOOD)
        self.assertTrue(report["passed"])
        self.assertEqual(report["mean_recall_at_k"], 1)
        self.assertEqual(report["p95_latency_ms"], 200)

    def test_retrieval_regression(self):
        bad = copy.deepcopy(GOOD)
        bad[1]["retrieved_sources"] = ["policy", "other", "other", "faq"]
        report = evaluate(CASES, bad)
        self.assertFalse(report["passed"])
        self.assertEqual(report["mean_recall_at_k"], 0.75)

    def test_duplicate_sources_do_not_inflate_recall(self):
        bad = copy.deepcopy(GOOD)
        bad[1]["retrieved_sources"] = ["policy", "policy", "policy"]
        self.assertEqual(evaluate(CASES, bad)["mean_recall_at_k"], 0.75)

    def test_required_phrase_missing(self):
        bad = copy.deepcopy(GOOD)
        bad[0]["answer"] = "Not specified"
        self.assertFalse(evaluate(CASES, bad)["checks"]["case_pass_rate"])

    def test_forbidden_phrase_always_blocks(self):
        bad = copy.deepcopy(GOOD)
        bad[0]["answer"] = "30 days or unlimited"
        self.assertFalse(evaluate(CASES, bad, min_pass_rate=0)["passed"])

    def test_latency_regression(self):
        bad = copy.deepcopy(GOOD)
        bad[1]["latency_ms"] = 1501
        self.assertFalse(evaluate(CASES, bad)["checks"]["latency"])

    def test_case_mismatch(self):
        with self.assertRaises(ValueError):
            evaluate(CASES, GOOD[:1])

    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):
            evaluate(CASES, GOOD + GOOD[:1])

    def test_invalid_latencies(self):
        for value in (-1, float("nan"), float("inf"), True, "100"):
            bad = copy.deepcopy(GOOD)
            bad[0]["latency_ms"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate(CASES, bad)

    def test_invalid_thresholds(self):
        for kwargs in ({"k": 0}, {"min_recall": 2}, {"min_pass_rate": -1}, {"max_p95_ms": 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                evaluate(CASES, GOOD, **kwargs)

    def test_empty_dataset(self):
        with self.assertRaises(ValueError):
            evaluate([], [])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases, preds, report = (root / name for name in ("cases.json", "preds.json", "out.json"))
            cases.write_text(json.dumps(CASES))
            preds.write_text(json.dumps(GOOD))
            args = ["--cases", str(cases), "--predictions", str(preds), "--report", str(report)]
            self.assertEqual(main(args), 0)
            self.assertTrue(json.loads(report.read_text())["passed"])
            bad = copy.deepcopy(GOOD)
            bad[0]["answer"] = "unknown"
            preds.write_text(json.dumps(bad))
            self.assertEqual(main(args), 1)
            self.assertFalse(json.loads(report.read_text())["passed"])
            preds.write_text("not json")
            self.assertEqual(main(args), 2)


if __name__ == "__main__":
    unittest.main()
