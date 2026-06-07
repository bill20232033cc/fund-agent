# MVP Real LLM Chapter Acceptance Calibration Deterministic Residual Evidence Plan

## 1. Goal

Determine whether the remaining Ch2 `delete_if_not_applicable` marker-obligation residual and Ch6 pressure-test `must_not_cover` C2 residual still require another implementation slice after accepted local Slice 1A-1F hardening.

This is an evidence-only gate. It must not run live LLM, change provider/runtime/default/budget/config, modify source code, relax parser/auditor rules, or claim live chapter/report acceptance.

## 2. Direct Evidence

Retained post-config live artifact:

- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-02.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-02-attempt-01-repair.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-06.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-06-attempt-00-writer.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-06-attempt-00-auditor-feedback.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-06-attempt-01-repair.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-06-attempt-01-auditor-feedback.md`

Observed retained facts:

- Ch2 attempt 1 has `programmatic:C2:chapter_2_alpha_yearly_breakdown:*` with `item_rule_ids=["chapter_2_alpha_yearly_breakdown"]` and message `ITEM_RULE 要求删除的段落仍出现在草稿中：超额收益分年度拆解`.
- Ch2 attempt 1 still has L1 issues; Slice 1D locally hardens prompt/repair context for L1 but does not change delete-rule behavior.
- Ch6 attempt 0 has `programmatic:C2:压力测试:*` with message `章节覆盖了 CHAPTER_CONTRACT must_not_cover 禁区：压力测试`.
- Ch6 attempt 1 has no programmatic C2, but stops at writer `unknown_anchor` before audit. Therefore retained evidence alone cannot prove whether pressure-test C2 would survive after unknown-anchor prompt hardening.

## 3. Scope

Allowed reads:

- Retained JSON/Markdown artifacts listed above.
- `docs/fund-analysis-template-draft.md`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/template/*`
- Existing tests that document relevant behavior.

Allowed artifacts:

- This plan.
- `docs/reviews/plan-review-20260607-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-review-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-deterministic-residual-evidence-judgment-20260607.md`
- Control-doc sync only if evidence is accepted.

## 4. Non-Goals

- Do not run `fund-analysis analyze --use-llm` or any provider call.
- Do not modify code, tests, template JSON, README, provider config, runtime budget, quality gate, golden/readiness, Host runtime, Agent runtime, or score-loop.
- Do not infer live acceptance from retained pre-hardening artifacts.
- Do not promote retained Ch2/Ch6 attempts to accepted output.

## 5. Evidence Procedure

1. Parse retained Ch2/Ch6 JSON and count issue classes by attempt:
   - Ch2 `chapter_2_alpha_yearly_breakdown` item-rule C2.
   - Ch2 L1 numerical closure.
   - Ch6 `压力测试` must_not_cover C2.
   - Ch6 unknown-anchor writer issues.

2. Check current authored template / typed projection for delete behavior:
   - whether `chapter_2_alpha_yearly_breakdown` is still a configured item rule;
   - whether current writer action for not-applicable delete remains `delete`;
   - whether auditor still detects deleted-rule markers if the draft contains marker phrases.

3. Check current Ch6 must_not_cover behavior:
   - whether `压力测试` remains a literal must_not_cover phrase in Ch6 contract;
   - whether programmatic auditor still blocks draft wording that includes `压力测试`;
   - whether Ch6 attempt 1 absence of pressure-test C2 is conclusive or inconclusive because writer parsing stopped before a normal audit pass.

4. Run focused deterministic validations:
   - `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q`
   - `uv run pytest tests/services/test_chapter_orchestrator.py -q`
   - `uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py`

## 6. Expected Classification Rules

- If current template/code no longer contains the delete-rule or Ch6 pressure phrase, close the corresponding residual as stale evidence.
- If retained artifact and current code both show the same fail-closed deterministic rule still active, classify the residual as surviving and route an implementation slice only if it is separable, scoped and useful.
- If retained evidence is blocked before a normal audit pass, classify the residual as inconclusive rather than closed.

## 7. Completion Criteria

The evidence gate is complete when it produces:

- a table of Ch2/Ch6 retained issue counts and current contract status;
- a controller recommendation: no-live closeout, another implementation slice, or explicit residual defer;
- validation command results;
- no code or runtime behavior changes.
