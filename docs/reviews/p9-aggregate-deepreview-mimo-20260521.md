# P9 Aggregate Deepreview — MiMo

> **审查日期**: 2026-05-21
> **审查范围**: P9-S1 + P9-S2（commit `56d579f..2f82d9e`，含所有 implementation、plan、review 和 doc artifact）
> **审查基线**: `main` HEAD `2f82d9e`
> **验证**: full suite `377 passed`，ruff passed
> **审查人**: AgentMiMo

---

## Reviewer Limitation

本审查人参与了 P9-S2 的 planning 和 implementation（`ce603a0`），不是独立第三方 reviewer。
P9-S2 的 controller judgment（`docs/reviews/p9-s2-code-review-controller-judgment-20260521.md`）已记录 AgentDS/AgentGLM 均未能产出独立 review artifact。本 aggregate deepreview 对 P9-S2 的代码结论受限于同一 reviewer 视角，应作为单-reviewer 覆盖而非双-reviewer 独立验证。

---

## 1. product analyze ignores developer overrides

**结论: PASS**

- `fund_analysis_service.py:451-453`：`_resolve_analyze_contract` 在 `mode == "product"` 时检查 `request.developer_overrides is not None`，抛出 `ValueError("product mode 不允许 developer_overrides")`。
- `fund_analysis_service.py:454-470`：product mode 返回的 `ResolvedAnalyzeContract` 所有 override 字段为 `None`，`final_judgment_override=None`，`quality_gate_policy="block"`，`current_stage=None`。
- CLI `cli.py:194`：`mode="developer_override" if dev_override else "product"`，未传 `--dev-override` 时强制 product mode。
- CLI `cli.py:738-741`：传了 override 参数但未传 `--dev-override` 时，`_build_developer_overrides` 抛出 `typer.BadParameter`。
- 测试覆盖：`tests/services/test_fund_analysis_service.py` + `tests/ui/test_cli.py` 覆盖 product mode 拒绝 override 的路径。

---

## 2. quality_gate_policy default block

**结论: PASS**

- `fund_analysis_service.py:465`：product mode `_resolve_analyze_contract` 硬编码 `quality_gate_policy="block"`。
- `fund_analysis_service.py:483`：developer_override mode 默认 `"block"`（`overrides.quality_gate_policy or "block"`）。
- `cli.py:116`：CLI `--quality-gate-policy` 默认值 `"block"`。
- `cli.py:665-666`：CLI 中 `quality_gate_policy != "block"` 被识别为 developer override option，未传 `--dev-override` 时阻断。
- `fund_analysis_service.py:336-340`：Service 在 `quality_gate_policy == "block"` 时，gate 结果为 `None`（not_run）或 `status == "block"` 均抛出结构化异常，CLI 返回退出码 2。

---

## 3. gate_not_run only selected pool source or membership pre gate failures

**结论: PASS**

- `fund_analysis_service.py:538-567`：`_check_pool_membership_before_extraction` 仅在 `quality_gate_policy == "block"` 时执行精选池 CSV 成员检查，不在池中时提前抛出 `QualityGateNotRunBlockedError`，避免浪费年报抽取 I/O。
- `quality_gate_integration.py:155-185`：`_selected_fund_for_bundle` 处理 CSV 不存在（`FileNotFoundError`）、格式错误（`ValueError`）、校验阻断和基金不在池中四类 not-run reason，全部通过显式 reason 字符串返回，不伪造 App 类别或继续评分。
- `quality_gate_integration.py:84-92`：`selected_fund is None` 时直接返回 `BundleQualityGateResult`，`score_result=None`、`quality_gate_result=None`，`not_run_reason` 有值。
- `fund_analysis_service.py:336-340`：block 策略下 `quality_gate_result is None` 触发 `QualityGateNotRunBlockedError`。
- `cli.py:863-878`：`_echo_quality_gate_not_run_blocked` 输出 `quality_gate_status: not_run` 和 `quality_gate_not_run_reason`。

---

## 4. missing strict golden coverage is FQ0 info, mismatch is FQ1 block

**结论: PASS**

