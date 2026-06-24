# Code Review — EC-P4 Slice 2 服务层确定性与生产集成

## 元数据

- **工作单元**: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- **闸门**: code review (deepreview)
- **切片**: Slice 2 — Service Deterministic Opt-In Propagation
- **分类**: heavy
- **时间戳**: 2026-06-22 22:54 Asia/Shanghai
- **审核人**: AgentDS
- **审核产物**: `docs/reviews/code-review-20260622-225412-ds-ec-p4-slice2.md`

## 裁决

**PASS_WITH_FINDINGS**

核心实现正确。策略解析与计划决策表一致，阻断语义与组合阻断表匹配，边界合规（无禁止导入，无仓库/源/解析器/PDF 直接访问），全部 94 项测试通过。四项发现中，两项涉及文档，一项涉及未测试边缘情况，一项涉及 Hosted LLM 路径错误传播。这些均非阻塞项；修改后即可接受。

## 审核目标

- `fund_agent/services/fund_analysis_service.py`（已修改）
- `tests/services/test_fund_analysis_service.py`（已修改）
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice2-implementation-evidence-20260622.md`（实施证据）

对照审核的参考产物：
- `AGENTS.md`
- `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`（已接受计划）
- `docs/reviews/evidence-confirm-productionization-ec-p4-plan-controller-judgment-20260622.md`（控制层裁决）
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice2-implementation-evidence-20260622.md`（实施证据）

## 摘要

实施工作新增了约 200 行业务逻辑代码进入 `fund_agent/services/fund_analysis_service.py`，以及约 250 行测试代码，新增 6 个专项测试用例，并更新了 2 个既有测试用例使其注入 fake runner 并验证无副作用。

### 已确认正确

1. **策略解析**（`_resolve_analyze_contract` + `_effective_evidence_confirm_policy`）：产品模式 → 固定 `off`；开发者覆盖 → `overrides.evidence_confirm_policy or "off"`；清单模式 → 固定 `off`。全部与计划匹配。

2. **Runner 注入与异步调用**：`EvidenceConfirmRunner` 协议定义为 `Callable[[EvidenceConfirmRepositoryRunRequest], Awaitable[EvidenceConfirmRepositoryRunResult]]`。默认值为 `run_repository_bounded_evidence_confirm`。测试注入 `_FakeEvidenceConfirmRunner`。Service 不直接实例化或导入 `FundDocumentRepository`。

3. **`ChapterFactProjection` 调用边界**：`project_chapter_facts(structured_data)` → `ChapterFactProjection` → `EvidenceConfirmRepositoryRunRequest.projection`。请求字段（`fund_code`、`report_year`、`projection`、`force_refresh`）均显式传递，无 `extra_payload` 滥用。

4. **边界合规**：对禁止术语（`FundDocumentRepository`、`pdf_cache`、`cache_helper`、`source_adapter`、`Docling`、`docling`、`pdfplumber`）执行 `rg` 扫描，无匹配项。静态测试 `test_fund_analysis_service_evidence_confirm_boundary_static_imports` 验证源码文件不含这些导入。Service 仅从 Fund 层导入公开的 Evidence Confirm 运行器/请求/结果/摘要辅助函数与 `project_chapter_facts()`。

5. **错误处理 — 运行器异常 → 安全摘要**：`_run_evidence_confirm_if_enabled` 在第 1327 行捕获 `Exception`（附带 `# noqa: BLE001` 注释），并调用 `_runner_exception_evidence_confirm_summary()` 生成 `status="fail"` 摘要，原因码为 `runner_exception:<class_name>`。异常消息不会泄露。

6. **阻断语义 — 对照计划表格**：

   | 场景 | 预期 | 实际 |
   |---|---|---|
   | QG-off + EC-block + EC-fail | `EvidenceConfirmBlockedError` | ✅ 第 1201 行 |
   | QG-warn + EC-block + EC-fail | `EvidenceConfirmBlockedError` | ✅ 第 1201 行 |
   | QG-block + EC-block + EC-fail（门控运行中） | `QualityGateBlockedError`（含 ECQ2） | ✅ 第 1199–1200 行 |
   | QG-block + QG 未运行 + EC-block + EC-fail | `EvidenceConfirmBlockedError` 先于 `QualityGateNotRunBlockedError` | ✅ 第 1197 行 |
   | EC-warn（任意 QG，任意 EC 状态） | 永不阻断 | ✅ — 策略 != `"block"` |

7. **`_run_analysis_core` 中的质量门控集成排序**：先调用 EC，再调用质量门控 → `run_quality_gate_for_bundle(..., evidence_confirm_summary=...)`。已抽取的结构化数据不会重新读取。

