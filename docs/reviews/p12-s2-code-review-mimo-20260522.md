# P12-S2 Code Review — AgentMiMo（2026-05-22）

- **Gate**: `P12-S2 ITEM_RULE multi-anchor evidence boundary code review`
- **Approved plan**: `docs/reviews/post-p12-s1-follow-up-planning-20260522.md`
- **Implementation artifact**: `docs/reviews/p12-s2-implementation-20260522.md`
- **Controller judgment**: `docs/reviews/p12-s2-plan-review-controller-judgment-20260522.md`

## Verdict

`PASS`

## Review Scope

审查当前 workspace 未提交 diff（4 文件，+124 / -4）：

- `fund_agent/fund/template/renderer.py`（+8 / -2）
- `tests/fund/template/test_renderer.py`（+115 / 0）
- `fund_agent/fund/README.md`（+1 / 0）
- `tests/README.md`（+4 / -2）

## Checklist Results

### 1. `_item_rule_evidence_bullet` 渲染全部去重 anchors

**PASS**

`renderer.py:611-616`：空 anchors 路径保留精确文本 `- 证据边界：数据不足，当前段落未携带独立证据锚点。`；非空路径调用 `_dedupe_anchors(anchors)` 后对每个 anchor 调用 `_body_anchor_reference(anchor)`，以 `；` join。`_dedupe_anchors`（`renderer.py:1181`）使用 seen-set + append-first 策略，保持输入顺序稳定。

### 2. 测试覆盖质量

**PASS**

四个新增测试均为 concrete 断言，非弱字符串 smoke test：

| 测试 | 覆盖内容 | 断言方式 |
|---|---|---|
| 多锚点（`test_render_template_report_renders_item_rule_segments_with_fixed_bullets_an_evidence_boundaries` 扩展） | `enhanced_index` 跟踪误差段同时有 benchmark + RABC anchors | 同一 `tracking_evidence_line` 包含 `benchmark_reference` 和 `rabc_reference` 具体文本 + `；`；单锚点 `index_evidence_line` 恰好出现 1 次 `benchmark_reference` 且无 `；`；`index_segment` 无 `> 📎 证据` |
| 空锚点（`test_render_template_report_renders_item_rule_empty_anchor_boundary_for_present_identity`） | `index_fund` identity_present 下清空 benchmark + attribution anchors | `evidence_line == _ITEM_RULE_EMPTY_EVIDENCE_BOUNDARY` + `item_rule_audit_context == "identity_present"` |
| 重复锚点（`test_item_rule_evidence_bullet_deduplicates_duplicate_anchors`） | 直接 helper 测试 `(anchor, anchor)` | `evidence_line.count(reference) == 1` |
| 单锚点无额外引用 | 同多锚点测试中 `index_segment` 断言 | `assert not any(line.startswith("> 📎 证据") for line in index_segment)` |

### 3. 数据不足语义保持

**PASS**

- 跟踪误差：`renderer.py` 未改变 `_render_tracking_error_segment` 文本，跟踪误差仍为 `数据不足，当前输入未抽取跟踪误差。`
- 指数编制方法：仍为 `数据不足，当前输入未抽取指数编制方法。`
- 成分股：仍为 `数据不足，当前输入未抽取持仓明细。`
- anchors 只表达 provenance，不证明 evidence sufficiency。README 明确声明。

### 4. 未改变边界

**PASS**

- 未修改 `ITEM_RULE` decisions/context、C2 audit、FQ5/quality gate
- 未修改 Service/UI/CLI/Engine/runtime/FundDocumentRepository/Dayu 边界
- 未修改 `docs/design.md`、`docs/implementation-control.md`、`docs/repo-audit-20260521.md`
- 变更文件严格在 allowed 文件清单内（renderer.py、test_renderer.py、fund/README.md、tests/README.md）

### 5. README 描述当前行为

**PASS**

- `fund_agent/fund/README.md`：新增一句描述多锚点渲染 + provenance 声明，未过度承诺
- `tests/README.md`：新增 ITEM_RULE 多锚点证据边界覆盖描述，术语与 plan 一致

## Validation

| 命令 | 结果 |
|---|---|
| `pytest tests/fund/template/test_renderer.py` | 35 passed |
| `pytest tests/fund/template/test_item_rules.py tests/fund/audit/test_audit_programmatic.py` | 48 passed |
| `ruff check fund_agent/fund/template tests/fund/template` | All checks passed |
| `git diff --check HEAD` | passed |

## Findings

无 blocking findings。

## Residual Risks

1. **Private helper import in tests**：测试直接 import `_body_anchor_reference` 和 `_item_rule_evidence_bullet`。plan 明确允许此路径（§9: "direct access to `_item_rule_evidence_bullet` is allowed only inside `tests/fund/template/test_renderer.py`"）。当前无实际风险，但后续若 helper 重构需同步更新测试 import。

2. **Long anchor list truncation**：当前 deterministic fixtures anchor 数量小（≤3）。未来真实数据可能产生更长 anchor 列表；plan 已将 truncation/grouping policy 标记为 future scope，当前不阻塞。

3. **`_dedupe_anchors` 双重调用**：`_render_tracking_error_segment` 已在调用前去重 anchors，`_item_rule_evidence_bullet` 内部再次调用 `_dedupe_anchors`。幂等无副作用，但构成冗余调用。不阻塞。

## Conclusion

P12-S2 实现严格遵循 approved plan，四项重点审查均通过。`_item_rule_evidence_bullet` 正确渲染全部去重 anchors，测试覆盖 concrete anchor 文本、空锚点、重复锚点和单锚点路径，数据不足语义保持不变，边界未被突破。建议接受。
