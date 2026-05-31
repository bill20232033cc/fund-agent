# MVP programmatic audit L1 calibration code review (GLM)

日期：2026-05-31

Gate：`MVP programmatic audit L1 calibration gate`

角色：Gateflow code reviewer（GLM），不是 implementation worker。

## Verdict

**PASS**

## Review scope

本 review 覆盖以下已读 artifacts 和代码：

- Gate plan：`docs/reviews/mvp-programmatic-audit-l1-calibration-plan-20260531.md`
- Plan reviews：GLM PASS、MiMo PASS
- Implementation evidence：`docs/reviews/mvp-programmatic-audit-l1-calibration-implementation-evidence-20260531.md`
- 上一 gate controller judgment：`docs/reviews/mvp-writer-marker-syntax-repair-controller-judgment-20260531.md`
- 上一 gate diagnostic JSON：`reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/controller-real-provider-006597-2024-diagnostic.json`
- `fund_agent/services/chapter_orchestrator.py`（lines 88-98, 138-149, 197-244, 1540-1648, 2020-2061, 2410-2431）
- `fund_agent/fund/chapter_auditor.py`（lines 669-697 `_audit_numerical_closure`，确认未修改）
- `fund_agent/fund/chapter_writer.py`（lines 434-435 L1 anchor rule）
- `fund_agent/ui/cli.py`（lines 858-866 first-failed summary）
- `tests/services/test_chapter_orchestrator.py`（lines 799-1060, 1197-1232）
- `tests/fund/test_chapter_auditor.py`（lines 306-406）
- `tests/fund/test_chapter_writer.py`（lines 236-255）
- `tests/ui/test_cli.py`（lines 483-529, 1465-1483）
- `git diff --name-only HEAD`：确认额外 8 个文件来自 prior gates，不在本 gate scope 内

## Review checklist

### 1. 只新增 l1_numerical_closure taxonomy/diagnostic，未放松 _audit_numerical_closure 或 L1 anchor proximity

**PASS。**

- `ChapterFailureSubcategory` Literal 新增 `"l1_numerical_closure"`（orchestrator line 95），位于 `"forbidden_phrase"` 之后。
- `_PROGRAMMATIC_L1_PREFIX = "programmatic:L1"`（line 138）作为常量提取。
- `_audit_prompt_contract_diagnostic()`（lines 1540-1598）新增 `l1_numerical_closure_count` 统计，来源仅为 `prefix_counts.get(_PROGRAMMATIC_L1_PREFIX, 0)`（line 1566）。不读取 issue message、location 或 draft。
- `_primary_subcategory()`（lines 1601-1648）新增 `l1_numerical_closure_count` 参数和对应 counter entry（line 1641），precedence walk 正确。
- `_audit_numerical_closure()`（chapter_auditor.py lines 669-697）代码未被修改。Slice 3 按计划 skipped。
- L1 anchor proximity 仍为上下各 2 行 window（line 687：`max(0, index - 2)` ~ `min(len(lines), index + 3)`），未放宽。

### 2. Slice 3 skipped，unsafe L1 cases 仍 fail-closed

**PASS。**

Implementation evidence 明确记录 Slice 3 skipped，reason：无同源证据表明 `_audit_numerical_closure()` 过严。

4 个 fail/pass fixture 覆盖完整：

| Fixture | 预期 | 测试 |
|---------|------|------|
| `A=R-B，因此 Alpha 为 2.10%。` 无邻近 anchor | fail L1 | `test_programmatic_audit_fails_l1_formula_without_nearby_anchor_marker` (line 306) |
| `A-C 后的净超额为 1.20%。` 无邻近 anchor | fail L1 | `test_programmatic_audit_blocks_l1_a_minus_c_without_nearby_anchor_marker` (line 347) |
| "数据不足"+ 具体无锚点闭环百分比 | fail L1 | `test_programmatic_audit_blocks_l1_missing_wording_with_concrete_unanchored_percentage` (line 368) |
| 仅解释 `R=A+B-C` 框架、不写具体百分比 | pass | `test_programmatic_audit_allows_l1_formula_framework_without_concrete_percentage` (line 389) |

无任何 unsafe L1 case 被放松。

### 3. _SUBCATEGORY_PRECEDENCE 插入位置安全

