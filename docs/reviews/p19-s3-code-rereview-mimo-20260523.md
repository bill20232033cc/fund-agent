# P19-S3 Code Re-review - Mimo - 2026-05-23

## Findings

None.

No blocking finding found. The accepted findings in `docs/reviews/p19-s3-code-review-controller-judgment-20260523.md` are closed in the current uncommitted diff:

- F1 closed: `FundAnalysisService._resolve_valuation_state()` now checks `result.index_code != target.index_code` and raises `ValueError` before building `ValuationStateResolution` (`fund_agent/services/fund_analysis_service.py:556`). Regression coverage exists in `test_fund_analysis_service_thermometer_identity_mismatch_fails_closed` (`tests/services/test_fund_analysis_service.py:611`).
- F2 closed: `ThermometerCalculationError` fallback now appends a derived thermometer failure anchor with `section_id="thermometer"`, `row_locator="<index_code>:calculation_error"`, target identity, unavailable reason, and disclaimer context (`fund_agent/services/fund_analysis_service.py:536`, `fund_agent/fund/analysis/valuation_state.py:398`). R1 now accepts either external API thermometer anchors or derived failure anchors containing the unavailable reason, and rejects missing failure provenance (`fund_agent/fund/audit/audit_programmatic.py:1101`, `fund_agent/fund/audit/audit_programmatic.py:1123`; tests at `tests/fund/audit/test_audit_programmatic.py:1415` and `tests/fund/audit/test_audit_programmatic.py:1458`).
- F3 closed: the Fund README no longer says checklist valuation only consumes explicit `valuation_state`; it now names `ValuationStateResolution` as the consumed truth source and describes explicit `valuation_state` as manual override / legacy projection (`fund_agent/fund/README.md:239`).
- F4 closed: supported `benchmark_index_code` no longer bypasses same-source text validation. Text components must be exact same supported index or ignorable cash/bond; derived/style/industry/other equity/uncertain components fail closed as `unsupported_index` or `ambiguous_benchmark` (`fund_agent/fund/analysis/valuation_state.py:189`, `fund_agent/fund/analysis/valuation_state.py:480`). Regression coverage includes `000300 + 沪深300价值指数收益率` and `000905 + 中证500质量成长指数收益率` (`tests/fund/analysis/test_valuation_state.py:253`).

No new boundary regression found in the reviewed diff: analyze still calls only `ThermometerService.run(ThermometerRequest(index_code=target.index_code))` after exact mapped target resolution (`fund_agent/services/fund_analysis_service.py:520`), explicit `valuation_state` returns before any thermometer call (`fund_agent/services/fund_analysis_service.py:517`), and no new `FundThermometerAdapter`, public page scraping, all-A, Dayu runtime, or `extra_payload` path was introduced into the analyze flow.

## Residual risks

- Live akshare / external data smoke was not run in this re-review. This remains outside the current fix diff and is still covered only by existing source/cache unavailable or fail-closed behavior.
- `ProgrammaticAuditInput.valuation_state_resolution` still has a historical optional compatibility branch. The current Service -> checklist -> renderer -> audit path passes the structured resolution, so this is not blocking for the accepted findings.
- The exact-identity text gate remains intentionally conservative. It can gray out ambiguous or unsupported benchmark text instead of attempting inference, which matches the P19-S3 fail-closed requirement.

Validation performed:

- `.venv/bin/python -m pytest tests/fund/analysis/test_valuation_state.py tests/fund/analysis/test_checklist.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q` -> `163 passed in 0.69s`
- `.venv/bin/python -m pytest -q` -> `537 passed in 1.08s`
- `.venv/bin/python -m ruff check fund_agent tests` -> `All checks passed!`
- `git diff --check` -> passed with no output

## Verdict

PASS
