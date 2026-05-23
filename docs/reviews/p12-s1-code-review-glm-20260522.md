# P12-S1 Code Review — AgentGLM（2026-05-22）

- **Gate**: `P12-S1 implementation`
- **Role**: AgentGLM independent code reviewer
- **Verdict**: **PASS**
- **Plan**: `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`
- **Controller judgment**: `docs/reviews/p12-s1-plan-review-controller-judgment-20260522.md`
- **Implementation artifact**: `docs/reviews/p12-s1-implementation-20260522.md`
- **Validation baseline**: targeted 81 passed, adjacent 43 passed, ruff passed, diff-check passed, full 401 passed（controller 本地确认）

---

## 1. Review Scope

审查对象为当前 workspace 未提交 diff，涉及 8 个文件，对照 `docs/design.md`、`docs/implementation-control.md`、P12-S1 plan / plan-review / implementation artifact，逐条检验 6 个重点问题。

| 文件 | 变更性质 |
|------|----------|
| `fund_agent/fund/template/item_rules.py` | 新增 `TemplateItemRuleAuditContext` 类型 |
| `fund_agent/fund/template/__init__.py` | 导出新类型 |
| `fund_agent/fund/template/renderer.py` | ITEM_RULE 决策解析、段落渲染、结果字段 |
| `fund_agent/fund/audit/audit_programmatic.py` | C2 ITEM_RULE 合规审计 |
| `tests/fund/template/test_renderer.py` | 六类基金渲染/删除矩阵 + 固定 bullet + 缺失路径 |
| `tests/fund/audit/test_audit_programmatic.py` | C2 ITEM_RULE 合规审计 7 个新测试 |
| `fund_agent/fund/README.md` | 行为描述更新 |
| `tests/README.md` | 测试描述更新 |

---

## 2. Findings

**无阻塞 finding。** 以下按严重度排列所有观察项。

### F1 — INFO：`_item_rule_evidence_bullet` 只引用首个锚点

| 字段 | 值 |
|------|-----|
| 严重度 | INFO |
| 文件 | `fund_agent/fund/template/renderer.py:598-600` |
| 类别 | 证据边界粒度 |

`_item_rule_evidence_bullet` 当锚点非空时只输出 `anchors[0]`。对于 `tracking_error_analysis` 段落，传入的锚点可能包含 benchmark + RABC 多个锚点，但只呈现第一个。这不违反 plan：plan 只要求"保留证据锚点或显式写未披露/数据不足"，且 tracking error 本身是数据不足占位。当前行为在 MVP 范围内可接受，但后续如有更多锚点需要独立呈现，应扩展为列表格式。

**Why**: 首个锚点足以标识来源类别，不伪造证据。plan §4.2 要求"benchmark anchors cannot prove constituents/methodology"，当前实现只引用首个不违反此约束。

**Residual risk**: 后续若 ITEM_RULE 段落引用多来源字段，单锚点呈现可能丢失部分 provenance。

### F2 — INFO：章节错配决策仍继续检查 marker

| 字段 | 值 |
|------|-----|
| 严重度 | INFO |
| 文件 | `fund_agent/fund/audit/audit_programmatic.py:556-576` |
| 类别 | 审计行为可预测性 |

`_audit_single_item_rule_decision` 在 `decision.chapter_id != rule.chapter_id` 时仍继续用 `decision.chapter_id` 查找 block 并检查 marker。由于章节错配本身已产生 C2 blocker issue，后续 marker 检查产生的额外 issue 不会放松约束。行为是 fail-closed 的，但审计消息可能略显冗余。

**Why**: 不影响正确性——错配已阻断。后续可考虑 `return issues` 提前退出以减少噪音，但不是 MVP 必需。

**Residual risk**: 审计 issue 数量在极端人为构造场景下可能略多于最小必要集，不掩盖任何问题。

### F3 — INFO：段落证据格式与章节级证据格式不同

| 字段 | 值 |
|------|-----|
| 严重度 | INFO |
| 文件 | `fund_agent/fund/template/renderer.py:585-600` |
| 类别 | 证据契约一致性 |

ITEM_RULE 段落使用 `- 证据边界：...` bullet 格式，而章节级证据使用 `> 📎 证据：...` quote 格式。implementation report 已显式说明这是为了避免"破坏每章一条正文证据行契约"。两个格式在语义上等价，且 plan §4.2 Slice 2 明确要求"do not remove existing chapter-level evidence line"。

**Why**: 设计意图清晰——每章只有一条 `> 📎 证据` line，ITEM_RULE 段落用 bullet 表达自身证据边界。不会混淆 P3 每章最小证据行审计。

**Residual risk**: 未来若 LLM/evidence audit 需要统一格式，需调整 `_item_rule_evidence_bullet` 输出。

---

## 3. Review by Review Criteria

### Q1: Renderer 是否只从 classified_fund_type 派生 ITEM_RULE decisions？

**通过。**

- `_resolve_item_rule_decisions()`（renderer.py:208-229）从 `structured_data.basic_identity.value["classified_fund_type"]` 派生。
- `facets=()` 硬编码，无 prose/fund name/category 推断。
- `identity_missing`：`basic_identity.value is None` → `(), "identity_missing"`。
- `identity_present`：有效 fund_type → 评估 decisions + `"identity_present"`。
- 无效/缺失 fund_type：`ValueError`，与 preferred_lens 行为一致。

