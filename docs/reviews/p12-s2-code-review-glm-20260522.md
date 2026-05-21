# P12-S2 Code Review — AgentGLM（2026-05-22）

## Verdict

`PASS`

无阻塞 finding。实现精确匹配已接受 plan 的全部要求，scope 严格限定在 renderer/test/docs，未触碰任何约定边界。

## Scope

| 项目 | 内容 |
|---|---|
| Gate | `P12-S2 ITEM_RULE multi-anchor evidence boundary code review` |
| Plan truth | `docs/reviews/post-p12-s1-follow-up-planning-20260522.md` |
| Controller judgment | `docs/reviews/p12-s2-plan-review-controller-judgment-20260522.md` |
| Implementation artifact | `docs/reviews/p12-s2-implementation-20260522.md` |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Reviewer | AgentGLM |

## Changed Files

| File | Lines changed | Within scope? |
|---|---|---|
| `fund_agent/fund/template/renderer.py` | +4 / -2 | ✅ allowed |
| `tests/fund/template/test_renderer.py` | +115 / -0 | ✅ allowed |
| `fund_agent/fund/README.md` | +1 / -0 | ✅ allowed |
| `tests/README.md` | +2 / -2 | ✅ allowed |

No other files changed. No Service/UI/CLI/Engine/runtime/FundDocumentRepository/audit/quality gate/source repository files touched. `docs/design.md` and `docs/implementation-control.md` unchanged.

## Review Checklist

### 1. `_item_rule_evidence_bullet` 是否渲染全部去重 anchors，保留空锚点 exact text，稳定顺序，使用 `_body_anchor_reference` 和 `；`

**PASS。**

- `renderer.py:612-613`：空锚点路径保留 exact text `"- 证据边界：{_INSUFFICIENT_TEXT}，当前段落未携带独立证据锚点。"`，无变化。
- `renderer.py:614-617`：非空路径调用 `_dedupe_anchors(anchors)` 去重，对每个 anchor 调用 `_body_anchor_reference(anchor)`，用 `'；'.join(anchor_references)` 拼接，末尾 `。` 闭合。
- `_dedupe_anchors` 是已有 helper，保持输入顺序的去重语义不变；tuple comprehension 保持顺序稳定。
- `_render_tracking_error_segment` 在传入前也做了一次 `_dedupe_anchors`（line 582-587），helper 内部再次去重。这是已接受 plan §8.2 的显式决策："make the helper self-contained"，双重去重是无害 no-op。

### 2. 测试是否覆盖 concrete benchmark + RABC anchor text、empty anchor、duplicate anchor、single-anchor / no extra `> 📎 证据`

**PASS。**

四项覆盖均满足，且断言使用 concrete anchor reference text 而非弱字符串 smoke test：

| 测试函数 | 覆盖路径 | 断言质量 |
|---|---|---|
| `test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries` | 多锚点 + 单锚点 + 无额外 chapter evidence | 从 `_render_input` 提取 `benchmark.anchors[0]` 和 `rabc_attributions[0].anchors[0]`，通过 `_body_anchor_reference(...)` 生成 expected text，断言两者同时出现在 tracking_evidence_line；断言 `；` 存在；断言 index segment 单锚点无 `；` 且 count==1；断言无 `> 📎 证据` |
| `test_render_template_report_renders_item_rule_empty_anchor_boundary_for_present_identity` | 空锚点 identity_present 路径 | 用 `replace(...)` 清空 `benchmark.anchors` 和 `rabc_attributions[0].anchors`，断言 `identity_present` 不变，断言 evidence line exact 等于 `_ITEM_RULE_EMPTY_EVIDENCE_BOUNDARY` |
| `test_item_rule_evidence_bullet_deduplicates_duplicate_anchors` | 重复锚点去重 | 直接调用私有 `_item_rule_evidence_bullet((anchor, anchor))`，断言 exact 等于单锚点输出、count==1 |
| (集成在首个测试中) | 跟踪误差仍为数据不足 | 原有断言 `"跟踪误差：数据不足"` 保持不变 |

### 3. 是否保持 tracking error、index methodology、constituents 为数据不足，不把 anchors 说成 evidence sufficiency

**PASS。**

- `_render_tracking_error_segment`（line 569-595）text 无变化：`"- 跟踪误差：{_INSUFFICIENT_TEXT}，当前输入未抽取跟踪误差。"` 保持 exact。
- `fund_agent/fund/README.md` 新增行明确："这些锚点只表达 provenance，不证明跟踪误差、指数编制方法或成分股已经具备实质数据"。
- 测试仍断言 `"跟踪误差：数据不足"` 存在于 chapter_2。

### 4. 是否未改变 ITEM_RULE decisions/context、C2 audit、FQ5/quality gate、Service/UI/CLI/Engine/runtime/FundDocumentRepository/Dayu 边界

**PASS。**

- `item_rule_decisions` 和 `item_rule_audit_context` 的生成逻辑未被修改。
- `_render_tracking_error_segment` 的 heading、bullet 文本和 marker 均未变，仅 `_item_rule_evidence_bullet` 的非空输出从单锚点扩展为全锚点。
- 程序审计 C2 消费的是 marker presence/delete，marker 未变。`tests/fund/template/test_item_rules.py` 和 `tests/fund/audit/test_audit_programmatic.py` 均通过（48 passed，implementation report 记录）。
- 无任何 Service/UI/CLI/quality gate/FundDocumentRepository/Dayu 文件被改动。

### 5. README 是否描述当前行为且不过度承诺

**PASS。**

- `fund_agent/fund/README.md` 新增一行描述"在同一行渲染全部去重后的相关锚点"，并附带 provenance-only 免责声明。
- `tests/README.md` 在 renderer test 描述中添加"ITEM_RULE 多锚点证据边界"，在 test policy 中添加"ITEM_RULE 多锚点/空锚点/重复锚点证据边界"覆盖要求。
- 无未来承诺，无 tracking error/extractor 实现暗示。

## Findings

无阻塞或推荐 finding。

### Residual Risks（非 finding，继承自 plan 和 implementation report）

| Risk | Owner | Note |
|---|---|---|
| Multi-anchor display 不证明 evidence sufficiency | Future E1/E2/E3 audit slice | 正确：本 slice 只做 provenance display |
| Tracking error / index methodology / constituents 仍为数据不足占位 | Future extractor/calculation slice | Intentional non-goal |
| 长锚点列表可能需要未来截断/分组策略 | Future evidence-display UX slice | 当前 fixture 为小锚点集 |
| RR-13 duplicate `016492` | User / App source | 继续保持 human-owned |
| `docs/repo-audit-20260521.md` | Controller / user | 继续保持 excluded |

## Validation Evidence

Implementation report 记录：

- `pytest tests/fund/template/test_renderer.py`: `35 passed`
- `pytest tests/fund/template/test_item_rules.py tests/fund/audit/test_audit_programmatic.py`: `48 passed`
- `ruff check fund_agent/fund/template tests/fund/template`: passed
- `git diff --check HEAD`: passed
- Full suite `pytest`: `403 passed`

Controller 已确认以上全部通过。

## Completion

P12-S2 code review 完成。Verdict: `PASS`。