8. **测试覆盖**：38 项 Service 测试通过，56 项 Fund 层测试通过，ruff 检查通过。新增测试覆盖了所有必需场景（参见下文测试覆盖矩阵）。

### 测试覆盖矩阵

| 计划要求的测试 | 状态 | 测试名称 |
|---|---|---|
| 默认 analyze — EC 未调用 | ✅ | `test_fund_analysis_service_builds_render_and_audit_path_with_fake_extractor` |
| 默认 checklist — EC 未调用 | ✅ | `test_fund_analysis_service_checklist_returns_shared_core_without_rendering` |
| 开发者覆盖 warn 调用运行器，无阻断 | ✅ | `test_fund_analysis_service_evidence_confirm_warn_calls_runner_without_blocking` |
| 开发者覆盖 block + QG-off → `EvidenceConfirmBlockedError` | ✅ | `test_fund_analysis_service_evidence_confirm_block_raises_when_gate_off` |
| QG-warn + EC-block + fail → `EvidenceConfirmBlockedError` | ✅ | `test_fund_analysis_service_quality_warn_evidence_confirm_block_fail_raises_ec_error` |
| QG-block + EC-fail → `QualityGateBlockedError`（含 ECQ2） | ✅ | `test_fund_analysis_service_quality_block_evidence_confirm_fail_raises_quality_error` |
| 产品模式拒绝开发者覆盖 | ✅ | `test_fund_analysis_service_product_mode_rejects_evidence_confirm_override` |
| 边界静态导入检查 | ✅ | `test_fund_analysis_service_evidence_confirm_boundary_static_imports` |

---

## 发现

### 发现 DS-ECP4S2-01

- **严重性**：MEDIUM
- **文件/行号**：`fund_agent/services/fund_analysis_service.py:737–741, 793–797, 1163–1167`
- **问题**：`analyze()`、`checklist()` 和 `_run_analysis_core()` 的 Raises 节未列出 `EvidenceConfirmBlockedError`。上述方法现在可以引发此异常（通过 `_raise_evidence_confirm_block_if_required` → `_run_analysis_core` 第 1197/1201 行），但各自的 Raises 节仅记录 `QualityGateBlockedError` 和 `QualityGateNotRunBlockedError`。
- **为何重要**：调用方（CLI、UI、托管 LLM 路径）依赖文档字符串确定需要处理哪些异常。文档字符串缺失可能导致调用方出现未处理异常，或导致未来维护者未意识到此错误即可在该调用路径中引发。
- **必要修复**：在三处 Raises 节中新增条目：`` EvidenceConfirmBlockedError: 当 EC 策略为 `block` 且确定性复核结果为 fail，且质量门控关闭或策略为 warn 时引发。``
- **建议负责人**：Service 实现者

### 发现 DS-ECP4S2-02

- **严重性**：MEDIUM
- **文件/行号**：`fund_agent/services/fund_analysis_service.py:1049–1071`（`analyze_with_llm_hosted` 内的 `operation()` 闭包）
- **问题**：`operation()` 闭包在第 1068 行捕获 `QualityGateBlockedError` 和 `QualityGateNotRunBlockedError`，用于结构化错误传播（`quality_gate_exception` 变量、`host_context.record_diagnostic`），但未捕获 `EvidenceConfirmBlockedError`。当 `_run_analysis_core()` 在托管 LLM 路径中引发 `EvidenceConfirmBlockedError` 时，异常会未经 `quality_gate_exception` 模式或 `record_diagnostic` 调用而传播至 `asyncio.run()`，最终进入 `HostRuntimeRunner().run_sync()`。结果可能是托管运行的非结构化失败，而非 Service 层预期的安全摘要传播。
- **为何重要**：托管 LLM 路径（Route C Gate 4）共享 `_run_analysis_core()`。在 `--use-llm` 下发起调用并启用 EC developer override 的用户，可能收到通用的 Host 运行失败信息，而非携带安全摘要的结构化 `EvidenceConfirmBlockedError`。
- **必要修复**：方案 A：将 `EvidenceConfirmBlockedError` 也加入 `operation()` 中的 except 子句。方案 B：新增一个 except 处理函数，设置 `quality_gate_exception`（或新的 `ec_exception` 变量），并在 `run_sync` 之后重新引发。更倾向于方案 A，因为在 EC 阻断下托管 LLM 输出没有意义——与 QG 阻断失败属于同一语义类别。
- **建议负责人**：Service/托管 LLM 负责人

### 发现 DS-ECP4S2-03

