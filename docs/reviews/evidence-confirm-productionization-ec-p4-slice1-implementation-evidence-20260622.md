# Evidence Confirm Productionization EC-P4 Slice 1 Implementation Evidence

## Gate / Slice

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `implementation`
- Classification: `heavy`
- Slice: `Slice 1 - Fund Summary + Quality Gate ECQ Projection`
- Branch: `evidence-confirm-productionization`
- Release/readiness: `NOT_READY`

## Changed Files

- `fund_agent/fund/evidence_confirm_production.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `tests/fund/test_evidence_confirm_production.py`
- `tests/fund/test_quality_gate_integration.py`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice1-implementation-evidence-20260622.md`

No Service/UI/renderer/CLI/control-doc/source/PDF/cache/parser/provider files were modified.

## Exact Behavior Implemented

- Added compact `EvidenceConfirmProductionSummary` with safe counts/statuses only.
- Added `summary_from_repository_result(result, policy)`.
  - Repository/pathway failure converts to `status="fail"` and `not_run_reason="repository_failure:<reason>"`.
  - Summary does not carry raw excerpts, PDF/cache paths, parser JSON or source adapter objects.
  - Aggregate precedence is `pathway fail -> fail`, then deterministic/semantic `fail > warn > pass > not_run/not_applicable`.
- Added `not_run_evidence_confirm_summary(fund_code, report_year, policy, reason)`.
  - Stable reason codes accepted: `not_requested`, `policy_off`, `invalid_request`, `runner_exception:<class_name>`, `repository_failure:<reason>`.
- Added optional `evidence_confirm_summary` parameter to `run_quality_gate_for_bundle()`.
  - Omitted/`None` default keeps existing FQ-only behavior unchanged.
  - Explicit not-run summary maps to `ECQ0/info`.
  - Pathway failure maps to `ECQ1/block|warn` according to policy.
  - Deterministic V2 fail maps to `ECQ2/block|warn` according to policy.
  - Deterministic V2 warn maps to `ECQ3/warn`.
- Added `QualityGateIssue.issue_id` for stable ECQ IDs.
- Added `merge_quality_gate_issues()` to re-aggregate status and rewrite `quality_gate.json` / `quality_gate.md` after `run_quality_gate()` returns.
- Did not change `score.json` generation or `write_extraction_score_records()`.

## Tests / Validation

Command:

```text
uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
```

Output:

```text
............................................                             [100%]
44 passed in 0.84s
```

Command:

```text
uv run ruff check fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py
```

Output:

```text
All checks passed!
```

Command:

```text
git diff --check -- fund_agent/fund/evidence_confirm_production.py fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py docs/reviews/evidence-confirm-productionization-ec-p4-slice1-implementation-evidence-20260622.md
```

Output:

```text
<no output; command passed>
```

## Boundary Proof

- `quality_gate_integration.py` imports only config paths, data extractor bundle type, extraction score writer, extraction snapshot helpers, the compact Evidence Confirm production summary, and quality gate types/helpers.
- `tests/fund/test_quality_gate_integration.py::test_quality_gate_integration_boundary_no_repository_or_source_imports` parses `quality_gate_integration.py` imports with AST and rejects repository, source adapter, parser, Docling and provider imports.
- Static check: `rg -n "evidence_confirm|EvidenceConfirm|ECQ" fund_agent/fund/extraction_score.py` returned no matches.
- `tests/fund/test_score_json_schema_remains_evidence_confirm_unaware` verifies ECQ appears in `quality_gate.json` while `score.json` remains Evidence-Confirm-unaware.
- No live/PDF/network/provider/LLM command was run.

## Residual Risks

- Service propagation remains covered by later approved Slice 2.
- CLI/UI summary and exit behavior remain covered by later approved Slice 3.
- Renderer non-rendering guard remains covered by later approved Slice 4.
- Semantic companion propagation remains covered by later approved Slice 5 if still inside the accepted injected-result boundary.
- Docs/control sync remains covered by later approved Slice 6.
- Release/readiness remains `NOT_READY`.

## Verdict

`EC_P4_SLICE1_IMPLEMENTATION_READY_FOR_CODE_REVIEW_NOT_READY`
