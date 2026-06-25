# Code Review: Atomic Source Fact Store / Composite Analysis View Split S4

## Findings

### S4-F1-未修复-中-单一 atomic fact 场景仍生成 partial derived composite fact

- **入口/函数**: `project_chapter_facts()` -> `_project_chapter()` -> `_project_field_facts()` -> `_project_atomic_field_facts()`
- **文件(行号)**: `fund_agent/fund/chapter_facts.py:1314`, `fund_agent/fund/chapter_facts.py:1317`, `fund_agent/fund/chapter_facts.py:1457`, `fund_agent/fund/chapter_facts.py:1460`, `fund_agent/fund/source_facts.py:317`, `fund_agent/fund/source_facts.py:332`
- **输入场景**: `StructuredFundDataBundle.source_facts` 只包含 migrated family 的单个 child fact，例如 `fee_schedule.management_fee`，但同 family sibling `fee_schedule.custody_fee` 不存在。
- **实际分支**: `_project_atomic_field_facts()` 先投影已有 atomic entry，然后无条件调用 `_composite_analysis_view_for_field()`；后者只要求 dependency ids 中存在任意一个 fact 就构造 derived view。`build_composite_analysis_view()` 把缺失 sibling 写入 gaps，并返回 `status="partial"`。
- **预期行为**: Phase 4 plan 明确区分 “Single fact needed -> one `source_fact_id`, no `derived_view_id`” 与 “Derived bundle needed -> one `derived_view_id` with `dependency_fact_ids`”。只需要单个 child fact 的场景应只输出 atomic bridge fact，不应额外输出带 missing sibling 的 derived composite fact。
- **实际行为**: 同一字段同时输出 atomic fact 和 `derived_view_id="fee_schedule"` 的 composite fact；当 sibling 缺失时，derived fact 映射为 `status="unknown"` / `missing_reason="field_missing"`，并把 `missing dependency fact: fee_schedule.custody_fee` 暴露到 projection.derived_views。
- **直接证据**:
  - `fund_agent/fund/chapter_facts.py:1314` 对任何 existing atomic facts 都构造 derived view。
  - `fund_agent/fund/chapter_facts.py:1457-1465` 只要任意 dependency fact 存在就调用 `build_composite_analysis_view()`。
  - `fund_agent/fund/source_facts.py:317-332` 对缺失 sibling 生成 dependency gap 并返回 `partial`。
  - no-live 复现命令输出：只输入 `fee_schedule.management_fee` 时，章节 facts 包含 `('fee_schedule.management_fee', 'available', None, ..., ('fee_schedule.management_fee',), None)` 和 `('fee_schedule', 'unknown', 'field_missing', {'fee_schedule.management_fee': '1.20%'}, (), 'fee_schedule')`。
- **影响**: S4 之后、S5 之前的现有 `ChapterFactProjection` 消费者仍按 `chapter.facts` 遍历；该 partial derived fact 会新增 `field_missing`/`unknown` 事实，可能让 writer/auditor/Evidence Confirm 旧路径把“未请求的 sibling 缺失”当成章节缺口处理。它也削弱了 “single atomic fact 独立投影” 的失败隔离目标。
- **建议改法和验证点**: 在 `_project_atomic_field_facts()` 中区分 single atomic fact projection 与 derived bundle projection。只有当前 spec 明确需要 composite compatibility view，或完整 required dependency 满足时，才生成 `_derived_view_fact_entry()`；否则只返回 atomic entries。新增 regression：只给 `fee_schedule.management_fee` 时，chapter facts 中不存在 `derived_view_id=="fee_schedule"`，且 chapter missing reasons 不因 `fee_schedule.custody_fee` 增加 `field_missing`。
- **修复风险（低/中/高）**: 中。需要明确 S4 对 compatibility derived fact 的触发条件，避免破坏 S5 后续可解析的 `projection.derived_views`。
- **严重程度（低/中/高/严重）**: 中

## Accepted Finding IDs

- S4-F1

## Open Questions

- Phase 4 plan 未明确 derived composite fact 的触发条件是否必须“全部 dependency fact 存在”或“只有下游明确需要 composite bundle 时”。修复前需要 controller/implementer 在 S4 fix artifact 中落定该条件。

## Residual Risks

- S5 Evidence Confirm atomic audit 未在本 review scope 内实现或验证。
  - Owner/destination: S5 Evidence Confirm Atomic Audit gate。
- Live/PDF/product CLI/provider/LLM 路径未运行，且本 gate 明确排除。
  - Owner/destination: 后续显式授权的 live/PDF/release evidence gate。
- 本 review 只覆盖指定 S4 files 与 implementation artifact；未审查 unrelated dirty docs、scripts、S5 implementation 或 release/readiness。
  - Owner/destination: 对应后续 gate 或独立 review。

## Scope

- Mode: Gateflow S4 Code Review
- Branch: `evidence-confirm-productionization`
- Work unit: `Atomic Source Fact Store / Composite Analysis View Split`
- Reviewed implementation artifact: `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s4-implementation-20260625-153508.md`
- Included scope:
  - `fund_agent/fund/chapter_facts.py`
  - `tests/fund/test_chapter_facts.py`
  - `tests/fund/test_chapter_facts_atomic.py`
  - S4 implementation artifact
- Excluded scope:
  - unrelated dirty docs/reviews plan files
  - unrelated untracked docs/scripts
  - S5 Evidence Confirm implementation
  - live/PDF/product CLI/provider/LLM/PR/readiness
- Parallel review coverage: 无

## Validation

- `uv run pytest tests/fund/test_chapter_facts_atomic.py tests/fund/test_chapter_facts.py -q`
  - Result: passed, `20 passed in 0.40s`
- `git diff --check -- fund_agent/fund/chapter_facts.py tests/fund/test_chapter_facts.py tests/fund/test_chapter_facts_atomic.py docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s4-implementation-20260625-153508.md`
  - Result: passed
- no-live inspection:
  - Command shape: project chapter 2 with only `fee_schedule.management_fee` in `AtomicSourceFactStore`
  - Observed facts: atomic `fee_schedule.management_fee` plus derived `fee_schedule` with `status="unknown"` and `missing_reason="field_missing"`

## Verdict

S4_CODE_REVIEW_BLOCKED_FIX_REQUIRED_NOT_READY

## Artifact Path

`docs/reviews/code-review-atomic-source-fact-store-s4-20260625-153759.md`
