# Small Baseline Real Evaluation Dev Tool

## Scope

Gate C adds a maintainer-only/dev-only wrapper at `scripts/report_quality_eval.py`.
The tool consumes explicit existing report-quality JSONL paths and/or single-bundle
JSON paths, calls the existing validator APIs, and writes a compact summary JSON
to an explicit output path chosen by the caller.

## Boundary

- Does not modify the product Typer CLI.
- Does not change Service defaults, renderer behavior, FQ0-FQ6, Host/Agent/dayu,
  FundDocumentRepository, source helpers, PDF cache, nav data, durable fixtures,
  product `analyze`, or product `checklist`.
- Does not fetch, parse, or read annual reports.
- Uses only `validate_report_quality_jsonl()` and `validate_report_quality_bundle()`.

## Usage

```bash
.venv/bin/python scripts/report_quality_eval.py \
  --jsonl /tmp/fund-agent-small-baseline-eval-20260526/bundles.jsonl \
  --bundle /tmp/fund-agent-small-baseline-eval-20260526/bundle.json \
  --output /tmp/fund-agent-small-baseline-eval-20260526/validator-summary.json \
  --run-id small-baseline-eval:20260526
```

The output JSON includes aggregate validator counts and per-input issue details.

## Verification

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/scripts/test_report_quality_eval.py -q` | `4 passed in 0.38s` |
| `.venv/bin/ruff check scripts/report_quality_eval.py tests/scripts/test_report_quality_eval.py` | `All checks passed!` |
| `git diff --check` | passed |
