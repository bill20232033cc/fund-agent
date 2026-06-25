# Code Review - Atomic Source Fact Store Aggregate

## Scope

- Mode: scoped aggregate deepreview for accepted S1-S6 Atomic Source Fact Store / Composite Analysis View Split.
- Branch: `evidence-confirm-productionization`.
- Accepted commits/artifacts covered: plan `25fef99`, S1 `42f02e4`, S2A `ad9bf86`, S2B `961a7f7`, S3 `fa95cb6`, S4 `ea725b5`, S5 `29fbb79`, S6 `70eef36`, current control sync `42d4824`, and the S6 implementation/review/fix/rereview artifacts listed in the gate request.
- Included code/docs scope: `fund_agent/fund/source_facts.py`, `fund_agent/fund/processors/contracts.py`, `fund_agent/fund/data_extractor.py`, `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/extractors/performance.py`, `fund_agent/fund/extractors/manager_ownership.py`, `fund_agent/fund/processors/active_annual.py`, `fund_agent/fund/processors/fund_disclosure_processor.py`, `fund_agent/fund/chapter_facts.py`, `fund_agent/fund/evidence_confirm.py`, `fund_agent/fund/evidence_confirm_sources.py`, `fund_agent/fund/evidence_confirm_value_diagnostics.py`, `docs/design.md`, `fund_agent/fund/README.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and focused tests under `tests/fund/`.
- Excluded scope: unrelated dirty/untracked residue, live/PDF/repository/source-helper/parser/provider/LLM/product CLI execution, PR/remote state, staging, commit, push, merge, tag, release, and readiness mutation.
- Parallel review coverage: none.

## Findings

### F-01-未修复-中-Evidence Confirm 对 ambiguous bridge identity/derived-view target 未全部 fail closed

- **入口/函数**: `confirm_projection_evidence_v2()` / `summarize_value_match_diagnostics()` 经 `_resolved_fact_material_value()` 和 `_derived_view_for_fact()` 解析 bridge material value。
- **文件(行号)**: `fund_agent/fund/evidence_confirm.py:1886`, `fund_agent/fund/evidence_confirm.py:1893`, `fund_agent/fund/evidence_confirm.py:1991`; bridge 字段定义在 `fund_agent/fund/chapter_facts.py:188` 和 `fund_agent/fund/chapter_facts.py:189`。
- **输入场景**: 调用方传入一个 `ChapterFactProjection`，其中某个 `ChapterFactEntry` 同时带 `source_fact_ids=("fee_schedule.management_fee",)` 与 `derived_view_id="fee_schedule"`，或 `projection.derived_views` 中存在两个相同 `view_id="fee_schedule"` 但 value/dependency 不同的 `CompositeAnalysisView`。
- **实际分支**: `_resolved_fact_material_value()` 先判断 `fact.source_fact_ids`，只要长度为 1 就从 `projection.source_facts` 取值并 `return source_fact.value`；不会检查同一 fact 是否同时声明了 `derived_view_id`。若只走 derived path，`_derived_view_for_fact()` 使用 `next(...)` 返回第一个匹配 view，不检查 duplicate view_id。
- **预期行为**: S5 aggregate contract 和当前 control truth 要求 bridge material resolution 使用显式 `source_fact_ids` / `derived_view_id`，并在 missing/ambiguous bridge targets 上 fail closed。ambiguous bridge identity 或 duplicate derived view target 应返回 `_UNRESOLVED_FACT_MATERIAL`，让 E3 blocking issue 进入结果。
- **实际行为**: 同时存在 atomic id 与 derived view id 时，resolver 静默偏向 atomic source fact；重复 `derived_view_id` target 时，resolver 静默取第一个 view。该路径可以把 malformed/ambiguous projection 的 material value 当作可审计事实继续做 value_match，而不是 fail closed。
- **直接证据**: `ChapterFactEntry` dataclass 对 `source_fact_ids` 与 `derived_view_id` 没有互斥校验（`chapter_facts.py:188-189`）。`_resolved_fact_material_value()` 在 `source_fact_ids` 分支只校验长度是否为 1 和 source fact 是否存在（`evidence_confirm.py:1886-1892`），随后才检查 `derived_view_id`（`evidence_confirm.py:1893-1897`）。`_derived_view_for_fact()` 对 `projection.derived_views` 使用 `next((view for view in ...), None)`（`evidence_confirm.py:1991-1994`），没有检测 0/1/many 的 target cardinality。
- **影响**: malformed 或 future-produced ambiguous bridge projection 会绕过 S5 宣称的 fail-closed 语义；Evidence Confirm value_match、source materializer token scope 和 diagnostics 可能基于任意一个 bridge target 输出 pass/fail，造成审计结果不可解释。当前 `project_chapter_facts()` 生成路径通常不会制造重复 derived view 或双 bridge id，因此这是 bridge API/contract correctness blocker，不是已观察到的默认 facade 数据回归。
- **建议改法和验证点**: 在 resolver 层增加桥接互斥与唯一性校验：`source_fact_ids` 非空且 `derived_view_id is not None` 返回 unresolved；derived view lookup 改为收集匹配项并要求 exactly one；必要时在 `ChapterFactEntry.__post_init__` 或投影构造辅助函数中同步守住互斥不变量。新增 no-live 回归覆盖双 bridge id、duplicate `derived_view_id`、missing `source_fact_id`、missing `derived_view_id`，并验证 E3 blocking issue 和 diagnostics token_count 安全降级。
- **修复风险（低/中/高）**: 低。
- **严重程度（低/中/高/严重）**: 中。
- **Blocking**: 是。该 finding 直接命中本 aggregate gate 的 review focus 4：fail closed on missing/ambiguous bridge targets。

## Open Questions

- 无。

## Residual Risk

- Missing exact `_atomic.py` processor test paths are acceptable as a stale plan/test-path residual, not an aggregate blocker by themselves. Current checkout only has `tests/fund/processors/test_active_annual_processor.py` and `tests/fund/processors/test_fund_disclosure_processor.py`; the focused existing atomic/source-fact processor suite passed and covers the implemented paths.
- No live/PDF, repository/source-helper/parser, provider/LLM, product CLI, PR state, tag, release, or readiness evidence was run or reviewed by instruction. Release/readiness remains `NOT_READY`.
- Existing unrelated dirty/untracked residue was observed and left untouched. The modified plan artifact is not treated as proof beyond the accepted commit/artifact scope.

## Validation

- `git branch --show-current` -> `evidence-confirm-productionization`.
- `git status --short` showed existing unrelated dirty/untracked residue before this review; no staging/commit/push/PR/tag/release/readiness action was performed.
- `git log --oneline -20` confirmed the accepted commit chain through current control sync `42d4824`.
- `git show --stat --oneline --name-only 25fef99 42f02e4 ad9bf86 961a7f7 fa95cb6 ea725b5 29fbb79 70eef36 42d4824` confirmed the requested artifacts and touched surfaces.
- `rg --files tests/fund/processors | rg "test_(active_annual|fund_disclosure_processor)_atomic\.py|test_(active_annual_processor|fund_disclosure_processor)\.py"` -> only `tests/fund/processors/test_active_annual_processor.py` and `tests/fund/processors/test_fund_disclosure_processor.py` exist.
- `uv run pytest tests/fund/test_source_facts.py tests/fund/processors/test_active_annual_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_evidence_confirm_atomic.py -q` -> `243 passed in 0.91s`.
- `uv run pytest tests/fund/test_data_extractor.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py tests/fund/test_evidence_confirm_value_diagnostics.py -q` -> `180 passed in 1.00s`.
- `git diff --check` -> passed.

## Verdict

ATOMIC_SOURCE_FACT_STORE_AGGREGATE_DEEPREVIEW_FINDINGS_NEED_FIX_NOT_READY
