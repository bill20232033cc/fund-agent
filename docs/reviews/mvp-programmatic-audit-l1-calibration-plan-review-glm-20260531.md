# MVP programmatic audit L1 calibration plan review (GLM)

日期：2026-05-31

Gate：`MVP programmatic audit L1 calibration plan review gate`

角色：Gateflow plan reviewer（GLM），不是 implementation worker。

## Conclusion

**PASS。**

Plan 可以进入 implementation gate，无需 blocking 修正。

以下记录 7 项 review 重点的逐项判断和 3 项非阻塞观察。

## Review 重点逐项判断

### 1. Plan 是否对齐当前 blocker chapter 2 programmatic_audit issue prefix programmatic:L1

**对齐。** 同源证据链：

- `current-startup-packet.md`：下一入口为 `MVP programmatic audit L1 calibration gate`；最新 service diagnostic 为 chapter 2 `programmatic_audit` with issue prefix `programmatic:L1`，subcategory `code_bug_other`。
- Diagnostic JSON（`reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/controller-real-provider-006597-2024-diagnostic.json`）：chapter 2 `failure_category: "prompt_contract"`，`failure_subcategory: "code_bug_other"`，`issue_id_prefix_counts: {"programmatic:L1": 2}`，candidate_facet / forbidden_phrase / invalid_marker / unknown_anchor counts 均为 0。
- 上一 gate controller judgment（`docs/reviews/mvp-writer-marker-syntax-repair-controller-judgment-20260531.md`）：确认 writer marker syntax repair 已 accepted locally，当前主 blocker 前进到 chapter 2 `programmatic:L1`，不是 provider config/auth。

Plan 的 Goal、Direct Evidence、Root-cause Decision Tree 和 Implementation Slices 均锚定这一 blocker，没有偏移。

### 2. 是否用代码/evidence 同源区分真实 L1 不合格、规则过严、writer 输出缺口、taxonomy gap

**充分。** Root-cause Decision Tree 按四分支同源定位：

1. 真实 L1 数值/逻辑闭合不合格 → 保持 fail-closed，增加 subcategory + repair guidance。
2. Audit rule 对真实 provider 输出过严或缺 missing semantics → 只允许收窄触发条件或加 guard，需 regression 证明 unsafe case 仍触发。
3. Writer output 缺 L1 所需结构/数值关系 → 补 writer prompt / repair_context，不放松 auditor。
4. Diagnostic taxonomy gap → 新增 `l1_numerical_closure` subcategory，同步 CLI。

Plan 要求 implementation worker 先用本地 deterministic / fake LLM 构造同源样本，不使用真实 provider 原文。这符合 AGENTS.md "root cause 必须逻辑/数据同源，禁止间接证据" 的硬约束。

代码同源验证：`_audit_numerical_closure()`（`chapter_auditor.py:669-697`）在 line 匹配 `_NUMERICAL_CLOSURE_RE`（R=A+B-C / A=R-B / A-C）且同 line 含 `_NUMERIC_TEXT_RE`（百分比）时，检查上下各 2 行内是否含 `<!-- anchor:`。当前 `_audit_prompt_contract_diagnostic()`（`chapter_orchestrator.py:1533-1588`）已经把 `programmatic:L1` 记入 `issue_id_prefix_counts`，但 `_primary_subcategory()`（`chapter_orchestrator.py:1591-1635`）没有 L1 对应 counter，所以落入 `code_bug_other`。Plan 准确识别了这个 taxonomy gap。

### 3. 是否不放松 L1、证据锚点、ITEM_RULE、candidate facet、交易建议、E2 deferred、missing semantics

**不放松。** 逐项确认：