- **严重性**：LOW
- **文件/行号**：`tests/services/test_fund_analysis_service.py`（缺少测试）
- **问题**：缺少运行器异常转换路径的显式测试（`_run_evidence_confirm_if_enabled` 第 1327–1333 行）。计划明确要求“运行器异常必须转换为 fail summary；……运行器异常原因码必须为 `runner_exception:<class_name>`”，但没有任何测试构造 `_FakeEvidenceConfirmRunner(RuntimeError("boom"))` 并验证生成的摘要。
- **为何重要**：`except Exception` 路径（附带 `BLE001` noqa）是宽泛的，且对正确性至关重要——如果在没有测试覆盖的情况下意外缩窄，运行器异常可能破坏整个分析，而非降级为安全摘要。
- **必要修复**：新增测试：
  ```python
  async def test_fund_analysis_service_runner_exception_becomes_safe_summary():
      runner = _FakeEvidenceConfirmRunner(RuntimeError("boom"))
      service = FundAnalysisService(extractor=_FakeExtractor(_bundle()), evidence_confirm_runner=runner)
      result = await service.analyze(_developer_request(quality_gate_policy="off", evidence_confirm_policy="warn"))
      assert result.evidence_confirm_summary.status == "fail"
      assert result.evidence_confirm_summary.not_run_reason == "runner_exception:RuntimeError"
      assert result.evidence_confirm_summary.pathway_status == "fail"
      assert result.report_markdown  # warn 不阻断
  ```
- **建议负责人**：Service 测试负责人

### 发现 DS-ECP4S2-04

- **严重性**：LOW
- **文件/行号**：`fund_agent/services/fund_analysis_service.py:917–921, 993–997`
- **问题**：`analyze_with_llm()` 和 `analyze_with_llm_execution()` 的 Raises 节未列出 `EvidenceConfirmBlockedError`。与 DS-ECP4S2-01 相同的文档缺失问题，应用至 LLM 分析方法。`_run_analysis_core()` 可以引发 `EvidenceConfirmBlockedError`，该异常会穿透这两个方法。
- **为何重要**：与 DS-ECP4S2-01 相同——调用方依赖文档字符串了解异常契约。
- **必要修复**：在两个方法的 Raises 节中新增 `EvidenceConfirmBlockedError`。
- **建议负责人**：Service 实现者

---

## 剩余风险 / 未覆盖领域

| 风险 | 严重性 | 处置 |
|---|---|---|
| 运行器异常摘要中的 `blocking_issue_ids` 格式（`evidence-confirm-runner:runner_exception:…`）可能与 `summary_from_repository_result` 产生的格式不同。 | LOW | 质量门控集成应通用处理所有 `blocking_issue_ids`。如集成层假设特定格式，则需对齐。不由本次审核阻断。 |
| 涉及真实 `FundDocumentRepository` 加载的端到端 EC 流程未经测试。 | 已确认 | EC-P2 单一样本 live 证据存在；全面 live 正确性推迟至 readiness matrix gate。范围外。 |
| 无清单模式 EC CLI 支持。 | 已确认 | 推迟至后续明确的清单 EC 切片/gate。 |
| 多项既有测试（例如 `test_fund_analysis_service_normalizes_fund_code_before_extraction`、温度计测试）在构造 `FundAnalysisService` 时未注入 fake runner。 | LOW | 由于默认 EC 策略为 `off`，生产默认运行器不会被调用。在后续切片中，当更多测试需要显式 fake 注入时，可逐步升级。 |

## 必要后续行动

1. **（阻断合并）** 无。无需更改即可合并。
2. **（建议）** 处理 DS-ECP4S2-01 和 DS-ECP4S2-04（文档字符串 Raises 节）。工作量 < 5 行。
3. **（建议）** 处理 DS-ECP4S2-02（`analyze_with_llm_hosted` 错误处理）。在 EC 开发者覆盖模式下使用托管 LLM 路径之前应修复，因为在没有门控的情况下不太可能这样做，但属于代码债务。
4. **（建议）** 处理 DS-ECP4S2-03（运行器异常测试）。工作量 < 15 行；覆盖关键安全路径。
5. **（控制层）** 当前闸门之后，继续执行切片 3（CLI/UI 摘要与退出行为）。

## 验证命令

```bash
# Service tests (38 passed)
uv run pytest tests/services/test_fund_analysis_service.py -q

# Fund-layer tests (56 passed)
uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q

# Lint
uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py

# Boundary check
rg -n "FundDocumentRepository|pdf_cache|cache_helper|source_adapter|Docling|docling|pdfplumber" fund_agent/services/fund_analysis_service.py
# Expected: no matches
```