### Q2: 身份缺失兼容性与 fail-closed？

**通过。**

- 空 decisions + `identity_missing`：renderer.py:224-225。
- Programmatic audit 跳过缺决策 issue：audit_programmatic.py:498-499。
- 身份存在但 fund_type 缺失/非法：renderer.py:227-228 `ValueError`。
- 测试 `test_render_template_report_missing_data_path_is_explicit_and_audit_compatible` 验证 `item_rule_decisions == ()` 和 `item_rule_audit_context == "identity_missing"`。
- 测试 `test_run_programmatic_audit_skips_missing_decision_issue_for_identity_missing_context` 验证审计通过。

### Q3: 条件段落确定性渲染？

**通过。**

- 固定 heading：`#### 指数编制规则与成分股`、`#### 基金经理投资哲学`、`#### 超额收益分年度拆解`、`#### 跟踪误差分析`。
- 固定 bullet keys（业绩基准引用/编制方法/成分股/披露策略/可验证动作/可用周期/分年度结论/跟踪误差/后续最小验证），无自由推断段落。
- benchmark anchors 只证明 benchmark/index reference：`_render_index_constituents_segment` 的编制方法和成分股 bullet 均为 `数据不足`。
- tracking error 是 data insufficient placeholder：`_render_tracking_error_segment` 全部 bullet 为 `数据不足` 和固定文本。
- 段落插入位置在章节 body 内、证据行之前：chapter 1（renderer.py:384-385）、chapter 2（renderer.py:435-436）。

### Q4: Programmatic C2 是否正确消费 renderer decisions/context？

**通过。**

- C2 消费 `input_data.item_rule_decisions` 和 `input_data.item_rule_audit_context`（audit_programmatic.py:140-145）。
- 只检查 `block.body_markdown`：audit_programmatic.py:578 `rendered_segment_present(block.body_markdown, rule)`。
- 不扫描全局 `report_markdown`。
- `identity_present` 空 decisions 触发 C2：audit_programmatic.py:500-506。
- 缺段（render marker missing）：audit_programmatic.py:580-586。
- 残留段（delete marker present）：audit_programmatic.py:588-594。
- 重复/未知/错章/不支持 status：audit_programmatic.py:512-521、544-554、556-566、596-603。
- 测试覆盖全部 7 个场景，含 matching-chapter-only 验证。

### Q5: 是否越界改动？

**未发现越界。**

- 无 Service/UI/Engine/Runtime 改动。
- 无 quality gate 行为改动。
- 无 LLM/Evidence Confirm/RepairContract/Host/tool loop 引入。
- 无 `docs/design.md`、`docs/implementation-control.md`、`docs/repo-audit-20260521.md` 改动。
- 变更限定在 Fund Capability template/audit + tests + README。

### Q6: 测试与 README 覆盖？

**通过。**

- 六类基金 parametrized 矩阵（index/active/bond/enhanced_index/qdii/fof），验证 render/delete 集合和 audit pass。
- 固定 bullet 和数据不足边界测试（enhanced_index 段落逐行断言）。
- 缺失身份路径测试。
- C2 审计 7 个新测试：identity-present 缺决策、identity-missing 兼容、render marker 缺失、delete marker 残留、重复/未知/错章、matching-chapter-only。
- 既有测试 helper `_rendered_audit_input` 和 full-pass 测试已更新为携带 renderer 产出的 decisions/context。
- README 更新描述当前行为，FQ5 仍只证明适用性元数据，renderer/audit 合规由 C2 验证。
- 无 FQ5 误写为证明 renderer ITEM_RULE 合规的措辞。

---

## 4. Residual Risks

| Risk | Severity | Description |
|------|----------|-------------|
| RR-P12-1 | INFO | `_item_rule_evidence_bullet` 只呈现首个锚点，多来源段落可能丢失部分 provenance。后续可扩展为列表。 |
| RR-P12-2 | INFO | tracking error 和 index constituents/methodology 仍为 `数据不足` 占位，需要后续 dedicated extractor 或计算输入才能填充实质内容。 |
| RR-P12-3 | INFO | FQ5 仍不证明最终报告语义正确；ITEM_RULE 段落 prose 为确定性 MVP 模板输出，不证明语义完整性。 |
| RR-P12-4 | INFO | 当前只有四条内置 conditional ITEM_RULE；后续新增规则需同步更新 `_render_item_rule_segment` 分发和对应测试。 |

---

## 5. Conclusion

**PASS** — 无阻塞 finding。实现完全匹配 plan 和 controller judgment 的契约约束：

1. Renderer 从 `classified_fund_type` + `facets=()` 派生 ITEM_RULE decisions，正确区分 `identity_missing` / `identity_present`，无效类型 fail closed。
2. 条件段落为固定 heading + 固定 bullet，无自由推断；benchmark anchors 不伪装为成分股/编制方法证据；tracking error 为数据不足占位。
3. C2 消费 renderer decisions/context，只检查匹配章节块 `body_markdown`；identity-present 空 decisions、缺段、残留、重复/未知/错章均 fail closed。
4. 无越界改动 Service/UI/CLI/quality gate/LLM/Evidence Confirm/Host/Engine/runtime/docs。
5. 测试覆盖六类基金渲染/删除矩阵和全部 C2 场景；README 正确描述当前行为且不误写 FQ5 为合规证明。

3 个 INFO finding 均为可观测性/可维护性观察，不影响正确性或安全性。
