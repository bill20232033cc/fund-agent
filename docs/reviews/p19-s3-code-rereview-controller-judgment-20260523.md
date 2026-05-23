# P19-S3 Code Re-review Controller Judgment - 2026-05-23

## Inputs

- Implementation commit: `dc4ea04`
- Code review artifacts:
  - `docs/reviews/p19-s3-code-review-mimo-20260523.md`
  - `docs/reviews/p19-s3-code-review-glm-20260523.md`
  - `docs/reviews/p19-s3-code-review-controller-judgment-20260523.md`
- Fix artifact: `docs/reviews/p19-s3-code-review-fix-20260523.md`
- Re-review artifacts:
  - `docs/reviews/p19-s3-code-rereview-mimo-20260523.md`
  - `docs/reviews/p19-s3-code-rereview-glm-20260523.md`

## Judgment

Verdict: ACCEPTED

P19-S3 automatic thermometer-to-`valuation_state` integration is accepted after the review/fix/re-review loop. MiMo and GLM both returned `PASS` on the fix diff, and the controller accepts that the blocking identity/provenance findings are closed.

## Accepted Closure

### F1 - Returned thermometer identity mismatch

Closed.

`FundAnalysisService._resolve_valuation_state()` now checks `ThermometerReading.index_code` against the mapped target index before constructing `ValuationStateResolution`. A mismatch raises `ValueError`, so a wrong provider/cache result cannot become an internally consistent but wrong report state.

### F2 - Unavailable thermometer provenance

Closed.

`ThermometerCalculationError` fallback now preserves a derived thermometer failure anchor with target index identity, failure reason, and self-owned thermometer context. R1 now rejects `unavailable_thermometer` resolutions that lack either an external thermometer anchor or this derived failure anchor.

### F3 - Fund README old wording

Closed.

`fund_agent/fund/README.md` now describes `ValuationStateResolution` as the current checklist valuation truth source, with explicit `valuation_state` limited to manual override / legacy projection.

### F4 - `benchmark_index_code` text conflict hardening

Closed.

Supported `benchmark_index_code` no longer bypasses same-source benchmark text checks. Derived/style/industry/other equity or uncertain components fail closed; exact supported index plus ignorable cash/bond components remains allowed.

## Validation

Controller and reviewers recorded these commands passing:

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check
```

Results:

- Targeted P19-S3 suite: `163 passed`
- Full suite: `537 passed`
- Ruff: passed
- Diff check: passed

## Residual Risks

- Live akshare / external data smoke was not run in this loop; this remains an external-data residual covered by unavailable/fail-closed behavior.
- `ProgrammaticAuditInput.valuation_state_resolution` remains optional for legacy compatibility. Current Service -> renderer -> audit path passes the structured resolution; removing the compatibility branch should be a future audit-hardening slice, not a P19-S3 blocker.
- Add a future persistent regression test for `benchmark_index_code=000300/000905` plus exact supported index and cash/bond components. Re-review manually verified this case, but the committed test set currently emphasizes conflict cases.

## Next Gate

Advance P19 to P19-S4 plan/review for expanded index coverage.

