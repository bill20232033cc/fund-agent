# Code Review

## Scope

- Mode: current changes (worktree uncommitted diff)
- Branch: `evidence-confirm-productionization`
- Base: uncommitted workspace changes relative to last commit `5616db7`
- Output file: `docs/reviews/code-review-20260622-233500-mimo-ec-p4-slice4.md`
- Included scope:
  - `tests/services/test_fund_analysis_service.py` (uncommitted diff: +37 lines, one new test)
  - `docs/reviews/evidence-confirm-productionization-ec-p4-slice4-implementation-evidence-20260622.md` (new untracked file)
- Excluded scope: production source code, renderer, CLI, quality gate, Fund layer
- Parallel review coverage: none

## Slice 4 Contract Verification

| Contract Requirement | Status | Evidence |
|---|---|---|
| EC-P4 deliberately keeps Evidence Confirm outside report Markdown | PASS | No production renderer code changed; test-only proof |
| Test proves Service result with EC summary returns existing renderer/report body unchanged | PASS | `result.report_markdown == baseline_result.report_markdown` (line 700) |
| Test asserts no "Evidence Confirm" or "evidence_confirm_status" string in report Markdown when EC summary exists | PASS | Lines 701-702 |
| Programmatic audit input remains current report Markdown | PASS | No audit input mutation; report_markdown equality proven |
| EC status not treated as investment conclusion, chapter content, or evidence appendix | PASS | No renderer change; EC summary stays on Service result only |
| No production renderer code change unless required | PASS | Only test file changed |

## Findings

未发现实质性问题。

## Validation Commands and Results

```text
$ git diff -- tests/services/test_fund_analysis_service.py
+37 lines: new test test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report

$ git diff -- docs/reviews/evidence-confirm-productionization-ec-p4-slice4-implementation-evidence-20260622.md
(empty — new untracked file, no diff against HEAD)

$ uv run pytest tests/services/test_fund_analysis_service.py -q
40 passed in 0.81s

$ uv run ruff check tests/services/test_fund_analysis_service.py
All checks passed!

$ git diff --check -- tests/services/test_fund_analysis_service.py docs/reviews/evidence-confirm-productionization-ec-p4-slice4-implementation-evidence-20260622.md
(no output — no whitespace errors)
```

## Test Analysis

The new test `test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report` (line 669) is well-constructed:

- **Baseline isolation**: uses two independent `FundAnalysisService` instances with separate `_FakeExtractor(_bundle())` calls. `_bundle()` constructs a fresh `StructuredFundDataBundle` per invocation; `_FakeExtractor.extract` uses `dataclasses.replace()` to copy, so the two service runs share no mutable state.
- **Correct policy/result pairing**: `evidence_confirm_policy="warn"` with a `_FakeEvidenceConfirmRunner(_repository_run_result("fail"))` correctly produces an EC summary (policy warn + fail = continue with warn-visible metadata, no blocking).
- **Strong assertion**: `result.report_markdown == baseline_result.report_markdown` proves exact byte-level equality, which is strictly stronger than the contract's substring-absence requirement.
- **String-absence assertions**: `"Evidence Confirm" not in result.report_markdown` and `"evidence_confirm_status" not in result.report_markdown` directly verify the non-rendering contract.

## Residual Risks

| Risk | Owner | Destination |
|---|---|---|
| Renderer type-level guard not added (no `evidence_confirm_summary` field on `TemplateRenderInput`) | Fund/template owner | Deferred to future renderer wording gate if product owner requires visible section; current test-only proof is sufficient for EC-P4 |
| UI-specific presentation of EC summary outside report body | UI/product owner | Later or separate approved UI/reporting work |
| Programmatic audit input remains current report Markdown without EC metadata | Audit owner | Covered by existing renderer/service tests and unchanged production code |

## Verdict

**PASS**

## Release / Readiness

**NOT_READY** — This is a test-only proof slice. No production code changed. Release/readiness remains determined by later gates.
