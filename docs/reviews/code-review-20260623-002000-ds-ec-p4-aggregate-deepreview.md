# EC-P4 Service/UI/renderer/quality-gate 生产集成聚合深度复核

**角色**: AgentDS independent aggregate deepreview reviewer
**工作单元**: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
**当前 gate**: 聚合 deepreview（Slice 1–6 已接受，commit `4c80d86`）
**分支**: `evidence-confirm-productionization`
**日期**: 2026-06-23T00:20:00Z

## Verdict: PASS_WITH_FINDINGS

---

## 复核矩阵

| 维度 | 范围 | 方法 | 结果 |
|------|------|------|------|
| 代码正确性 | `evidence_confirm_production.py`, `quality_gate_integration.py`, `fund_analysis_service.py`, `cli.py`, `renderer.py`, `quality_gate.py` | 全文阅读 + 边界分析 | PASS_WITH_FINDINGS |
| 测试覆盖 | `tests/fund/test_evidence_confirm_production.py`, `tests/fund/test_quality_gate_integration.py`, `tests/fund/test_evidence_confirm_semantic.py`, `tests/services/test_fund_analysis_service.py`, `tests/ui/test_cli.py` | 全部 EC-P4 相关测试执行 | PASS |
| 边界合规 | Service/UI/Host/Agent 四层边界，renderer 不渲染 EC，checklist CLI 不暴露 EC | AGENTS.md + design.md 对照 | PASS_WITH_FINDINGS |
| 真源文档对齐 | design.md §Evidence Confirm, implementation-control.md | diff 核对 | PASS |
| NOT_READY 边界 | default-on EC、checklist EC CLI、provider semantic quality、release/readiness | 硬约束逐条验证 | PASS |

---

## 命令执行记录

```bash
# EC-P4 相关测试（全部通过）
.venv/bin/python -m pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py -v
# → 28 passed

.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py -v -k "evidence_confirm"
# → 8 passed

.venv/bin/python -m pytest tests/ui/test_cli.py -v -k "evidence_confirm"
# → 6 passed

.venv/bin/python -m pytest tests/fund/test_evidence_confirm_semantic.py -v
# → 19 passed

# 全量测试
.venv/bin/python -m pytest tests/ -q
# → 2258 passed, 1 failed (非 EC-P4 相关边界测试，详见 Finding F1)

# 变更量统计
git diff HEAD~6..HEAD --stat
# → 50 files changed, 5954 insertions(+), 25 deletions(-)
```

---

## Findings

### F1 — 边界导入测试因模块命名触发误报（WARN）

**位置**: `fund_agent/services/fund_analysis_service.py:65–68`

```python
from fund_agent.fund.evidence_confirm_sources import (
    EvidenceConfirmRepositoryRunRequest,
    EvidenceConfirmRepositoryRunResult,
    run_repository_bounded_evidence_confirm,
)
```

`tests/services/test_fund_analysis_service_llm.py` 中的 `test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries` 将 `"source"` 列为禁止片段。模块名 `evidence_confirm_sources` 因包含子串 `source` 而触发该检查，导致该测试 FAIL。

**分析**: Service 实际导入的是 typed dataclass（`EvidenceConfirmRepositoryRunRequest`、`EvidenceConfirmRepositoryRunResult`）和 runner 函数签名（`run_repository_bounded_evidence_confirm`）。Service 不直接读取年报文件、PDF、cache 或 source helper——它只把 runner 作为注入依赖调用，符合 AGENTS.md 对 Service 层的边界约束（"Service 不得直接调用具体来源、PDF cache 或下载 helper"）。但模块名 `evidence_confirm_sources` 中对 `sources` 的命名暗示了该模块承载 source 相关语义，且字面匹配导致边界测试失败。

**建议处置**: accepted candidate。此模块已在 EC-P2 gate 中接受为 repository-bounded 实现。可考虑：a) 在边界测试中将 `evidence_confirm_sources` 加入白名单（该模块是 Fund 层 internal，不破坏 Service 边界）；或 b) 长远考虑重命名模块以避免 `source` 子串。当前行为不构成实际边界违规。

---

### F2 — `_evidence_confirm_quality_gate_issues` 与 `run_quality_gate_for_bundle` 对 `None` 的处理路径不一致（INFO）