- **L1 fail-closed**：Stop conditions 明确要求"不得把弱证据包装成 L1 通过"；Slice 1 只改 taxonomy，不改 pass/fail 行为；Slice 2 只改 repair guidance；Slice 3 条件式收窄保留 unsafe examples。
- **证据锚点**：`_audit_anchor_refs()` / `_audit_numerical_closure()` 的 anchor proximity 逻辑未在 plan 的 Allowed implementation files 中被放松。
- **ITEM_RULE**：不在 Allowed files 范围。
- **Candidate facet**：Plan 的 Blocked criteria 明确禁止修改 candidate facet；`_SUBCATEGORY_PRECEDENCE` 中 `candidate_facet_assertion` 优先于 `l1_numerical_closure`。
- **交易建议**：`_FORBIDDEN_PHRASES` 不在 Allowed files 范围。
- **E2 deferred**：Plan 的 Explicitly forbidden 列表明确排除。
- **Missing semantics**：Stop conditions 明确要求"不得放松 missing semantics"。

### 4. Proposed l1_numerical_closure taxonomy 和 repair guidance 是否安全且最小

**安全且最小。**

**Taxonomy（Slice 1）**：

- 新增 `l1_numerical_closure` 到 `ChapterFailureSubcategory` Literal —— 这是一个精确诊断标签，不是放松。
- 在 `_primary_subcategory()` 中 L1 beat `code_bug_other` 但不 beat `candidate_facet_assertion` / `forbidden_phrase` —— 这合理，因为 L1 是 programmatic audit issue，其诊断优先级应低于更高安全级别的 facet / forbidden phrase。
- Payload safety 保留：只存 prefix counts 和 scalar counters，不存 issue suffix、location raw text、draft、prompt 或 response。

**Repair guidance（Slice 2）**：

- L1 branch 在 `_required_correction_from_issue()` 中给出确定性修正指令："公式/百分比闭合断言必须在同句或上下 2 行内放 allowed anchor marker；无同源事实支撑时删除数值闭合断言并写缺口/下一步验证问题；不得编造 Alpha/Beta/Cost/R 数值。"
- 当前 `_required_correction_from_issue()`（`chapter_orchestrator.py:2019-2047`）没有 L1 分支，L1 issue fallback 到 `_sanitize_text(message)` —— 这是一个脱敏但非确定性的 correction，修复合理。
- Repair context 通过 typed `ChapterRepairContext` 传递，不通过 `extra_payload`，符合 AGENTS.md 硬约束。

### 5. Slice 3 条件式规则收窄是否有足够 guard，不会误放无锚点数值闭合

**足够。** Guard 层次：

1. **前置条件**：只有"同源本地 reproduction 证明当前 L1 rule is too broad"时才允许 Slice 3。
2. **允许收窄范围**：只允许调整 `_audit_numerical_closure()` trigger conditions for "clearly non-assertive formula mentions or explicit missing/gap wording"。
3. **Unsafe examples 必须保持 blocked**：
   - `A=R-B，因此 Alpha 为 2.10%。` without nearby anchor → must fail。
   - Numeric closure with unknown anchor → must fail through E1/L1。
   - "数据不足" plus concrete unanchored closure percentage → must not pass。
4. **Skip 条件**：If no overstrict evidence exists → skip Slice 3 and record "rule unchanged"。

三层 guard（前置条件 + 收窄范围 + regression test）足以防止误放。

非阻塞观察：Slice 3 中 "clearly non-assertive formula mentions" 的精确判定标准需要在 implementation 时用具体 test fixture 定义。建议 implementation evidence 包含至少以下 test cases：

- 公式框架解释 + 百分比 + 明确"数据不足"否定断言 → 预期 pass
- 公式框架解释 + 百分比 + 无否定/否定不明确 → 预期 fail
- 具体数值闭合断言 + 百分比 + 无 anchor → 预期 fail（已有）

### 6. Tests/validation/real provider evidence 是否足够且脱敏

**足够且脱敏。**

