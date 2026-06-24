# Code Review

## Scope

- Mode: current changes (workspace diff)
- Branch: evidence-confirm-productionization
- Base: main
- Output file: docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice1.md
- Included scope:
  - `fund_agent/services/fund_analysis_service.py` — Slice EC-DO-1 生产代码改动（3处 docstring + 1行策略默认值）
  - `tests/services/test_fund_analysis_service.py` — Slice EC-DO-1 测试新增（6个新测试 + `_FakeQualityGateForBundle` + 3个新 import）
- Excluded scope:
  - `fund_agent/ui/cli.py` — Slice EC-DO-2
  - `tests/ui/test_cli.py` — Slice EC-DO-2
  - `tests/fund/test_quality_gate_integration.py` — Slice EC-DO-3
  - `docs/design.md` / `docs/implementation-control.md` / `docs/current-startup-packet.md` / `README.md` — Slice EC-DO-4
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## 逐路径验证记录

### 路径1: product `analyze()` → EC warn 生效

入口 `FundAnalysisService.analyze()` (`:730`) → `_run_analysis_core(replace(request, command_source="analyze"))` → `_resolve_analyze_contract()` product 分支 (`:1590`) 返回 `evidence_confirm_policy="warn"` → `_effective_evidence_confirm_policy(command_source="analyze")` 返回 `"warn"` → `_run_evidence_confirm_if_enabled(policy="warn")` 调用 runner → 结果经 `summary_from_repository_result()` 投影为安全摘要 → 传入 quality gate → 最终写入 `_AnalysisCoreResult.evidence_confirm_summary`。

- 直接证据: `:1590` 策略字段赋值、`:1200` 策略传入、`:1333-1353` runner 调用与异常处理
- 测试覆盖: `test_fund_analysis_service_product_analyze_default_warn_calls_evidence_confirm` (`:704`) 断言 runner 调用一次、policy="warn"、status="pass"、report 产出

### 路径2: product `analyze()` EC fail → warn 非阻断

同上入口 → runner 返回 fail → `summary_from_repository_result(runner_result, "warn")` 返回 `status="fail"` summary → `_raise_evidence_confirm_block_if_required()` (`:1750-1753`) 检查 `summary.policy == "block"` → 条件为 False（policy 是 "warn"）→ 不抛异常 → 分析继续。

- 直接证据: `:1752` 阻断条件 `summary.policy == "block"`，product 默认 "warn" 不满足
- 测试覆盖: `test_fund_analysis_service_product_analyze_default_warn_fail_is_non_blocking` (`:757`) 断言不抛异常、summary status="fail"、quality_gate status="warn"（EC fail 投影）

### 路径3: product `analyze()` EC runner 抛异常 → 安全摘要

runner 抛出 `RuntimeError("boom /tmp/raw.pdf parser_payload provider_secret excerpt")` → `_run_evidence_confirm_if_enabled()` except 分支 (`:1346-1352`) 捕获 → `_runner_exception_evidence_confirm_summary()` 构造摘要，仅含 `exception_type="RuntimeError"`，不含异常消息原文 → 摘要 `not_run_reason="runner_exception:RuntimeError"`。

- 直接证据: `:1346` `except Exception as exc` 捕获所有异常、`:1347-1352` 仅传 `exc.__class__.__name__` 不含消息
- 测试覆盖: `test_fund_analysis_service_product_analyze_runner_exception_is_safe_summary` (`:800`) 断言摘要不含 "boom"、"/tmp/raw.pdf"、"parser_payload"、"provider_secret"、"excerpt"

### 路径4: product `checklist()` → EC 强制 off

入口 `FundAnalysisService.checklist()` (`:786`) → `_run_analysis_core(replace(request, command_source="checklist"))` → `_effective_evidence_confirm_policy(command_source="checklist")` 返回 `"off"` → `_run_evidence_confirm_if_enabled(policy="off")` 返回 `None`。

- 直接证据: `:1683-1684` `command_source == "checklist"` 返回 `"off"`、`:1333-1334` `policy == "off"` 返回 `None`
- 测试覆盖: `test_fund_analysis_service_product_checklist_default_keeps_evidence_confirm_off` (`:850`) 断言 runner 未调用、summary 为 None

### 路径5: product `analyze-annual-period` → 继承 EC warn

入口 `FundAnalysisService.analyze_multi_year_annual()` (`:821`) → 构造 `FundAnalysisRequest(mode="product", ...)` → 调用 `self.analyze()` → 进入路径1 → `evidence_confirm_policy="warn"`。

- 直接证据: `:864` mode 为 `"product"`（当 `developer_overrides is None`）、路径1 的完整调用链
- 测试覆盖: `test_multi_year_annual_analysis_product_default_inherits_evidence_confirm_warn` (`:2133`) 断言 runner 调用一次、policy="warn"、summary 传入 quality gate

### 路径6: developer override → EC off 隔离

入口 `analyze()` → `_developer_request()` 默认 `evidence_confirm_policy=None` → `_resolve_analyze_contract()` developer 分支 `evidence_confirm_policy=overrides.evidence_confirm_policy or "off"` → `"off"` → `_run_evidence_confirm_if_enabled(policy="off")` 返回 `None`。