- `extraction_score.py:432-471`：`_correctness_coverage_issue` 构造 issue 时硬编码 `rule_code="FQ0"`、`severity=SEVERITY_INFO`。覆盖所有缺失场景：`not_configured`、`fund_not_covered`、`no_comparable_fields`、`partially_covered`。
- `extraction_score.py:333`：`CorrectnessSummary.coverage_required` P9-S2 固定为 `False`，缺失 golden 覆盖不进入阻断分母。
- `quality_gate.py:363-429`：`_correctness_available_coverage_issue` 对 `available` status 的 correctness 汇总，检查 `coverage_scope`，非 `covered` 时生成 `FQ0/info`。
- `quality_gate.py:502-533`：`_correctness_mismatch_issue` 构造 issue 时硬编码 `rule_code="FQ1"`、`severity=SEVERITY_BLOCK`。
- `extraction_score.py:1775-1788`：golden 期望存在但 snapshot 明确缺失时标记为 `CORRECTNESS_MISMATCH`。
- `quality_gate.py:358-359`：`_evaluate_correctness` 对 `record_results` 中 `status == "mismatch"` 的行调用 `_correctness_mismatch_issue`。
- CLI `cli.py:907-937`：`_quality_gate_info_lines` 对 `FQ0/info` 且有 `fund_code` 的 issue 输出 fund-scoped info 行到 stderr。

---

## 5. malformed inputs fail closed

**结论: PASS**

以下路径已逐一验证：

| 入口 | 畸形输入 | 行为 |
|------|---------|------|
| `_load_score_payload` | score.json 非 dict | `ValueError` |
| `_evaluate_score_payload` | field_scores 缺失/非 list | `ValueError` |
| `_evaluate_field_score` | 缺少 field_name/priority/status/coverage_rate | `ValueError` |
| `_evaluate_fund_quality` | 缺少 fund_code/app_category_status/missing_field_rate | `ValueError` |
| `_normalize_preferred_lens_status` | 非法状态值 | `ValueError` |
| `_evaluate_correctness` | status 非 available/unavailable | `ValueError` |
| `_correctness_mismatch_issue` | 缺少 fund_code/field_name/sub_field/expected_value/reason | `ValueError` |
| `_resolve_analyze_contract` | mode 非 product/developer_override | `ValueError` |
| `_validate_request` | fund_code 非 6 位数字 / report_year ≤ 0 | `ValueError` |
| `derive_final_judgment` | quality_gate_status 非 pass/warn/block/not_run | `ValueError` |
| `load_snapshot_records` | JSONL 行非 dict | `ValueError` |
| `load_snapshot_error_records` | 缺少 fund_code | `ValueError` |
| `_resolve_golden_answer_path` | 非默认路径但文件不存在 | `FileNotFoundError` |
| `_validate_report_wording` | 报告含"买入""卖出"等禁用词 | `ValueError` |

所有畸形输入路径均显式抛出异常，不静默降级或伪造结果。

---

## 6. final judgment has no buy or sell wording

**结论: PASS**

- `renderer.py:38-42`：`_FINAL_JUDGMENT_TEXT` 只映射三个值：`worth_holding → 值得持有`、`needs_attention → 需要关注`、`suggest_replace → 建议替换`。无"买入""卖出""仓位比例""收益预测"。
- `renderer.py:43`：`_FORBIDDEN_TERMS = ("买入", "卖出", "仓位比例", "收益预测")`。
- `renderer.py:1152-1167`：`_validate_report_wording` 在渲染后扫描完整报告，命中禁用词时抛出 `ValueError`。
- `renderer.py:551`：第 7 章固定输出"判断边界：本结论只在公开披露信息和显式输入范围内成立，不预测未来收益，不给出交易或配置指令。"
- `final_judgment.py:20-24`：`_JUDGMENT_ORDER` 只包含三个 `FinalJudgment` 值，类型 `Literal["worth_holding", "needs_attention", "suggest_replace"]`。
- `AGENTS.md:227`：硬约束"禁止直接输出'买入''卖出'建议，只输出'值得持有 / 需要关注 / 建议替换'判断"。

---

## 7. docs match current behavior

**结论: PASS（1 个 info finding）**

design.md 与代码当前行为对齐验证：

