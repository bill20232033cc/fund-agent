# Code Review

## Scope

- Mode: current changes
- Branch: evidence-confirm-productionization
- Base: 5616db7 gateflow: accept ec-p4 service integration slice 3
- Output file: docs/reviews/code-review-20260622-233500-ds-ec-p4-slice4.md
- Included scope: `tests/services/test_fund_analysis_service.py` uncommitted diff (+37 lines, one new test)
- Excluded scope: all other workspace files (unchanged production code, docs residue outside Slice 4 contract)
- Parallel review coverage: 无

## Slice 4 Contract Verification

| Contract item | Evidence | Result |
|---|---|---|
| EC-P4 keeps Evidence Confirm outside report Markdown | `TemplateRenderInput` (renderer.py:88-115) has no `evidence_confirm_summary` field; renderer has zero `evidence_confirm` references | ✅ |
| Test proves Service result with EC summary returns existing renderer/report body unchanged | `assert result.report_markdown == baseline_result.report_markdown` (test line 700) | ✅ |
| Test asserts no "Evidence Confirm" / "evidence_confirm_status" in report Markdown | String negative assertions (test lines 701-702) | ✅ |
| Programmatic audit input remains current report Markdown | `run_programmatic_audit(render_result.audit_input)` (service.py:764) unchanged; no EC in audit path | ✅ |
| EC status not treated as investment conclusion, chapter, or evidence appendix | `evidence_confirm_summary` is peer field on `FundAnalysisResult` (service.py:428), never enters `TemplateRenderInput` | ✅ |
| No production renderer code change | `git diff --stat` shows only test file changed; `renderer.py` untouched | ✅ |

## Findings

未发现实质性问题。

### Structural Analysis

The non-rendering guard is enforced at two independent levels:

1. **Type-level**: `TemplateRenderInput` (renderer.py:88-115) defines the sole input contract to `render_template_report()`. It has no `evidence_confirm_summary` field. No production code change added one.

2. **Data-flow level**: `FundAnalysisResult.report_markdown` (service.py:444) delegates exclusively to `self.render_result.report_markdown`. The `evidence_confirm_summary` field (service.py:428) is a peer field on the result dataclass, accessible to CLI/quality-gate callers but structurally invisible to the rendering pipeline.

The test `test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report` (test_fund_analysis_service.py:669-702) exercises the full analysis path:

- Baseline: Service without EC runner → report markdown
- Test: Service with EC runner (policy="warn", fail result) → report markdown
- Assertion 1: `evidence_confirm_summary is not None` — proves EC actually ran and produced output
- Assertion 2: `report_markdown == baseline_result.report_markdown` — proves byte-identical rendering
- Assertions 3-4: string-level negative guards — proves no text/field-name leak

### Adversarial Pass

- **Renderer bypass**: No path exists. `render_template_report()` only reads `TemplateRenderInput` fields; `evidence_confirm_summary` is not one of them.
- **Quality gate interference**: Test isolates with `quality_gate_policy="off"`. With quality gate on, EC warnings go to `FundAnalysisResult.warnings`, not `report_markdown` — separate channel, no contamination path.
- **Policy interaction**: Test uses `evidence_confirm_policy="warn"`. Under `"block"` with fail, the analysis blocks before rendering — no report is produced, so no markdown to contaminate.
- **Pass vs fail EC result**: The structural separation is independent of EC outcome. A pass result would produce an `evidence_confirm_summary` that is equally invisible to the renderer.
- **Non-deterministic report content**: The equality assertion (`==`) passes, confirming the renderer produces identical output for identical input regardless of EC state.

## Validation Commands and Results

```text
$ uv run pytest tests/services/test_fund_analysis_service.py -q
........................................                                 [100%]
40 passed in 0.79s

$ uv run ruff check tests/services/test_fund_analysis_service.py
All checks passed!

$ git diff --check -- tests/services/test_fund_analysis_service.py
(no output — no whitespace errors)
```

## Open Questions

无

## Residual Risk

| Risk | Owner | Destination |
|---|---|---|
| Renderer type-level guard (optional `evidence_confirm_summary` field on `TemplateRenderInput` docstring-stating non-rendering) was not added | Renderer owner | Classified as not required for Slice 4; current structural separation is sufficient. If a future gate adds EC rendering, the existing regression test will fail on the string negative assertions |
| UI-specific EC presentation remains unimplemented | UI/product owner | Covered by later approved UI/reporting gate |
| Release/readiness remains NOT_READY | Controller | PR-40 remains draft/open |

## Verdict

**PASS**
