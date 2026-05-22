# P17-S1 tracking_error extractor ambiguity boundary code review controller judgment（2026-05-22）

## Verdict

`ACCEPTED`

P17-S1 implementation is accepted. The implementation stays inside Fund Capability extractor scope, removes the stale generic `tracking_error_ambiguous` production path, preserves direct-disclosure success semantics, and converts target/limit, mixed actual/target, manager narrative, benchmark-only, standard-deviation-only, unparseable, table/text conflict, and multi-match cases into explicit fail-closed notes.

## Reviewed Artifacts

- Plan: `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md`
- Implementation report: `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-implementation-20260522.md`
- MiMo review: `docs/reviews/p17-s1-code-review-mimo-20260522.md`
- GLM review: `docs/reviews/p17-s1-code-review-glm-20260522.md`

## Finding Judgment

| Finding | Decision | Rationale |
|---|---|---|
| Standard-deviation-only note can be recorded without a tracking-error keyword | Accepted as residual | First principles: this is a missing-path diagnostic only, never a success path. Standard deviation is the exact known confusion source for tracking error, so the note improves observability without accepting unsupported values. Future note-precision work may add a stricter keyword guard if real data shows misleading diagnostics. |
| Removing `年化` from actual-signal keywords can downgrade some mixed rows to target/limit note | Accepted as residual | `年化` is a measurement-period modifier, not evidence that a value is actual observed disclosure. Fail-closed behavior is preserved, and direct `年化跟踪误差为 X%` remains accepted when no target/limit keyword is present. |
| `_classify_tracking_error_nonmatch_context` lacks benchmark-only table-context classification | Accepted as residual | The observed production risk is low and fail-closed behavior is unchanged. Benchmark-only text path is covered; table-context alignment can be handled by a future classifier precision pass if needed. |
| Table-level multi-match and `§2` fallback lacked focused tests | Accepted and fixed before closeout | Controller required a minimal test-only follow-up because both paths are part of the implemented contract. Added deterministic tests for table-level multi-match and `§2` fallback. |
| Orphan `performance_with_tracking_error_ambiguous.txt` fixture | Deferred optional cleanup | It is not referenced and does not affect behavior. Removing historical fixtures is repo hygiene, not required for this gate. |
| `_tracking_error_context_is_target_or_ambiguous` name is now slightly broad | Deferred optional cleanup | Cosmetic rename only. Behavior and public contract are unaffected. |

## Design Boundary Check

- Scope stayed in `fund_agent/fund/extractors/performance.py`, `tests/fund/extractors/test_performance.py`, `tests/README.md`, and review artifacts.
- No Service/UI/Runtime/Engine/source orchestration/document adapter/PDF/cache helper changes.
- No production golden rows, selected CSV edits, external index data, calculated tracking error, Evidence Confirm, LLM audit, or Dayu runtime dependency.
- No direct annual-report source access was introduced; extractor continues to consume `ParsedAnnualReport`.
- No explicit parameters were hidden in `extra_payload`.

## Validation

Controller re-ran:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
# 22 passed in 0.41s

.venv/bin/python -m pytest tests/fund/extractors -q
# 62 passed in 0.43s

.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
# 55 passed in 0.46s

.venv/bin/python -m ruff check fund_agent tests
# All checks passed!

git diff --check HEAD
# passed with no output
```

## Residuals

| Residual | Owner | Handling |
|---|---|---|
| Standard-deviation-only note precision | Future note precision pass | Only revisit if real reports show misleading missing notes. |
| `年化` mixed-row note precision | Future note precision pass | Keep current classifier because `年化` is not actual-disclosure evidence. |
| Benchmark-only table-context note alignment | Future classifier alignment pass | Add table-context classifier parity only when a real fixture requires it. |
| `tracking_error_incomplete_anchor` fixture | Future parser malformed-table fixture | Current builders naturally produce complete anchors; do not fabricate impossible parser objects for this gate. |
| Production `tracking_error` golden rows for `001548` and P16 enhanced-index candidates | Future evidence-backed golden gate | Still blocked until reviewed direct observed disclosure evidence exists. |
| Calculated tracking error / external index data | Future design phase | Out of scope for deterministic direct-disclosure extractor hardening. |

## Next Gate

Proceed to P17-S1 aggregate deepreview after recording the accepted implementation commit in `docs/implementation-control.md`.
