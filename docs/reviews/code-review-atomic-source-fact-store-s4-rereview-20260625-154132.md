# Code Review: Atomic Source Fact Store / Composite Analysis View Split S4 Re-review

## Scope

- Mode: Gateflow S4 re-review after fix
- Branch: `evidence-confirm-productionization`
- Work unit: Atomic Source Fact Store / Composite Analysis View Split
- Accepted finding target: `S4-F1` only
- Reviewed prior review artifact: `docs/reviews/code-review-atomic-source-fact-store-s4-20260625-153759.md`
- Reviewed fix artifact: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s4-fix-20260625-153949.md`
- Included files:
  - `fund_agent/fund/chapter_facts.py`
  - `tests/fund/test_chapter_facts_atomic.py`
  - `tests/fund/test_chapter_facts.py`
  - fix artifact
- Excluded scope:
  - S5 Evidence Confirm/live/PDF/product CLI/provider/LLM/PR/readiness
  - unrelated dirty docs, plans, scripts, and untracked artifacts
  - unrelated source-truth, release, or quality-gate residuals
- Parallel review coverage: 无

## Finding Status

- `S4-F1`: 已修复

## Findings

未发现 S4-F1 fix scope 内的新实质性问题。

## Evidence

- `fund_agent/fund/chapter_facts.py` 中 `_composite_analysis_view_for_field()` 现在先读取 `_MIGRATED_FIELD_FACT_IDS`，并在任一 dependency fact 不存在时返回 `None`，不再把 single atomic child 输入传入 `build_composite_analysis_view()` 生成 partial composite view。
- `_project_atomic_field_facts()` 在 `derived_view is None` 时只返回 atomic entries；因此单个 `fee_schedule.management_fee` 不再附加 `derived_view_id="fee_schedule"` 的章节 fact。
- `_project_composite_analysis_views()` 复用同一 `_composite_analysis_view_for_field()` 条件；因此 `projection.derived_views` 也不会为缺 sibling 的 family 生成 partial view。
- full dependency 场景仍调用 `build_composite_analysis_view()`，derived view 保留 `dependency_fact_ids`。
- `tests/fund/test_chapter_facts_atomic.py` 覆盖：
  - 单个 `fee_schedule.management_fee` 保留 atomic entry；
  - 不生成 `derived_view_id == "fee_schedule"`；
  - `projection.derived_views` 不含 `fee_schedule`；
  - 不新增 `field_missing`；
  - full dependency `fee_schedule.management_fee` + `fee_schedule.custody_fee` 仍生成 derived view，并断言两个 `dependency_fact_ids`。

## Validation Results

- `uv run pytest tests/fund/test_chapter_facts_atomic.py tests/fund/test_chapter_facts.py -q`
  - Result: passed, `20 passed in 0.65s`
- `uv run pytest tests/fund/test_source_facts.py -q`
  - Result: passed, `17 passed in 0.62s`
- `uv run ruff check fund_agent/fund/chapter_facts.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_chapter_facts.py`
  - Result: passed, `All checks passed!`
- `git diff --check -- fund_agent/fund/chapter_facts.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_chapter_facts.py docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s4-fix-20260625-153949.md`
  - Result: passed
- no-live manual projection check:
  - Single input: only `fee_schedule.management_fee`
    - Observed `source_fact_ids`: `[("fee_schedule.management_fee",)]`
    - Observed derived chapter facts: `[]`
    - Observed `projection.derived_views`: `[]`
    - Observed chapter `missing_reasons`: `()`
  - Full input: `fee_schedule.management_fee` + `fee_schedule.custody_fee`
    - Observed derived chapter facts: `["fee_schedule"]`
    - Observed projection view: `("fee_schedule", ("fee_schedule.management_fee", "fee_schedule.custody_fee"), "accepted")`

## Residual Risks

- S5 Evidence Confirm atomic audit remains outside this re-review scope.
  - Owner/destination: S5 Evidence Confirm Atomic Audit gate.
- Live/PDF/product CLI/provider/LLM paths were not run and remain outside this gate.
  - Owner/destination: later explicitly authorized live/PDF/release evidence gate.
- Release/readiness remains `NOT_READY`; this artifact only accepts the S4 fix slice for local commit consideration.
  - Owner/destination: controller / release-readiness gate.
- Unrelated dirty and untracked workspace files were not reviewed.
  - Owner/destination: corresponding work units or artifact disposition gate.

## Open Questions

- 无。

## Verdict

S4_RE_REVIEW_PASS_READY_FOR_ACCEPTED_SLICE_COMMIT_NOT_READY

## Artifact Path

`docs/reviews/code-review-atomic-source-fact-store-s4-rereview-20260625-154132.md`
