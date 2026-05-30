# MVP Gate 3 chapter_orchestrator implementation review (MiMo)

日期：2026-05-30
角色：AgentMiMo independent implementation review
Gate：`MVP Gate 3: chapter_orchestrator`
分类：`heavy`

## Verdict

**PASS**

实现完整匹配 accepted plan，Service/Fund 边界合规，无 scope creep，所有 fail-closed 行为被测试覆盖。两个 MEDIUM 发现属于防御性改进，不阻断 accepted。

## 1. Plan Conformance

| 检查项 | 状态 | 说明 |
|---|---|---|
| 文件清单 | ✅ | `chapter_orchestrator.py`、`__init__.py`、`test_chapter_orchestrator.py`、`fund_agent/README.md`、`tests/README.md` 均在 |
| Literal aliases | ✅ | `ChapterOrchestratorSchemaVersion`、`ChapterOrchestrationStatus`、`ChapterRunStatus`、`ChapterRunStopReason`（完整 14 值）、`ChapterRepairAction`、`ChapterOrchestrationInputKind` 全部实现 |
| Public dataclasses | ✅ | `ChapterOrchestratorLLMClients`、`ChapterOrchestrationPolicy`、`ChapterOrchestrationInput`、`AcceptedChapterConclusion`、`ChapterRepairDecision`、`ChapterAttemptRecord`、`ChapterRunResult`、`ChapterOrchestrationResult` 全部 frozen/slots/kw_only |
| Public API | ✅ | `build_chapter_orchestration_input()`、`orchestrate_chapters()`、`ChapterOrchestrator` façade 三者均实现且契约一致 |
| Policy 校验 | ✅ | target_chapter_ids 1-6 only、unique、non-empty；max_repair_attempts >= 0；max_output_chars > 0 |
| Input 校验 | ✅ | bundle/projection 互斥、fund_code/report_year 同源一致 |
| Writer stop reason mapping | ✅ | 一对一 mapping table 完整覆盖 `none`、`fund_type_unknown`、`missing_required_facts`、`evidence_anchor_missing`、`item_rule_deleted_required_content`、`chapter_requires_accepted_conclusions`、`prompt_only`、`llm_unavailable`、`llm_empty_response`、`llm_contract_violation`。不在表中的 stop reason raise ValueError |
| Auditor unavailable early stop | ✅ | `run_llm_audit=True and auditor is None` 全局 blocked，不调用 writer，不进入 repair loop |
| `_decide_repair()` 签名和决策表 | ✅ | 签名匹配 plan §8.2；决策表覆盖 accepted、auditor unavailable、LLM_UNAVAILABLE issue、needs_more_facts、none hint、budget exhausted、blocked/fail with patch/regenerate |
| `max_repair_attempts=0` | ✅ | initial audit fail 后不进入 repair retry |
| Accepted conclusion extraction | ✅ | `### 结论要点` / `## 结论要点` heading 抽取、fallback 前 3 非空行、`MAX_ACCEPTED_CONCLUSION_CHARS=500` hard cap |
| Exports | ✅ | `__init__.py` 精确导出 7 个 public symbol |
| docs/design.md 未修改 | ✅ | |
| docs/current-startup-packet.md 未修改 | ✅ | |
| docs/implementation-control.md 未修改 | ✅ | |
| AGENTS.md 未修改 | ✅ | |
| docs/fund-analysis-template-draft.md 未修改 | ✅ | |

## 2. Service/Fund Boundary

| 检查项 | 状态 |
|---|---|
| Service 只调用 Fund 公开 primitive | ✅ 只导入 `build_chapter_writer_input`、`write_chapter`、`audit_chapter`、`ChapterFactProvider`、`project_chapter_facts` |
| Service 不重写 CHAPTER_CONTRACT / preferred_lens / ITEM_RULE | ✅ |
| Service 不读取 repository/PDF/cache/source/helper/downloader/parser | ✅ 测试 `test_chapter_orchestrator_imports_do_not_cross_forbidden_boundaries` AST 扫描确认 |
| Service 不构造真实 LLM provider | ✅ |
| Service 不接入 Host/Agent/dayu | ✅ |

