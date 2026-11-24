# RAG release quality gate

## Engineering problem

A successful API health check alone cannot establish that a retrieval-augmented generation system continues to retrieve relevant sources, preserve expected answer facts, or meet a latency budget after a change.

This repository-specific, AI-assisted extension introduces an independent, deterministic evaluator for recorded RAG outputs. It runs without provider credentials or external dependencies. Review the commit diffs for implementation history.

## Architecture

Reference cases (expected source IDs, required and prohibited phrases) + recorded predictions (ranked source IDs, answer, latency) -> strict ID and schema validation -> per-case scoring -> aggregate release thresholds -> machine-readable report + process exit code.

## Metrics and decisions

- Recall@k: fraction of unique expected sources present among the first k retrieved source IDs, averaged equally across cases.
- Case pass rate: fraction of cases with complete expected-source recall at k, all required substrings present, and no forbidden substrings.
- P95 latency: nearest-rank percentile of recorded latencies; not the runtime of the evaluator.
- Forbidden phrase matches block the gate regardless of aggregate thresholds.
- Missing, extra and duplicate case IDs, invalid latencies and empty datasets fail input validation.
- Exit 0: quality gate passes. Exit 1: evaluated regression. Exit 2: invalid input or I/O failure.
- Defaults: k=3, mean recall >=0.90, case pass rate=1.0, p95 <=1500 ms. CLI flags override these.

## Reproduce

```bash
python -m unittest discover -s quality_tests -v
python quality_gate.py --cases quality_fixtures/cases.json --predictions quality_fixtures/passing.json --report reports/passing.json
python quality_gate.py --cases quality_fixtures/cases.json --predictions quality_fixtures/regression.json --report reports/regression.json
```

The first fixture is designed to pass; the second is designed to fail with exit 1. Inspect generated JSON for per-case and aggregate evidence. The dedicated CI workflow tests both paths and uploads reports. CI execution status is available under Actions and must be checked before claiming success.

## Limitations and next steps

Fixtures are intentionally synthetic and latencies are supplied example values, not measured service performance. Phrase matching cannot establish semantic correctness, entailment or hallucination absence. The evaluator currently consumes recorded outputs, not live FastAPI predictions. It is an offline validation gate, not a deployed monitoring system or proof of production ML accuracy. The workflow verifies the evaluator; it is not yet a required branch-protection check or a dependency of the Render deployment job.

Before connecting to a deployment, capture predictions from a controlled RAG evaluation run, establish a reviewed real reference set, add semantic evaluation and configure the gate as a required release check. Upstream licensing and independent deployment ownership remain unresolved; this extension does not change those facts.
