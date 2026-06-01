# MVP writer prompt contract diagnostic narrowing plan review (MiMo)

日期：2026-05-31

Reviewer：MiMo plan reviewer

Plan artifact：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-plan-20260531.md`

## Review scope

读取了以下文件：

- `AGENTS.md`（规则真源）
- `docs/current-startup-packet.md`（短启动入口）
- `docs/implementation-control.md`（实施总控）
- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-controller-judgment-20260531.md`（上一 gate controller judgment）
- `fund_agent/fund/chapter_writer.py`（writer primitive）
- `fund_agent/fund/chapter_auditor.py`（auditor primitive，部分）
- `fund_agent/services/chapter_orchestrator.py`（orchestrator）
- `fund_agent/ui/cli.py`（CLI 入口）
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/controller-real-provider-006597-2024-diagnostic.json`（现有诊断证据目录）

## Verdict

**PASS**

Plan 可进入 implementation。以下按 review 重点逐项说明。

## 1. Gate 目标满足度

Plan 正确对齐当前 gate 目标：把真实 provider 的 `prompt_contract` / `llm_contract_violation` 收窄到唯一可修复子类。

- 当前 blocker 已精确定位为 writer `prompt_contract`（controller judgment 证据：chapter 1 accepted / chapter 2 blocked，CLI rerun first failed chapter 1）。
- Plan 设计了 8 个子类，按确定性优先级选择主分类，与 controller judgment 的下一步最小入口完全一致。
- 两类可接受结果（full smoke pass 或 唯一子类 + 最小修复入口）明确且可验证。

## 2. 敏感信息保护

Plan 在多处明确禁止保存完整 prompt/draft/provider response/API key/Auth header：

- "Explicitly disallowed implementation shortcuts" 列表完整（Section "Minimal Code Touches"）。
- 证据 JSON schema 只包含 typed counts、response_chars、max_output_chars、finish_reason、accepted_draft_present 布尔值。
- `issue_id_prefix_counts` 明确排除 raw anchor ids、missing reason values、facet text、forbidden phrase text。
- CLI stderr 只输出 scalar `first_failed_subcategory=<value>`，不输出 issue message。
- Completion Report Format 明确排除 prompt body / draft body / provider response body / env dump / secret-bearing logs。
- Validation Matrix 包含 secret scan 检查项。

**无发现**。

## 3. Taxonomy 完整性

8 个子类足以区分当前已知的 `prompt_contract` 失败模式：

| 子类 | 对应现有 issue_id / reason | 代码来源验证 |
|---|---|---|
| `missing_structure` | `missing_required_structure`（reason） | `chapter_writer.py:892-919` `_required_structure_issues()` |
| `missing_required_marker` | `missing_required_output_marker`（reason） | `chapter_writer.py:922-947` `_required_output_marker_issues()` |
| `unknown_anchor` | `unknown_anchor`（reason） | `chapter_writer.py:966-994` `_parse_anchor_markers()` |
| `invalid_marker` | `writer:invalid_anchor_marker:*` / `writer:invalid_missing_marker:*` / `writer:unknown_missing_reason:*` / `writer:evidence_line_without_anchor_marker`（issue_id prefix，reason=`llm_contract_violation`） | `chapter_writer.py:857-889` `_invalid_marker_issues()`；`chapter_writer.py:997-1029` `_parse_missing_markers()`；`chapter_writer.py:1032-1054` `_evidence_line_issues()` |
| `candidate_facet_assertion` | programmatic audit issue（post-draft） | `chapter_auditor.py` programmatic audit C2 rule |
| `forbidden_phrase` | `writer:forbidden_phrase:*`（issue_id prefix，reason=`llm_contract_violation`）或 audit forbidden content | `chapter_writer.py:1057-1078` `_forbidden_phrase_issues()`；`chapter_auditor.py` programmatic audit |
| `response_length_incomplete` | `response_too_long` / `response_incomplete`（reason）或 `finish_reason` in INCOMPLETE_FINISH_REASONS | `chapter_writer.py:816-831` |
| `code_bug_other` | 异常 / unmapped issue id / no counters | orchestrator fallback |

**无发现**。现有 issue id 和 reason 已足够区分所有子类，无需新增 writer parser 逻辑（除暴露 typed 字段外）。

## 4. 安全边界

逐项检查：

- **Evidence anchors fail-closed**：Plan 保留 unknown_anchor 和 invalid_marker 阻断。未放松允许 anchor 集合。**通过**。
- **ITEM_RULE deletion fail-closed**：Plan 不修改 item_rule 逻辑。**通过**。
- **Candidate facet non-asserted**：Plan 只计数 candidate facet assertion，不接受它。明确 "Diagnostic counters may count candidate facet assertion but must not accept it"。**通过**。
- **Trading advice blocked**：Plan 不修改 forbidden phrase 阻断。**通过**。
- **E2 deferred**：Plan 不实现 Evidence Confirm，明确 "this gate must not pretend to implement Evidence Confirm or weaken E1/E3/L1/C1/C2"。**通过**。
- **Missing semantics strict**：Plan 不放松 missing data 语义。**通过**。
- **No deterministic fallback**：Plan 不新增 fallback，不让 `--use-llm` partial result 输出报告。**通过**。
- **Default deterministic behavior unchanged**：Validation Matrix 包含 deterministic analyze/checklist 检查。**通过**。

**无发现**。

## 5. Code touch 最小性

Plan 允许触碰的文件：

- `fund_agent/fund/chapter_writer.py`（添加 typed diagnostic 字段到返回结构）
- `fund_agent/services/chapter_orchestrator.py`（添加子类派生逻辑和 diagnostic summary）
- `fund_agent/ui/cli.py`（添加 `first_failed_subcategory` stderr 输出）
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- evidence artifacts under `docs/reviews/` and `reports/`

明确不碰：golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态/provider config/auth/template/AGENTS.md。

**无发现**。文件范围合理且最小。

## 6. Tests/validation 充分性

- **Targeted unit tests** 覆盖所有 8 个子类的正面和反面 case。
- **Orchestrator tests** 覆盖 writer blocked → subcategory mapping、audit-blocked → subcategory mapping、provider timeout 不产生 prompt-contract subcategory、unmapped issue → code_bug_other。
- **CLI tests** 覆盖 `first_failed_subcategory` 输出和敏感信息排除。
- **Validation Matrix** 包含 ruff、targeted pytest、full pytest with coverage、deterministic analyze/checklist、missing-config fail-closed、real provider smoke、secret scan。

**无发现**。

## Minor observations（非 blocking）

### O1. `candidate_facet_assertion` 时序说明

Plan 表格中 `candidate_facet_assertion` 的 phase 标注为 `programmatic_audit`，这是正确的。但当 writer 本身 blocked 时（如 missing marker），programmatic audit 不会运行，candidate facet assertion 不可能被检测到。这是预期行为——candidate facet 只在 writer 成功 drafted 后的 audit 阶段才能出现。建议 implementation worker 在测试中显式覆盖 writer drafted + programmatic audit candidate facet blocked 的场景（plan 已在 orchestrator tests 中列出此 case）。

### O2. `code_bug_other` 含义边界

"no issue counters despite `llm_contract_violation`" 作为 `code_bug_other` 的触发条件是合理的安全网。但实现时需注意：如果 writer 的 `_draft_from_llm_response` 在极端情况下返回 `None, ()`（无 issues），`write_chapter` 会生成一个 generic `llm_contract_violation` issue。此时 issue 存在但不含可分类的 reason/id prefix。Plan 的 `code_bug_other` 兜底覆盖了这种情况，routing 到 code diagnostic 而非 prompt wording 变更是正确决策。

### O3. `ChapterRunResult` 新字段语义

Plan 描述了 `primary_subcategory` 字段但未给出显式 dataclass 定义。Implementation worker 应在 `ChapterRunResult` 上新增一个 `Optional[str]` 字段（如 `failure_subcategory`），accepted 章节为 `None`，blocked/failed 章节由 orchestrator 派生填入。该字段应为 frozen dataclass 的一部分，与现有 `failure_category` 并列。

## Conclusion

**PASS**。Plan 满足当前 gate 目标，安全边界完整，taxonomy 覆盖已知失败模式，code touch 最小，tests/validation 充分。3 个 minor observations 均为 implementation 指导建议，不构成 blocking findings。
