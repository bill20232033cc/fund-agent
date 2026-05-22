# P19-S3 Code Review Controller Judgment - 2026-05-23

## Inputs

- Implementation commit: `dc4ea04`
- Control commit: `d829237`
- MiMo review: `docs/reviews/p19-s3-code-review-mimo-20260523.md`
- GLM review: `docs/reviews/p19-s3-code-review-glm-20260523.md`

## Judgment

Verdict: BLOCKED

P19-S3 must not enter acceptance until the automatic thermometer path is fail-closed on identity mismatch and the unavailable thermometer evidence path preserves enough provenance for R1 and the report appendix.

## Accepted Findings

### F1 - Returned thermometer identity is not checked

Accepted as blocker.

First-principles reason: P19-S3 changes final judgment inputs by default only when benchmark identity is exact. If the provider or cache returns a different `ThermometerReading.index_code`, the rendered report and R1 can be internally consistent around the wrong index while the fund benchmark was a different supported index. The Service must compare the requested `target.index_code` with the returned reading and fail closed on mismatch.

Required fix:

- In `FundAnalysisService._resolve_valuation_state()`, after confirming `ThermometerReading`, require `result.index_code == target.index_code`.
- Treat mismatch as programming/provider contract error and raise `ValueError`.
- Add a Service regression test: mapped `000300` target plus returned `000905` reading must fail closed.

### F2 - `ThermometerCalculationError` path lacks thermometer failure provenance anchor

Accepted as required fix in the same loop.

First-principles reason: unavailable thermometer is still a thermometer path. The benchmark anchor explains why the service attempted automatic valuation, but not why the self-owned thermometer failed. The evidence appendix and R1 need a structured failure anchor carrying the target index and failure reason.

Required fix:

- Build a dedicated derived thermometer failure anchor for `source="unavailable_thermometer"` calculation-error fallback.
- Anchor should include target `index_code`, `index_name`, failure reason, and self-owned thermometer/disclaimer context.
- R1 should require unavailable thermometer resolutions to carry either an `external_api` thermometer anchor or a derived thermometer failure anchor whose note includes the unavailable reason.
- Add Service and audit tests for the fallback anchor.

### F3 - Fund README old checklist wording still says valuation only consumes explicit input

Accepted as low-risk documentation fix.

Required fix:

- Update `fund_agent/fund/README.md` to say valuation consumes `ValuationStateResolution`; explicit `valuation_state` is only the manual override / legacy compatible projection.

### F4 - `benchmark_index_code` priority can bypass text identity conflict checks

Accepted as required correctness hardening.

First-principles reason: the exact identity gate should be based on all same-source benchmark evidence, not one convenient field. If later extraction starts filling `benchmark_index_code` from a derived/style/industry benchmark, the code-only fast path could bypass the P19-S3 non-goal boundary.

Required fix:

- When `benchmark_index_code` is supported and benchmark/index-profile text exists, validate textual components are compatible with the same exact rule or ignorable cash/bond components.
- If text contains unsupported equity or derived supported-index components, return `unsupported_index` or `ambiguous_benchmark` and do not call the thermometer.
- Add tests for `benchmark_index_code="000300"` with `沪深300价值指数收益率` and `benchmark_index_code="000905"` with `中证500质量成长指数收益率`.

## Deferred Findings

### D1 - R1 keeps legacy compatibility when `valuation_state_resolution` is absent

Deferred, not a P19-S3 acceptance blocker.

Reason: the current Service and renderer pass `ValuationStateResolution` as the structured truth, and removing the compatibility path may broaden the blast radius beyond this slice. Keep as a residual risk unless the fix loop touches the same audit branch safely. Future audit-hardening phase should replace implicit legacy pass-through with an explicit legacy flag.

## Required Validation

- Targeted P19-S3 suite:

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q
```

- Full suite:

```bash
.venv/bin/python -m pytest -q
```

- Ruff:

```bash
.venv/bin/python -m ruff check fund_agent tests
```

- Diff hygiene:

```bash
git diff --check
```

