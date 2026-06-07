# MVP Real LLM Chapter Acceptance Calibration Slice 1A Implementation Evidence

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `Real LLM chapter acceptance calibration gate`
- Slice: `1A - Ch1 Typed Required-Output Marker Protocol Alignment`
- Classification: `heavy`
- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-gate-plan-20260607.md`
- Controller judgment: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-gate-plan-controller-judgment-20260607.md`

This slice did not run live LLM, did not change provider/default/runtime/budget/config, did not change template JSON, and did not touch Ch2 L1, Ch4 audit parse, Ch6 unknown anchor, score-loop, golden/readiness, Agent runtime, Host runtime, PR, push or release state.

## 2. Root Cause

Accepted local root cause for Slice 1A:

- Production `--use-llm` uses `typed_template_path="typed_template_contract"`.
- Writer prompt/parser uses stable typed required-output item id markers when `typed_required_output_items` is present.
- Programmatic auditor still checked legacy `chapter.contract.required_output_items` text markers.
- Therefore a typed-path draft could satisfy writer marker protocol while failing auditor C2 marker checks.

This root cause covers Ch1 marker-protocol mismatch only. It does not claim to fix Ch2 `l1_numerical_closure`, Ch4 `audit_parse`, Ch6 `unknown_anchor`, duplicate anchor behavior, semantic LLM audit issues, or accepted final report assembly.

## 3. Files Changed

- `fund_agent/fund/chapter_auditor.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- `fund_agent/fund/README.md`
- this evidence artifact

## 4. Implementation Summary

`chapter_auditor.py`:

- Added `_required_output_marker_items(writer_input)`.
- `_audit_contract_markers()` now checks:
  - typed stable item ids when `writer_input.typed_required_output_items` is present;
  - legacy CHAPTER_CONTRACT required-output text when typed items are absent.
- Bare required-output text remains insufficient.
- Missing typed marker still triggers C2.
- No deleted-item action filtering was implemented in this slice.

Tests:

- Added typed Ch1 positive marker test.
- Added typed missing-marker fail-closed test.
- Added legacy regression proving typed id markers do not satisfy legacy marker checks.
- Added Service orchestrator Ch1 typed path test proving Ch1 can be accepted with typed item id markers.
- Updated existing typed path tests whose previous expected failures were caused by the marker mismatch; they now assert accepted/partial behavior while preserving typed required-output propagation checks.

README:

- Updated Fund package README to state current programmatic auditor marker behavior for typed and legacy paths.

## 5. Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Result: `121 passed in 1.02s`

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Result: `47 passed in 0.46s`

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Result: `All checks passed!`

## 6. Residuals

- Ch1 may still fail live LLM acceptance on duplicate anchor ids, LLM semantic audit, conclusion extraction or other non-marker issues. No live rerun was authorized or executed.
- Ch2 `prompt_contract/l1_numerical_closure` remains a separate numerical-closure calibration gate.
- Ch4 `audit_parse` remains a separate auditor line-protocol gate.
- Ch6 `prompt_contract/unknown_anchor` remains a separate anchor projection / group-anchor conversion gate.
- Ch3 and Ch5 `code_bug_other` should be revisited after deterministic evidence determines whether they share the marker-protocol root cause.
- `delete_if_not_applicable` marker-obligation sharing remains a deferred future contract gate if current evidence ever requires it.

## 7. Verdict

`SLICE_1A_IMPLEMENTED_LOCALLY`

The typed required-output marker protocol is now aligned between writer prompt/parser and programmatic auditor for current typed path behavior, with legacy behavior preserved.