- 每个 Slice 有具体 test 要求：Slice 1 需 programmatic L1 → `l1_numerical_closure` subcategory 映射 + payload 不含敏感文本；Slice 2 需 L1-specific correction + writer repair fail-closed + fail-closed after repair；Slice 3 需 false-positive fixture pass + unsafe fixture fail-closed；Slice 4 需 CLI subcategory 一致。
- Validation Plan 包含 ruff check、targeted pytest、full coverage（≥50% gate）、deterministic `analyze`/`checklist`、missing-config smoke、`git diff --check`。
- Controller Real-provider Rerun Matrix 明确列出 allowed safe fields vs must-not-store fields。
- Blocked criteria 明确要求"If any complete prompt/draft/provider response is persisted, this gate is blocked even if tests pass"。

### 7. Scope 是否不碰 golden/fixtures/score/quality gate/Host/Agent/dayu/provider config/PR

**不碰。** Allowed implementation files 精确限定为 `chapter_orchestrator.py`、`chapter_auditor.py`、`chapter_writer.py` 和对应 tests。Explicitly forbidden 列表包含 golden/fixtures/score/quality gate/final judgment/Host/Agent/dayu/provider config/auth/PR state。Validation Plan 包含 deterministic `analyze`/`checklist` 不变验证。

## 非阻塞观察

### N1: `_SUBCATEGORY_PRECEDENCE` 插入位置应显式确认

Plan 说"L1 beats `code_bug_other` but does not beat candidate facet / forbidden phrase precedence"。当前 `_SUBCATEGORY_PRECEDENCE`（`chapter_orchestrator.py:137-146`）为：

```python
_SUBCATEGORY_PRECEDENCE = (
    "response_length_incomplete",
    "invalid_marker",
    "unknown_anchor",
    "missing_required_marker",
    "missing_structure",
    "candidate_facet_assertion",
    "forbidden_phrase",
    "code_bug_other",
)
```

Implementation 时应在 `"forbidden_phrase"` 和 `"code_bug_other"` 之间插入 `"l1_numerical_closure"`，或在 `_audit_prompt_contract_diagnostic()` 中用 L1 prefix count 直接覆盖 subcategory。Plan 意图清晰，但 implementation worker 应显式记录插入位置和理由。

### N2: CLI/service taxonomy 不一致的 root cause 应在 implementation 时定位

Controller judgment 报告 CLI stderr first-failed category 为 `audit_rule_too_strict`、subcategory 为 `unknown`，但 diagnostic JSON 的 `first_failed` 显示 `failure_category: "prompt_contract"`、`failure_subcategory: "code_bug_other"`。两者不一致。

Plan 的 Slice 4 要求对齐，但没有指定不一致的 root cause。Implementation 时应先定位 CLI 输出 category 的代码路径（可能使用 `stop_reason` 映射而非 `failure_category`），再决定修正在 CLI 侧还是 diagnostic 侧。

### N3: 现有 L1 test 覆盖仅 2 个 case

`test_chapter_auditor.py` 目前只有 `test_programmatic_audit_fails_l1_formula_without_nearby_anchor_marker` 和 `test_programmatic_audit_allows_l1_formula_with_nearby_anchor_marker` 两个 L1 test。Implementation 时建议补充：

- 多行公式 + 百分比在不同行的边界 case（当前 `_NUMERICAL_CLOSURE_RE` 和 `_NUMERIC_TEXT_RE` 要求同一 line 同时匹配）
- 不同公式形态（`A-C`、`R=A+B-C`）的触发覆盖
- anchor marker 在 proximity window 边界（上 2 行 / 下 2 行）的 pass case

## Self-check

- 本 review 只读取了 `AGENTS.md`、`current-startup-packet.md`、`implementation-control.md`、plan、上一 gate controller judgment、diagnostic JSON、`chapter_auditor.py`、`chapter_orchestrator.py`、`chapter_writer.py` 和相关 test 代码。
- 没有修改任何代码。
- 没有运行真实 provider。
- 没有保存完整 prompt、draft、provider response 或 API key。

## Next Minimal Entry

Plan review PASS → start `MVP programmatic audit L1 calibration implementation gate`。