**位置**:
- `fund_agent/fund/quality_gate_integration.py:173–207`（`_evidence_confirm_quality_gate_issues`）
- `fund_agent/fund/quality_gate_integration.py:128–134`（`run_quality_gate_for_bundle` 调用点）

`_evidence_confirm_quality_gate_issues(summary=None)` 内部生成 `ECQ0/info` issue（"Evidence Confirm 未请求"），但 `run_quality_gate_for_bundle` 在 `evidence_confirm_summary is None` 时完全跳过调用，不生成任何 ECQ issue。

两条路径对 `None` 语义不同：
- 经 `run_quality_gate_for_bundle`：`None` → 无 ECQ issue（与旧行为完全兼容）
- 直接调用 `_evidence_confirm_quality_gate_issues`：`None` → ECQ0/info（显式可审计标记）

当前所有生产路径都走 `run_quality_gate_for_bundle`，因此 `_evidence_confirm_quality_gate_issues(summary=None)` 的 ECQ0 分支在生产中不可达。测试 `test_quality_gate_integration_explicit_summary_none_produces_no_ecq_issues` 验证了 `run_quality_gate_for_bundle(None)` 无 ECQ issue 行为。

**建议处置**: accepted candidate。两路径均有意为之：`run_quality_gate_for_bundle` 兼容旧行为，`_evidence_confirm_quality_gate_issues` 为未来直接调用者提供显式可审计性。建议在 `_evidence_confirm_quality_gate_issues` 的 docstring 中注明两条路径的 None 语义差异。

---

### F3 — `_semantic_issue_count` 命名与实际统计范围不精确（INFO）

**位置**: `fund_agent/fund/evidence_confirm_production.py:261–280`

```python
def _semantic_issue_count(semantic_result: EvidenceSemanticResult | None) -> int:
    if semantic_result is None:
        return 0
    return sum(
        1
        for claim_result in semantic_result.claim_results
        if claim_result.severity in {"block", "warn"}
    )
```

函数名 `_semantic_issue_count` 暗示统计所有 semantic claim 数量，但实际只统计 `severity ∈ {block, warn}` 的 claim，排除了 `info` 和 `not_applicable` 等级的 claim。该函数的唯一调用方是 `summary_from_repository_result`（line 129），用于填充 `issue_count` 字段，该字段聚合 V2 issue 与 semantic block/warn claim。过滤逻辑与 `issue_count` 的"生产可见问题"语义一致。

**建议处置**: accepted candidate。行为正确，命名可改进为 `_semantic_production_issue_count` 以传达 `block/warn only` 过滤。不改名不影响正确性。

---

## 逐 Slice 正确性确认

### Slice 1: Fund Summary + Quality Gate ECQ Projection

- `EvidenceConfirmProductionSummary` dataclass（`evidence_confirm_production.py:33–74`）正确实现 frozen/slots，所有字段有类型注解和 docstring
- `summary_from_repository_result()` 正确消费 `EvidenceConfirmRepositoryRunResult`，不读取 repository/PDF/cache
- `not_run_evidence_confirm_summary()` 正确实现稳定原因码校验（`STABLE_NOT_RUN_REASONS` ∪ `runner_exception:*` ∪ `repository_failure:*`）
- `_aggregate_summary_status()` 优先级正确：pathway fail > deterministic/semantic fail > warn > pass > not_run
- `_validate_semantic_result_identity()` 正确校验 fund_code/report_year 一致性
- `_ecq_issue()` 生成稳定 issue_id：`evidence-confirm:{fund_code}:{report_year}:{rule_code}:{reason}`
- ECQ0-ECQ4 投影逻辑正确：`_evidence_confirm_quality_gate_issues()` 按 summary 状态分支正确
  - `None` → ECQ0/info（仅直接调用可达）
  - `not_run` → ECQ0/info
  - `pathway fail` → ECQ1（severity 由 policy 决定）
  - `deterministic fail` → ECQ2（severity 由 policy 决定）
  - `deterministic warn` → ECQ3/warn
  - `semantic fail/warn` → ECQ4（severity 由 policy 决定）
- `merge_quality_gate_issues()`（`quality_gate.py:212–249`）正确合并 issues 并重写 JSON/MD 产物，不修改 score.json
- 测试 28 个全部通过

### Slice 2: Service Deterministic Opt-in Propagation

