# 针对性复审 — EC-P4 Slice 2 代码审查修复

## 元数据

- **工作单元**：Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- **闸门**：code-review targeted re-review
- **切片**：Slice 2 — Service Deterministic Opt-In Propagation
- **分类**：heavy
- **时间戳**：2026-06-22 23:06 Asia/Shanghai
- **审核人**：AgentDS
- **复审产物**：`docs/reviews/code-review-rereview-20260622-230645-ds-ec-p4-slice2.md`

## 复审范围

- **原始审核产物**：`docs/reviews/code-review-20260622-225412-ds-ec-p4-slice2.md`
- **修复产物**：`docs/reviews/evidence-confirm-productionization-ec-p4-slice2-code-review-fix-20260622.md`
- **已审核文件**：
  - `fund_agent/services/fund_analysis_service.py`
  - `tests/services/test_fund_analysis_service.py`

## 裁决

**PASS**

全部 4 项发现均已修复，附直接文件/行号证据；无新增阻塞项引入。

## 逐项发现状态

### DS-ECP4S2-01 — analyze() / checklist() / _run_analysis_core() 的 Raises 节

- **状态**：**已修复**
- **证据**：`fund_agent/services/fund_analysis_service.py`
  - `analyze()` 第 742 行：`EvidenceConfirmBlockedError: 当 EC policy 为 block 且确定性复核失败时抛出。`
  - `checklist()` 第 798 行：`EvidenceConfirmBlockedError: 当 EC policy 为 block 且确定性复核失败时抛出。`
  - `_run_analysis_core()` 第 1182 行：`EvidenceConfirmBlockedError: 当 EC policy 为 block 且确定性复核失败时抛出。`
- **验证**：`rg -n "EvidenceConfirmBlockedError" fund_agent/services/fund_analysis_service.py` 输出第 742、798、924、1001、1044、1182、1743 行——覆盖全部六个 method/function 的 Raises 节。

### DS-ECP4S2-02 — analyze_with_llm_hosted 结构化传播

- **状态**：**已修复**
- **证据**：`fund_agent/services/fund_analysis_service.py`
  - 第 1054–1059 行：`structured_block_exception` 变量类型扩展至 `QualityGateBlockedError | QualityGateNotRunBlockedError | EvidenceConfirmBlockedError | None`
  - 第 1079–1082 行：`except` 子句新增 `EvidenceConfirmBlockedError`
  - 第 1084 行：`host_context.record_diagnostic(error_type=type(exc).__name__)` — 与既有 QG 错误相同的诊断记录
  - 第 1093–1094 行：`if structured_block_exception is not None: raise structured_block_exception` — Host 运行后重新引发
- **验证**：异常捕获 → 诊断记录 → 重新引发链完整；`EvidenceConfirmBlockedError` 不再作为非结构化 Host 失败传播。

### DS-ECP4S2-03 — 运行器异常转换测试

- **状态**：**已修复**
- **证据**：`tests/services/test_fund_analysis_service.py`
  - 第 669–703 行：新增 `test_fund_analysis_service_evidence_confirm_runner_exception_becomes_safe_summary`
  - 第 682 行：`_FakeEvidenceConfirmRunner(RuntimeError("boom"))` — 注入异常
  - 第 698–702 行：断言 `status="fail"`、`not_run_reason="runner_exception:RuntimeError"`、`pathway_status="fail"`、`deterministic_status="not_run"`
  - 第 703 行：`assert result.report_markdown` — 确认 warn 策略下报告仍然渲染
- **验证**：`uv run pytest tests/services/test_fund_analysis_service.py -q` → 39 项通过（此前为 38 项），新增测试名称已确认。

### DS-ECP4S2-04 — analyze_with_llm() / analyze_with_llm_execution() 的 Raises 节

- **状态**：**已修复**
- **证据**：`fund_agent/services/fund_analysis_service.py`
  - `analyze_with_llm()` 第 924 行：`EvidenceConfirmBlockedError: 当 EC policy 为 block 且确定性复核失败时抛出。`
  - `analyze_with_llm_execution()` 第 1001 行：`EvidenceConfirmBlockedError: 当 EC policy 为 block 且确定性复核失败时抛出。`
  - 额外：`analyze_with_llm_hosted()` 第 1044 行 — 超出原始发现范围，但属于一致性改进。
- **验证**：上述三行由 `rg -n` 输出确认。

## 验证命令输出

```
uv run pytest tests/services/test_fund_analysis_service.py -q
39 passed in 0.87s

uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
56 passed in 0.51s

uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py
All checks passed!
```

## 新增阻塞项

无。

## 剩余风险

| 风险 | 分类 | 负责人/去向 |
|---|---|---|
| CLI/UI Evidence Confirm 摘要与退出行为 | Slice 3 已批准 | Slice 3 实现者 |
| 渲染器非渲染守卫 | Slice 4 已批准 | Slice 4 实现者 |
| 语义伴随传播 | Slice 5 已批准 | Slice 5 实现者 |
| 清单模式 Evidence Confirm 仍为 off/无运行器 | 推迟 | 后续清单 EC gate |
| 产品模式 Evidence Confirm 仍为 off；NOT_READY | 推迟 | 后续就绪 gate |
