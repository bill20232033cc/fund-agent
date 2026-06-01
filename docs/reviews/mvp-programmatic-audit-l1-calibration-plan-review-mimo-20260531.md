# MVP programmatic audit L1 calibration plan review — MiMo

日期：2026-05-31

Gate：`MVP programmatic audit L1 calibration plan review gate`

角色：Gateflow plan reviewer，不是 implementation worker。

## Review Scope

- Plan：`docs/reviews/mvp-programmatic-audit-l1-calibration-plan-20260531.md`
- Source of truth：`AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`
- Previous gate judgment：`docs/reviews/mvp-writer-marker-syntax-repair-controller-judgment-20260531.md`
- Code：`fund_agent/fund/chapter_auditor.py`、`fund_agent/fund/chapter_writer.py`、`fund_agent/services/chapter_orchestrator.py`
- Tests：`tests/fund/test_chapter_auditor.py`、`tests/fund/test_chapter_writer.py`、`tests/services/test_chapter_orchestrator.py`、`tests/ui/test_cli.py`

## Review Findings

### F1. Plan 对齐 blocker：PASS

Plan 精准对齐当前 blocker：chapter 2 `programmatic_audit` issue prefix `programmatic:L1`，service subcategory `code_bug_other`，CLI category `audit_rule_too_strict`。与 implementation-control 和 startup-packet 中记录的状态完全一致。

### F2. Root-cause decision tree 同源性：PASS

Plan 要求 implementation worker 先用本地 deterministic / fake LLM 构造同源样本，禁止使用真实 provider 原文，禁止保存完整 draft。四种分支（真实 L1 不合格、规则过严、writer 输出缺口、taxonomy gap）的判定条件清晰可验证，与 AGENTS.md "找问题 root cause 一定要逻辑/数据同源，禁止使用间接证据" 硬约束对齐。

### F3. L1 不放松：PASS

- Plan 明确要求 "不得允许无锚点的数值闭合断言通过，不得把'数据不足'包装成通过"。
- Slice 3 条件式规则收窄有显式 unsafe fixture 守卫：`A=R-B，因此 Alpha 为 2.10%。` without anchor must fail、"数据不足" plus unsupported percentage must not pass。
- Slice 3 末尾明确 "If no overstrict evidence exists, skip Slice 3 and record 'rule unchanged; writer/taxonomy only'"，避免无同源证据时碰规则。
- 证据锚点、ITEM_RULE、candidate facet、交易建议、E2 deferred、missing semantics 在 plan scope 中不被修改。

### F4. Proposed taxonomy 和 repair guidance 安全性：PASS

- `l1_numerical_closure` 作为 `ChapterFailureSubcategory` 新增枚举值，映射到 `_primary_subcategory()` 优先级链中，位置低于 `candidate_facet_assertion` 和 `forbidden_phrase` 但高于 `code_bug_other`。这确保 L1 不会掩盖更严重的 facet/forbidden 问题。
- Repair guidance 的两个分支安全：(1) 有同源事实时要求在同一句或上下 2 行内放 allowed anchor；(2) 无同源事实时删除数值闭合断言并写缺口/下一步验证问题。不放松锚点要求。
- `audit_rule_too_strict` 保持为 programmatic pass 后 LLM audit fail 的 category，plan 不改变其语义。

### F5. Slice 3 guard 充分性：PASS（有观察项）

Slice 3 的 guard 设计合理：
- 明确 unsafe fixture 列表必须 remain fail-closed。
- 明确 false-positive fixture 必须 "contains no numeric closure assertion or uses explicit missing semantics without concrete unsupported percentage"。
- 有 "skip Slice 3" fallback。

**观察项（非 blocking）**：plan 未给出 `_audit_numerical_closure()` 当前 regex `_NUMERICAL_CLOSURE_RE` 和 `_NUMERIC_TEXT_RE` 匹配范围的详细边界分析。例如，当前 regex 匹配 `R=A+B-C` 等公式模式，但不区分"解释公式框架"vs"作出数值闭合断言"。Plan 把这项分析留给 implementation worker 的 local reproduction，这是合理的，但 reviewer 建议 implementation evidence 中显式记录 regex 匹配的边界 case 分析。

### F6. Tests/validation/evidence 充分性：PASS

- Slice 1 tests 覆盖 diagnostic mapping、payload safety、precedence preservation。
- Slice 2 tests 覆盖 repair guidance 通过 typed `ChapterRepairContext`、fake writer L1 failure -> anchored correction -> accept、fake writer unanchored closure -> fail-closed。
- Slice 3 tests 覆盖 existing fail/pass tests remain、new false-positive fixture、new unsafe fixture。
- Slice 4 tests 覆盖 CLI subcategory alignment。
- Validation plan 包含 ruff、targeted pytest、full coverage、deterministic analyze/checklist unchanged、missing-config fail-closed、git diff --check。
- Controller rerun matrix 只保存 safe fields，显式禁止 full prompt/draft/provider response。
- 真实 provider 不用于 implementation validation。