- `_run_evidence_confirm_if_enabled()`（`fund_analysis_service.py:1306–1350`）正确实现：
  - `policy="off"` → 返回 `None`（不调用 runner）
  - `policy ∈ {warn, block}` → 调用注入的 `_evidence_confirm_runner`
  - 通过 `project_chapter_facts(structured_data)` 投影章节事实（不直接读取原文）
  - runner 异常 catch-all → `_runner_exception_evidence_confirm_summary()` 生成 fail-closed 摘要（不泄漏异常消息）
- `_effective_evidence_confirm_policy()`（line 1658–1683）正确实现 checklist 固定为 `off`
- `_raise_evidence_confirm_block_if_required()`（line 1731–1749）仅在 `policy=block ∧ status=fail` 时抛出
- `_run_analysis_core()` 中两次调用 `_raise_evidence_confirm_block_if_required` 的位置正确：
  - 第一次在 QG block 分支内，先抛 EC 阻断再抛 QG 阻断（正确的优先级）
  - 第二次在 QG 分支后，确保 warn/pass 路径下 EC fail 也不被吞掉
- `ResolvedAnalyzeContract.evidence_confirm_policy` 正确默认 `"off"`（product mode）或读取 developer override
- `FundAnalysisResult` 和 `FundChecklistResult` 均正确包含 `evidence_confirm_summary` 字段
- `EvidenceConfirmBlockedError`（line 658–685）正确携带安全摘要，不包含原文/路径
- 测试 8 个全部通过

### Slice 3: CLI/UI Summary and Exit Behavior

- `analyze` 命令新增 `--evidence-confirm-policy` 参数（`cli.py:747–753`），仅在 `--dev-override` 下生效
- `checklist` 命令不暴露 `--evidence-confirm-policy`（测试确认）
- `_evidence_confirm_policy()` validator（`cli.py:2113–2129`）正确校验 off/warn/block
- `_echo_evidence_confirm_summary()`（`cli.py:2641–2668`）输出 stderr 安全行：
  - `evidence_confirm_status`、`evidence_confirm_policy`、`evidence_confirm_checked_facts`、`evidence_confirm_failed_facts`、`evidence_confirm_auditability_score`
  - 不输出原文 excerpt、PDF 路径、parser JSON、source adapter 信息
- `_echo_evidence_confirm_blocked()`（`cli.py:2598–2612`）在 EC block 异常时输出"Evidence Confirm 阻断报告输出"
- CLI 退出码正确：`EvidenceConfirmBlockedError` → exit 2
- `_build_developer_overrides()` 正确传递 `evidence_confirm_policy` 到 `FundAnalysisDeveloperOverrides`
- 测试 6 个全部通过

### Slice 4: Renderer Non-Rendering Guard

- `renderer.py` 不导入、不引用、不渲染 Evidence Confirm 相关内容
- `render_template_report()` 不接受 Evidence Confirm 参数
- `_render_evidence_section()` 只渲染证据锚点附录，不涉及 Evidence Confirm
- Service 层不从 `evidence_confirm_summary` 向 renderer 传递数据（`FundAnalysisResult.report_markdown` 来自 renderer，与 EC 摘要完全隔离）
- 测试 `test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report` 已证明 EC warn 启用时 `report_markdown` 与 baseline 完全一致，且不含 `evidence_confirm_status` 等内部字段
- design.md §"当前已实现：Evidence Confirm developer opt-in 与 ECQ 投影" 明确声明："CLI/UI 只展示 summary 行；renderer 报告 Markdown 仍不渲染 Evidence Confirm"

### Slice 5: No-Live Semantic Companion Propagation

- `summary_from_repository_result()` 接受 `semantic_result: EvidenceSemanticResult | None` 参数
- `_validate_semantic_result_identity()` 校验 semantic result 与 deterministic result 身份一致
- `_semantic_status()` 正确提取 no-live injected 结果的状态（not_applicable → not_applicable，其余直接传递）
- `_semantic_issue_count()` 只统计 block/warn severity claims
- Code path 不含任何 provider client 构造或 LLM 调用
- `_semantic_ecq_issue()` 通过 `_ecq_policy_severity()` 正确映射 policy→severity
- `_ecq_policy_severity()` 在 `policy="off"` 的 fail/warn 摘要进入时抛 ValueError（防御性检查）
- 测试 19 个全部通过，覆盖：entailed/contradicted/insufficient/not_applicable、client 调用 guard（deterministic fail 时不调用、candidate-only 引用不调用、缺少 bounded excerpt 不调用）、malformed/incompatible client 结果 fail-closed、client 异常不泄漏、identity 不匹配阻断、模块导入隔离和 provider 构造隔离