| design.md 声明 | 代码事实 | 状态 |
|---------------|---------|------|
| `quality_gate_policy=block` 是 `analyze` 默认策略 | `fund_analysis_service.py:465` 硬编码 `"block"` | ✅ |
| product mode 下 quality gate block/not-run 由 Service 在派生前 fail-closed | `fund_analysis_service.py:336-340` | ✅ |
| FQ0 前置条件缺失 info/not-run | `quality_gate.py` FQ0 使用 `SEVERITY_INFO` | ✅ |
| FQ1 correctness 或 App 类别冲突 block | `quality_gate.py` FQ1 使用 `SEVERITY_BLOCK` | ✅ |
| FinalJudgmentDecision selected/derived/source 契约 | `final_judgment.py` + `fund_analysis_service.py:394-401` | ✅ |
| R2 审计检查 developer_override 冲突 | `audit_programmatic.py:605-612` | ✅ |
| renderer 禁用"买入""卖出"等措辞 | `renderer.py:43,1152-1167` | ✅ |
| quality gate FQ0-FQ6 规则表 | 与 `quality_gate.py` 实现一致 | ✅ |

**Info finding**: `audit_programmatic.py:30` 的 `AuditRuleCode` 类型定义为 `Literal["P1", "P2", "P3", "C2", "L1", "R1", "R2"]`，但 `_audit_contract_conformance` 使用 `code="C2"` 构造 issue（`audit_programmatic.py:365`）。运行时行为正确（字符串传递），但若启用 mypy strict 模式，`_issue()` 的 `code` 参数类型标注为 `AuditRuleCode` 会与 `"C2"` 文字量冲突。design.md 5.2 节已声明 C2 为 MVP 已实现规则码。该 finding 不影响运行时正确性，属于类型标注与运行使用不一致。

implementation-control.md P9 条目与代码状态对齐：P9-S1 和 P9-S2 的 implementation commit、review artifact、controller judgment 和验证结果均已记录，与当前 `377 passed` 基线一致。

---

## 8. adversarial failure pass

以下 adversarial 场景已检查：

| 场景 | 路径 | 结论 |
|------|------|------|
| product mode 传 `developer_overrides={}` | `_resolve_analyze_contract` 抛 ValueError | ✅ 阻断 |
| CLI 传 `--equity-position 80%` 无 `--dev-override` | `_build_developer_overrides` 抛 BadParameter | ✅ 阻断 |
| score.json `correctness.status` 为 `"available"` 但 `record_results` 含 mismatch | FQ1/block | ✅ 阻断 |
| 精选池 CSV 基金不在池中 + block 策略 | `_check_pool_membership_before_extraction` 抛异常 | ✅ 阻断 |
| 精选池 CSV 不存在 + block 策略 | `_selected_fund_for_bundle` 返回 not_run_reason | ✅ 阻断 |
| golden answer JSON 存在但基金不在其中 | `coverage_scope=fund_not_covered` → FQ0/info | ✅ 不阻断 |
| golden answer JSON 存在且有 mismatch | FQ1/block | ✅ 阻断 |
| 报告渲染后含"买入" | `_validate_report_wording` 抛 ValueError | ✅ 阻断 |
| quality_gate_status 为 `"not_run"` | `_derive_without_override` 派生 `needs_attention` | ✅ 降级 |
| `quality_gate_result` 和 `quality_gate_not_run_reason` 同时存在 | `_resolve_final_judgment_quality_gate_status` 抛 ValueError | ✅ fail-closed |

---

## 9. project instruction compliance

| AGENTS.md 硬约束 | P9 代码 | 状态 |
|-----------------|---------|------|
| 禁止直接输出"买入""卖出"建议 | renderer `_FORBIDDEN_TERMS` + `_validate_report_wording` | ✅ |
| 证据必须可溯源 | renderer 每章 `_evidence_line` + 附录 | ✅ |
| 禁止把显式参数放在 extra_payload 里传递 | `FundAnalysisRequest` 显式字段，无 extra_payload | ✅ |
| 基金类型判断优先于通用分析 | `_extract_fund_type` 在 analysis 前执行 | ✅ |
| 后端 fallback fail-closed | P8-S3 五类 taxonomy + P9 不改变 | ✅ |

---

## 结论

P9-S1 和 P9-S2 的 7 项审查要点全部 PASS。1 个 info finding（AuditRuleCode 类型标注不含 C2 但运行时使用），不影响正确性。全量 `377 passed`，ruff passed，docs 与代码行为对齐。

**主要风险**：P9-S2 缺独立 Agent code review artifact（AgentDS compacting 未产出、AgentGLM 401），本 aggregate deepreview 为单 reviewer 覆盖，不等同双 reviewer 独立验证。该限制已在 implementation-control.md 和本报告 reviewer limitation 中记录。