- 直接证据: `:1617` `overrides.evidence_confirm_policy or "off"`，当 None 时得 "off"
- 测试覆盖: `test_fund_analysis_service_developer_default_and_explicit_off_do_not_inherit_warn` (`:889`) 断言 runner 未调用

### 边界检查

- **禁止依赖**: 测试 `test_fund_analysis_service_evidence_confirm_boundary_static_imports` (`:1191`) 对生产代码文件做静态字符串扫描，禁止 `FundDocumentRepository`、`pdf_cache`、`Docling`、`docling`、`pdfplumber` 等 7 个术语。EC-DO-1 的生产改动仅涉及 docstring 和一行策略默认值，未引入任何新 import，该测试应继续通过。
- **scope 合规**: workspace diff 仅包含 plan 允许的两个文件，无 CLI、quality gate 生产代码、设计文档或 README 改动。
- **`extra_payload` 合规**: 未在 `FundAnalysisRequest` 或 `FundAnalysisDeveloperOverrides` 新增字段，未使用 `extra_payload`。
- **AGENTS.md 硬约束合规**: 未违反四层边界（Service → Host → Agent）、未直接操作文件系统、未引入外部 `dayu-agent` 依赖、未使用魔法字符串。

### 阻断逻辑走查

`_run_analysis_core()` 中 quality gate block 与 EC block 的交互 (`:1212-1218`):

| quality_gate_policy | quality_gate_result | EC policy | EC status | 实际行为 |
|---|---|---|---|---|
| `"block"` | `None` | `"block"` | `"fail"` | 先抛 `EvidenceConfirmBlockedError`（`:1214`），不抛 `QualityGateNotRunBlockedError` |
| `"block"` | `None` | `"warn"` | `"fail"` | `_raise_evidence_confirm_block_if_required` 检查不通过（`:1752`），抛 `QualityGateNotRunBlockedError`（`:1215`） |
| `"block"` | `status="block"` | `"block"` | `"fail"` | 抛 `QualityGateBlockedError`（`:1217`），EC block 并入 QG block 的 ECQ issues |
| `"block"` | `status="block"` | `"warn"` | `"fail"` | 抛 `QualityGateBlockedError`（`:1217`） |
| `"warn"` | 任意 | `"block"` | `"fail"` | `:1212` 不进入，`:1218` 抛 `EvidenceConfirmBlockedError` |
| `"warn"` | 任意 | `"warn"` | `"fail"` | 不抛异常，分析继续 |
| `"off"` | 任意 | `"block"` | `"fail"` | `:1212` 不进入，`:1218` 抛 `EvidenceConfirmBlockedError` |
| product（QG block + EC warn） | `status="block"` | `"warn"` | `"fail"` | 抛 `QualityGateBlockedError`（`:1217`），符合 plan 要求 |

所有组合的行为均与 accepted plan 的语义声明一致。

### 测试断言强度

6 个新测试的断言覆盖了 plan 要求的全部验证点：

- runner 调用次数、请求字段（fund_code、report_year、projection、force_refresh）
- summary 的 policy、status、not_run_reason 字段
- 安全摘要不泄漏内部细节（异常消息、文件路径、parser/provider payload）
- quality gate 收到 EC summary 的传递路径
- report Markdown 仍正常产出
- developer off 隔离（runner 零调用）
- multi-year 路径的继承语义

## Open Questions

1. **LLM 路径（`analyze_with_llm` 系列）无 EC 集成测试**。三个 LLM 方法均通过 `_run_analysis_core()` 间接继承了 EC 默认 `warn`，但 Slice EC-DO-1 未要求也未添加 LLM 路径的 EC 行为 no-live 测试。`analyze_with_llm_hosted()` 的 except 子句（`:1080-1087`）已包含 `EvidenceConfirmBlockedError`，且 product 默认 `warn` 不会触发该异常，当前行为上不会回归。但缺少测试意味着后续 slice 变更时可能意外破坏 LLM 路径的 EC 语义。建议后续 slice 补充。

2. **`_FakeQualityGateForBundle` 的 EC fail→warn 投影逻辑与真实 `run_quality_gate_for_bundle` 之间无契约校验**。测试 fake 硬编码 `status="warn" if evidence_confirm_summary.status == "fail" else "pass"`（`:475-479`），仅验证 Service→QG 传参路径，不验证 Fund 层 ECQ issue 的真实生成行为。此 gap 由 Slice EC-DO-3 的 quality gate integration regression 覆盖。

## Residual Risk

| Residual | Classification | Owner / destination |
|---|---|---|
| LLM 路径无 EC 集成测试 | 测试 gap，非当前 slice regression | 后续 LLM 路径 EC gate 或 provider-backed semantic quality gate |
| 真实 ECQ warn-policy 投影行为未经本 slice 验证 | 测试 gap，由 EC-DO-3 覆盖 | Slice EC-DO-3 quality gate regression guard |
| Checklist EC CLI/support 仍为 off | 计划明确列为后续 gate | Checklist Evidence Confirm gate |
| Provider-backed/live semantic quality 未验证 | 计划明确列为后续 gate | Provider-backed semantic quality gate |
| Multi-sample live source/PDF coverage 未验证 | 计划明确列为后续 gate | Multi-sample live evidence gate |
| Release/readiness 仍为 `NOT_READY` | 计划明确列为后续 gate | Release/readiness gate |

## Verdict

**CODE_REVIEW_PASS**