## 3. Scope Creep Check

| 禁止项 | 状态 |
|---|---|
| 无 final assembler / chapter 0 / chapter 7 生成 | ✅ policy 校验拒绝 0/7 |
| 无 CLI `--use-llm` | ✅ |
| 无 deterministic analyze/checklist 行为变更 | ✅ |
| 无 Host/Agent/dayu 依赖 | ✅ |
| 无 golden fixture/answer/manifest/score/snapshot/quality gate/FQ0-FQ6 变更 | ✅ |
| 无 real LLM provider SDK/env/config | ✅ |
| 无 source probing / repository access | ✅ |

## 4. Explicit Parameters

| 检查项 | 状态 |
|---|---|
| 无 `extra_payload` | ✅ 所有参数显式声明在 typed dataclass |
| LLM client 显式注入 | ✅ `ChapterOrchestratorLLMClients` bundle |
| `fact_provider` 可注入 | ✅ `ChapterOrchestrator.__init__(fact_provider=None)` 委托到 `orchestrate_chapters()` |

## 5. Fail-Closed Behavior

| 行为 | 实现 | 测试 |
|---|---|---|
| unknown fund type → 全局 blocked，不调用 writer | ✅ L395-401 | `test_unknown_fund_type_returns_global_blocked_without_writer_calls` |
| auditor None + run_llm_audit=True → 全局 blocked | ✅ L403-409 | `test_auditor_unavailable_blocks_before_writer_when_llm_audit_enabled` |
| writer None → blocked llm_unavailable | ✅ L660-662 via `_map_writer_stop_reason` | `test_writer_unavailable_blocks_and_does_not_call_auditor` |
| LLM exception → failed llm_exception | ✅ L661 | `test_writer_exception_becomes_llm_exception_and_does_not_leak` |
| auditor exception → failed llm_exception，保留 writer attempt | ✅ L696-706 | `test_auditor_exception_becomes_llm_exception_and_records_writer_attempt` |
| budget exhausted → failed repair_budget_exhausted | ✅ L852-858 | `test_repair_budget_exhausted_returns_failed_stop_reason` |
| max_repair_attempts=0 → 不 retry | ✅ | `test_max_repair_attempts_zero_does_not_retry_after_audit_failure` |
| LLM_UNAVAILABLE issue → stop，不 regenerate | ✅ L831-837 | `test_auditor_llm_unavailable_issue_stops_without_writer_retry` |
| needs_more_facts → stop，不 source probing | ✅ L838-844 | `test_needs_more_facts_stops_without_retrying_source_access` |
| fail_fast=True → 后续章节 skipped | ✅ L427-428 | `test_fail_fast_true_skips_later_chapters_after_first_blocked` |
| fail_fast=False → 继续执行 | ✅ | `test_fail_fast_false_continues_and_returns_partial` |
| writer blocked 不进入 auditor | ✅ L664-684 | `test_writer_unavailable_blocks_and_does_not_call_auditor` |

## 6. Writer Stop Reason Mapping Completeness

`_WRITER_STOP_REASON_MAPPING` (L68-81) 一对一覆盖所有 `ChapterWriteStopReason`：

| Writer Stop Reason | Run Status | Run Stop Reason |
|---|---|---|
| `none` | `accepted` | `none` |
| `fund_type_unknown` | `blocked` | `fund_type_unknown` |
| `missing_required_facts` | `blocked` | `missing_required_facts` |
| `evidence_anchor_missing` | `blocked` | `missing_required_facts` |
| `item_rule_deleted_required_content` | `blocked` | `missing_required_facts` |
| `chapter_requires_accepted_conclusions` | `blocked` | `dependency_missing` |
| `prompt_only` | `blocked` | `writer_blocked` |
| `llm_unavailable` | `blocked` | `llm_unavailable` |
| `llm_empty_response` | `blocked` | `llm_empty_response` |
| `llm_contract_violation` | `blocked` | `llm_contract_violation` |

