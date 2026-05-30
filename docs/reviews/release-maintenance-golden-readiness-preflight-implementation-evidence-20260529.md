# Golden Readiness Preflight Implementation Evidence

日期：2026-05-29

角色：implementation worker。未启动 gateflow；未 commit、push、PR、merge、release 或 golden promotion。

Accepted plan：`docs/reviews/release-maintenance-golden-readiness-preflight-plan-20260529.md`

Accepted plan commit：`cda2364`

## Changed Files

- `fund_agent/fund/golden_readiness_preflight.py`
- `fund_agent/services/golden_readiness_preflight_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_golden_readiness_preflight.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/release-maintenance-golden-readiness-preflight-implementation-evidence-20260529.md`

## Implementation Summary

- Added Fund-layer read-only `run_golden_readiness_preflight(...)` API with explicit dataclasses/Literals and no `extra_payload`.
- Added static current accepted disposition manifest with `schema_version`, `accepted_as_of`, `source_artifacts`, `entries`, and lifecycle semantics.
- Preserved `110020` as `raw_disposition=reviewed_coverage_candidate_input_accepted` and `preflight_disposition=reviewed_coverage_candidate`.
- Added Service request/wrapper and CLI command `golden-readiness-preflight`.
- CLI supports production `--preflight-input` JSON and shortcut `--fund-artifact fund_code::report_year::snapshot_path::score_path::quality_gate_path`; conflicting inputs exit 2.
- Current strict golden answer v1 coverage is fund-level only; reserved `strict_golden_year_not_covered` and `strict_golden_partial_coverage` are not triggered.
- Fixture promotion manifest absence is reported as `fixture_promotion_absent` blocker, not IO failure.
- 006597 bond risk blocker is emitted only as resolved item, not blocker.

## Validation

Focused ruff:

```text
uv run ruff check fund_agent/fund/golden_readiness_preflight.py fund_agent/services/golden_readiness_preflight_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_golden_readiness_preflight.py tests/ui/test_cli.py
All checks passed!
```

Focused pytest:

```text
uv run pytest tests/fund/test_golden_readiness_preflight.py tests/ui/test_cli.py -q
59 passed in 0.98s
```

Docs / repo hygiene focused pytest:

```text
uv run pytest tests/config/test_paths.py tests/fund/test_golden_readiness_preflight.py tests/ui/test_cli.py tests/test_repo_hygiene.py -q
70 passed in 1.21s
```

Full ruff:

```text
uv run ruff check .
All checks passed!
```

Full pytest / coverage gate:

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
959 passed in 4.67s
Required test coverage of 50% reached. Total coverage: 91.53%
```

## Smoke Output

Command:

```text
uv run fund-analysis golden-readiness-preflight --run-id golden-readiness-preflight-20260529 --source-csv docs/code_20260519.csv --golden-answer-path reports/golden-answers/golden-answer.json --output-dir reports/golden-readiness-preflight/golden-readiness-preflight-20260529
```

Stdout:

```text
preflight_json: reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json
preflight_md: reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md
overall_status: block
```

Generated artifacts:

- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md`

## 006597 Proof

JSON inspection result:

```text
overall_status block
006597_blocker_codes strict_golden_not_configured,fixture_promotion_absent
006597_resolved_codes blocker_resolved:bond_risk_evidence_missing
bond_blocker_emitted False
```

Conclusion:

- Current repository preflight output has `overall_status=block`.
- `006597` does not emit `bond_risk_evidence_missing` as a blocker.
- `006597` records `blocker_resolved` with `original_blocker_code=bond_risk_evidence_missing`.

## Guardrails

- Did not modify score policy, quality gate semantics, FQ0-FQ6 severity, final judgment, golden answer JSON, golden fixtures, fixture promotion state, QDII probing, FundDocumentRepository access, Host/Agent/dayu runtime, release readiness, push/PR/merge, or golden promotion.