**PASS。**

完整 precedence 序列（lines 139-149）：

```
response_length_incomplete > invalid_marker > unknown_anchor >
missing_required_marker > missing_structure > candidate_facet_assertion >
forbidden_phrase > l1_numerical_closure > code_bug_other
```

- `"l1_numerical_closure"` 位于 `"forbidden_phrase"` 之后、`"code_bug_other"` 之前。
- candidate facet 和 forbidden phrase 的优先级高于 L1，不会被掩盖。
- 测试 `test_candidate_facet_and_forbidden_phrase_precedence_beats_l1`（orchestrator tests line 897）验证三者共存时 `primary_subcategory == "candidate_facet_assertion"`，且 `l1_numerical_closure_count == 1` 正确计数。
- `_primary_subcategory()` precedence walk 对 `"code_bug_other"` 做 `continue`（line 1644），不会提前返回。

### 4. _required_correction_from_issue 的 L1 guidance 安全

**PASS。**

L1 分支（orchestrator lines 2056-2061）：

```python
if issue.rule_code == "L1" or _audit_issue_id_prefix(issue.issue_id) == _PROGRAMMATIC_L1_PREFIX:
    return (
        "修复模板第2章 R=A+B-C 数字闭环：公式/百分比闭合断言必须在同一句或上下2行内放入"
        " allowed anchor marker；若没有同源事实支撑 R、A、B、C 或 A-C 数值关系，删除具体数值闭合断言，"
        "改写为未披露/数据不足/下一步最小验证问题；不得编造 Alpha、Beta、Cost 或 R 数值。"
    )
```

安全性分析：

- 匹配条件双重覆盖：`rule_code == "L1"` 或 issue_id prefix 为 `programmatic:L1`。确保 chapter 级和 report 级 L1 issue 都能命中。
- 修正项确定性：
  - 要求放 anchor 在同句或上下 2 行内 ✓（与 auditor proximity window 一致）
  - 无同源事实时要求删除数值断言，改写为缺口 ✓
  - 明确禁止编造 R/A/B/C/A-C 数值 ✓
- 无 `extra_payload`：correction 通过 typed `ChapterRepairContext.required_corrections` 传递。
- 测试 `test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair`（line 1016）验证二轮修复通过。
- 测试 `test_required_corrections_are_deterministic_for_known_issue_patterns`（line 1197）验证 L1 correction 包含"第2章 R=A+B-C 数字闭环"和"不得编造 Alpha、Beta、Cost 或 R 数值"。
- 测试 `test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory`（line 1042）验证修复后仍无锚点时 fail-closed，`failure_subcategory == "l1_numerical_closure"`。

不鼓励编造数值，不放松 L1。

### 5. CLI/service taxonomy 一致，failed stdout empty/no fallback

**PASS。**

- Service 层 diagnostic 通过 `_serialize_diagnostic()`（lines 2410-2431）序列化，包含 `primary_subcategory` 和 `l1_numerical_closure_count`。
- CLI `_first_failed_summary()`（lines 850-868）直接读取 `failure_subcategory` 字段并打印，无特殊分支。
- CLI 测试 `test_analyze_cli_use_llm_l1_numerical_closure_fail_closed`（line 1465）断言：
  - `exit_code == 1` ✓
  - `stdout == ""` ✓
  - `first_failed_category=prompt_contract` ✓
  - `first_failed_subcategory=l1_numerical_closure` ✓
  - `first_failed_subcategory=unknown` 不出现 ✓
  - `first_failed_category=audit_rule_too_strict` 不出现 ✓
  - `analyze_called is False`（无 deterministic fallback）✓
- 之前 `code_bug_other` / `unknown` / `audit_rule_too_strict` 歧义已消除。

### 6. Serialization/secret safety

**PASS。**

- `ChapterPromptContractDiagnostic` 只保存枚举、计数和标量。dataclass docstring（lines 199-224）明确声明不保存 prompt、draft、provider response、audit raw response 或具体 anchor/facet/phrase 文本。
- `_serialize_diagnostic()` 输出为标量 dict（lines 2411-2431），不含任何文本内容。
- 测试 `test_l1_prompt_contract_serialization_exposes_safe_subcategory_only`（line 955）验证序列化结果：
  - 包含 `"programmatic:L1"` prefix ✓
  - 不包含 `"line:"` ✓
  - 不包含 `"Alpha 为 2.10%"` ✓
  - 不包含 `"A=R-B"` ✓
  - 不包含 `"draft_markdown"` ✓
  - 不包含 `"user_prompt"` ✓
