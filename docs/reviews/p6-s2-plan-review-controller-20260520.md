# P6-S2 Plan Review Controller - 2026-05-20

## Scope

- Reviewed plan: `docs/reviews/p6-s2-renderer-contract-alignment-plan-20260520.md`
- Design truth: `docs/design.md`
- Control doc: `docs/implementation-control.md`
- Code facts checked:
  - `fund_agent/fund/template/renderer.py`
  - `fund_agent/fund/template/contracts.py`
  - `tests/fund/template/test_renderer.py`
  - `fund_agent/fund/audit/audit_programmatic.py`

## Assumptions Tested

- P6-S2 should align renderer chapter titles with the P6-S1 manifest without changing report Markdown semantics.
- P6-S2 should expose chapter blocks for P6-S3 while not implementing contract audit.
- Audit `_REQUIRED_CHAPTER_TITLES` drift should remain P6-S3 scope, not be pulled into P6-S2.
- Adding `TemplateRenderResult.chapter_blocks` should not break direct construction sites.

Code fact: `TemplateRenderResult(...)` is only directly constructed in `renderer.py`, so adding a required field is low-risk if implementation updates that single construction site and keeps existing fields unchanged.

## Findings

No blocking findings.

### 001-需修订-[低]-新增 `TemplateRenderResult` 字段的兼容性约束应写得更明确

- **位置**: `Target Public Contract` / `Extend TemplateRenderResult`
- **问题类型**: 契约缺失 / 测试缺口
- **当前写法**: Plan 要求新增 `chapter_blocks: tuple[RenderedChapterBlock, ...]`，并说明 existing fields must remain unchanged。
- **反例/失败场景**: Implementation agent 若把 `chapter_blocks` 插入到 dataclass 字段最前面，或让 tests 只走 `render_template_report(...)` happy path，可能不会注意到 dataclass positional construction 的兼容语义变化。
- **为什么有问题**: 当前代码事实显示 repo 内只有 renderer 直接构造 `TemplateRenderResult(...)`，所以风险不高；但这是公共导出类型，plan 应明确减少不必要的 public contract churn。
- **直接证据**: `rg "TemplateRenderResult\\(" .` 只命中 `fund_agent/fund/template/renderer.py:128`；plan 已要求 public export。
- **影响**: 低。主要是外部调用方若使用 positional dataclass construction，字段顺序变化可能造成兼容性噪音。
- **建议改法和验证点**: 修订 plan：`chapter_blocks` 应追加到 `TemplateRenderResult` 现有字段之后；implementation tests 应断言 `result.audit_input.report_markdown == result.report_markdown` 和现有 fields 保持可访问。无需增加反向兼容 shim。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Architecture Boundary Review

Pass. Plan 把 renderer alignment 限定在 Capability `template/` 内，明确不改 Service/UI、不改 quality gate、不实现 audit。它识别到 `audit_programmatic.py` 仍有独立 title tuple，但把 contract-aware audit 留给 P6-S3，符合 phase backlog。

## Overengineering / Overcoupling Review

Pass with minor risk. `RenderedChapterBlock` 是合理的最小 surface：它只绑定 rendered Markdown 与 `ChapterContract`，没有把 audit result、item-rule state 或 quality-gate metadata 塞进 renderer。Plan 没有引入新 parser module，避免为当前 renderer-owned Markdown 过度拆层。

## Test Review

Pass. Plan 保留现有 renderer Markdown compatibility tests，并新增 malformed splitter fail-closed tests。测试重点覆盖标题来源、章节块结构、appendix 边界和 audit input 兼容，足以保护 P6-S2 目标。

## Open Questions

- Character offsets are not required in P6-S2. Exact block markdown is sufficient for P6-S3 deterministic audit; offsets can be added later if an accepted audit plan proves a need.

## Residual Risks

- `audit_programmatic.py` 的 `_REQUIRED_CHAPTER_TITLES` 仍与 contract manifest 并存。Tracking destination: P6-S3 contract audit plan/review.
- Source template typo `危级/降级阈值` remains tracked by RR-19 and should not be fixed opportunistically in P6-S2.

## Conclusion

`pass-with-minor-plan-patch`.

The plan is safe to hand to implementation after the low-severity `TemplateRenderResult` field-order/test wording is patched.