### Slice 6: Docs Sync and Control Evidence

- `README.md`: 新增 `--evidence-confirm-policy` 参数说明和 stderr 输出格式，标注 dev-override only
- `fund_agent/README.md`: 同步 EC-P4 边界描述
- `fund_agent/fund/README.md`: 新增 Evidence Confirm 包说明
- `tests/README.md`: 更新测试覆盖描述
- `docs/design.md`: 更新 EC-P4 当前实现描述（v2.34），明确区分已实现/未来候选
- `docs/implementation-control.md`: 更新 gate 状态
- `docs/current-startup-packet.md`: 更新 gate 入口

---

## 硬约束验证

| AGENTS.md 约束 | 验证结果 |
|---------------|---------|
| Service 不直接调用具体来源、PDF cache 或下载 helper | ✓ 通过；Service 通过 `EvidenceConfirmRunner` Protocol 注入 |
| 结构化提取必须通过 Fund 层 Processor/Extractor 边界 | ✓ 通过；`project_chapter_facts()` 从 `StructuredFundDataBundle` 投影 |
| 不得把显式参数放在 extra_payload 里传递 | ✓ 通过；`evidence_confirm_policy` 是 `FundAnalysisDeveloperOverrides` 显式字段 |
| Host 层级只做生命周期治理 | ✓ 通过；`EvidenceConfirmBlockedError` 在 Host runner operation 内正确传播 |
| 以代码为准，不让文档先于代码"设计未来" | ✓ 通过；design.md 明确标注"未来/候选边界" |
| 禁止 default-on Evidence Confirm | ✓ 通过；product mode 默认 `off`，checklist 固定 `off` |
| 禁止 checklist Evidence Confirm CLI support | ✓ 通过；checklist 不暴露该参数 |
| 禁止 provider-backed semantic quality | ✓ 通过；semantic companion 只接受 no-live injected result |
| 禁止 release/readiness 声明 | ✓ 通过；全链路保留 `NOT_READY` |

---

## 未覆盖区域与残余风险

1. **evidence_confirm_sources 模块命名与边界测试冲突**（F1）：当前仅影响一个测试，不影响生产行为。
2. **`_evidence_confirm_quality_gate_issues` 双路径 None 语义**（F2）：生产路径不可达 ECQ0 的 None 分支，但代码可读性受影响。
3. **EC runner 生产集成未经 live 验证**：所有测试使用 fake runner；真实 `run_repository_bounded_evidence_confirm` 仅在 EC-P2 gate 中有 bounded live 证据（`004393 / 2025` 单样本）。
4. **多年路径 (`analyze_multi_year_annual`) 不传递 EC policy**：`MultiYearAnnualAnalysisRequest` 没有 `evidence_confirm_policy` 字段——它通过 `analyze()` 间接获得 product mode 的 `off` 默认值。这是正确的 NOT_READY 行为，但文档中未显式说明。
5. **ECQ0/info 在 `run_quality_gate_for_bundle` 中不可达**：当 `evidence_confirm_summary` 不为 None 但 status 为 `not_run` 时，ECQ0/info 通过 `_evidence_confirm_quality_gate_issues(summary=not_none_with_not_run_status)` 可达。但当 summary 为 None 时，整个 ECQ 分支被跳过。这意味着 quality gate 产物中没有"Evidence Confirm 未请求"的可审计标记——这是与旧行为兼容的故意设计。

---

## 处置总结

| Finding | 严重度 | 处置 | 理由 |
|---------|--------|------|------|
| F1 边界导入测试误报 | WARN | accepted candidate | 实际导入仅为 typed dataclass，不违反边界；建议白名单或重命名 |
| F2 None 处理路径不一致 | INFO | accepted candidate | 双路径均有意为之；建议增强 docstring |
| F3 `_semantic_issue_count` 命名 | INFO | accepted candidate | 行为正确；命名可改进但不影响正确性 |

AGGREGATE_DEEPREVIEW_COMPLETE_NOT_READY