测试 `test_every_writer_stop_reason_maps_to_exact_run_reason` (L397-425) 确认 mapping set 与 `ChapterWriteStopReason.__args__ - {"none"}` 完全相等。

## 7. Accepted Conclusion Extraction

| 检查项 | 状态 | 测试 |
|---|---|---|
| `### 结论要点` heading 抽取到下一个 `###` 或 `##` | ✅ | `test_heading_conclusion_extraction_stops_before_next_heading` |
| `## 结论要点` heading 抽取到下一个 `##` | ✅ | `test_h2_conclusion_extraction_stops_before_next_h2` |
| Fallback 前 3 非空行 | ✅ | `test_fallback_conclusion_uses_first_three_non_empty_lines` |
| 500 字符 hard cap + `conclusion_truncated=True` | ✅ | `test_long_conclusion_is_capped_at_500_chars` |
| 按章节顺序输出 | ✅ | `test_result_includes_accepted_conclusions_sorted_by_chapter_order` |
| 不生成第 0/7 章 | ✅ | `test_result_excludes_chapter_zero_and_seven_generation_scope` |

## 8. Findings

### MEDIUM

| # | 文件:行号 | 描述 | 影响 |
|---|---|---|---|
| M1 | `chapter_orchestrator.py:940` | `_stop_reason_from_repair_decision()` 使用中文字符串 `"章节修复预算耗尽。"` 匹配判断 repair budget exhausted。若 `_decide_repair()` 的 reason 文案变更会导致 silent mis-classification。当前测试覆盖，短期安全。 | 建议后续 refactor 改用 action 枚举判断或传递 budget_exhausted flag，不依赖字符串 |
| M2 | `chapter_orchestrator.py:993-996` | `_extract_conclusion_text()` 在第一个匹配 heading 返回空字符串时直接返回，不会尝试第二个 heading。即 `### 结论要点` 存在但为空时，不会 fallback 到 `## 结论要点`。Plan 未明确要求此 fallback 行为，且 Gate 2 writer 输出约定包含结论内容，实际发生概率低。 | 无阻断风险；如后续 writer 输出变空结论可追加空检查 |

### LOW

| # | 文件:行号 | 描述 |
|---|---|---|
| L1 | `chapter_orchestrator.py:1078` | `_orchestration_result()` 用 `len(accepted_conclusions) == len(policy.target_chapter_ids)` 判断 accepted 状态。功能正确（因为 `_validate_projection_coverage` 已保证唯一覆盖），但语义上不如 `set(accepted_chapter_ids) == set(policy.target_chapter_ids)` 直观 |

## 9. Residual Risks

与 accepted plan decision 一致：

| 残余风险 | 裁决 | Owner |
|---|---|---|
| `patch` 映射为 best-effort regenerate，无 typed patch API | MVP accepted；budget-bounded | Future repair contract gate |
| `partial` 结果不等于完整报告 | Gate 3 不把 partial 当 complete；Gate 4 必须裁决 partial assembly 行为 | Gate 4 plan |
| E2 source verification deferred | Gate 3 无 source access | Future Evidence Confirm gate |
| Chapter 5 cross-period evidence missing | No source probing in Gate 3 | Future cross-period data gate |
| No production LLM provider construction | Explicit client injection only | Gate 4/provider config gate |

## 10. Validation Reviewed

```text
uv run ruff check .
All checks passed!
```

```text
uv run pytest tests/services/test_chapter_orchestrator.py -q
29 passed in 0.82s
```

```text
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_facts.py -q
51 passed in 0.43s
```

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1039 passed in 4.86s
Total coverage: 91.73%
fund_agent/services/chapter_orchestrator.py: 93%
```

```text
git diff --check
clean
```