- 测试 `test_sanitized_prompt_contract_serialization_excludes_raw_payloads`（line 930）检查 system_prompt、user_prompt、draft_markdown、raw_response、provider_response、accepted_draft.markdown、Authorization、Bearer、sk- 均不出现。
- Implementation evidence secret scan：PASS。

### 7. Deterministic analyze/checklist 不变

**PASS。**

- `_audit_numerical_closure()` 代码未修改（verified：chapter_auditor.py diff 不涉及 lines 669-697）。
- Implementation evidence 记录 `uv run fund-analysis analyze 006597 --report-year 2024` exit 0 和 `uv run fund-analysis checklist 006597 --report-year 2024` exit 0。
- L1 calibration 只新增 taxonomy、repair guidance 和 writer prompt rule，不影响 deterministic 路径。
- Missing-config `--use-llm` with LLM env unset 仍 fail-closed exit 1，stdout empty。

### 8. Scope 不碰 forbidden files

**PASS。**

Implementation evidence 声称修改 6 个文件 + 1 个 evidence doc：

| 文件 | 属于本 gate scope |
|------|------------------|
| `fund_agent/services/chapter_orchestrator.py` | ✓ L1 taxonomy + diagnostic + repair |
| `fund_agent/fund/chapter_writer.py` | ✓ L1 anchor rule |
| `tests/fund/test_chapter_auditor.py` | ✓ L1 fail/pass fixtures |
| `tests/fund/test_chapter_writer.py` | ✓ L1 prompt rule test |
| `tests/services/test_chapter_orchestrator.py` | ✓ L1 diagnostic + precedence + repair + serialization tests |
| `tests/ui/test_cli.py` | ✓ CLI L1 fail-closed test |

`git diff --name-only HEAD` 显示 16 个文件变更，其中额外 8 个（`llm_provider.py`、`llm config`、`test_llm_config.py`、`test_llm_provider.py`、`implementation-control.md`、`current-startup-packet.md`、`config/README.md`、`fund/README.md`）属于 prior gates，不在本 gate scope。

未触碰 forbidden files：golden、fixtures（共享）、score、quality gate、final judgment、Host/Agent/dayu、provider config/auth、PR state。

`chapter_auditor.py` 的 diff 包含 `_required_output_marker` import 和 `_facet_asserted()` refactoring，经核实属于 prior gate（writer marker syntax repair），非本 gate 变更。`_audit_numerical_closure()` 代码行 669-697 未被修改。

## Minor observations（非 blocking）

1. **Writer prompt L1 rule 作用域**：`"第2章 R=A+B-C 数字闭环"` 规则在所有章节的 writer prompt 中出现（chapter_writer.py lines 434-435），而非仅 chapter 2。这无害——规则文本明确指向第 2 章内容，且 auditor 对所有章节检查 L1——但略显冗余。非 blocking，可在后续 prompt 优化时考虑条件注入。

2. **`_primary_subcategory()` 尾行冗余**：line 1648 `return "code_bug_other" if not has_any_counter else "code_bug_other"` 两个分支返回相同值，`has_any_counter` 在此路径无区分效果。非 blocking，不影响正确性。

## Blocking findings

无。

## Conclusion

实现完整覆盖 plan 的 Slice 1（L1 diagnostic taxonomy）、Slice 2（L1 repair guidance）和 Slice 4（CLI/service taxonomy alignment）。Slice 3 按计划 skipped，理由充分且 unsafe L1 cases 全部 fail-closed。

`_SUBCATEGORY_PRECEDENCE` 插入位置安全，不掩盖 candidate facet 或 forbidden phrase。`_required_correction_from_issue()` 的 L1 guidance 是确定性的安全修正，不鼓励编造数值。CLI/service taxonomy 对齐，failed stdout empty 且无 deterministic fallback。Serialization 不泄露 secret、prompt、draft 或 response。Deterministic analyze/checklist 语义不变。Scope 严格限制在 plan 允许的文件。

**PASS。**