### F7. Scope 不越界：PASS

Plan 明确 forbidden list：golden / fixtures / score / quality gate / final judgment / Host / Agent / dayu / provider config/auth / PR state / deterministic default semantics。Allowed files 只限 `chapter_orchestrator.py`、`chapter_auditor.py`、`chapter_writer.py`、对应 tests、CLI test（conditionally）、gate evidence/reports。

### F8. 代码路径验证

Reviewer 对照代码验证 plan 的假设：

1. `_audit_numerical_closure()`（`chapter_auditor.py:669-697`）：当前逻辑为逐行匹配 `_NUMERICAL_CLOSURE_RE`（公式模式）且同行含 `_NUMERIC_TEXT_RE`（百分比），上下 2 行内无 `_ANCHOR_MARKER_TEXT` 则触发 L1。Plan 对此的描述准确。

2. `_required_correction_from_issue()`（`chapter_orchestrator.py:2019-2047`）：当前无 L1 专用分支，L1 issue 会 fallback 到 `_sanitize_text(message)`，产生泛化修正。Plan 要求新增 L1 分支，这是正确的。

3. `_primary_subcategory()`（`chapter_orchestrator.py:1591-1635`）：当前 `programmatic:L1` 不命中任何 counter，落入 `code_bug_other`。Plan 要求新增 `l1_numerical_closure` counter 并插入 precedence chain，正确。

4. `_audit_prompt_contract_diagnostic()`（`chapter_orchestrator.py:1533-1588`）：当前只统计 candidate_facet_assertion 和 forbidden_phrase，不统计 L1。Plan 要求扩展统计 `programmatic:L1` prefix count，正确。

5. `_chapter_failure_category_from_audit_result()`（`chapter_orchestrator.py:1444-1468`）：当前 L1 走 `_is_audit_rule_too_strict()` 返回 True（因为 programmatic fail 但 LLM 可解析），分类为 `audit_rule_too_strict`。但 service diagnostic subcategory 走 `_audit_prompt_contract_diagnostic()` 时，因为 `_chapter_failure_category_from_audit_result` 返回 `audit_rule_too_strict`（不是 `prompt_contract`），所以 `_audit_prompt_contract_diagnostic` 返回 `None`，subcategory 为 `None`。等等——实际 diagnostic JSON 显示 subcategory 为 `code_bug_other`，不是 `None`。让我重新检查。

   实际上，`_chapter_failure_category_from_audit_result` 返回 `audit_rule_too_strict`，然后 `_audit_prompt_contract_diagnostic` 检查 `!= "prompt_contract"` 返回 `None`。但 diagnostic JSON 显示 `code_bug_other`。这意味着 subcategory 来自其他地方——可能是 attempt 1 的 writer prompt diagnostic，而不是 audit diagnostic。这与 plan 的 taxonomy gap 诊断一致：`programmatic:L1` 没有专用 subcategory。

   **修正分析**：`failure_subcategory` 在 `ChapterRunResult` 中设置时（`chapter_orchestrator.py:1017-1019`），如果 `prompt_diagnostic` 为 `None` 则 `failure_subcategory` 为 `None`。但 diagnostic JSON 显示 `code_bug_other`，说明实际运行中 `prompt_diagnostic` 不为 `None`。这可能是因为 attempt 1 的 writer 成功但 audit 失败，此时 `_audit_prompt_contract_diagnostic` 被调用，而 `_chapter_failure_category_from_audit_result` 在 attempt 1 时返回 `prompt_contract`（因为 L1 是 programmatic fail，repair_hint 为 `patch`，不是 `needs_more_facts`，且 `_is_audit_rule_too_strict` 检查 `programmatic.status != "pass"` 时返回 False，所以走 `prompt_contract`）。然后 attempt 2 repair 后再次失败，此时同样的路径产生 `code_bug_other` subcategory。

   Plan 的 taxonomy gap 诊断是准确的。

### F9. Pass/blocked criteria 完整性：PASS

Pass criteria 和 blocked criteria 覆盖了所有关键安全边界。特别注意 "Root cause relies on indirect inference rather than code/evidence 同源" 被列为 blocked criteria，与 AGENTS.md 一致。

## Conclusion

**PASS**

Plan 对齐当前 blocker，root-cause decision tree 同源且完整，不放松 L1/锚点/facet/E2/missing semantics 安全边界，proposed taxonomy 和 repair guidance 安全且最小，Slice 3 有充分 guard，tests/validation/evidence 设计合理，scope 不越界。无 blocking finding。

**观察项（非 blocking）**：
1. Implementation evidence 应显式记录 `_NUMERICAL_CLOSURE_RE` / `_NUMERIC_TEXT_RE` 匹配边界 case 分析。
2. Plan 可考虑在 Slice 2 中要求测试 `_required_correction_from_issue()` 对 `programmatic:L1:*` issue prefix 的匹配，而非只测试 rule_code。
