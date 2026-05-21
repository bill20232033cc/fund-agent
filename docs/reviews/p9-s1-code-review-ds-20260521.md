# P9-S1 Code Review - AgentDS

- **Date**: 2026-05-21
- **Phase**: P9-S1 analyze product contract hardening
- **Plan**: `docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`
- **Implementation artifact**: `docs/reviews/p9-s1-implementation-20260521.md`
- **Controller judgment**: `docs/reviews/p9-s1-plan-review-controller-judgment-20260521.md`
- **Review type**: implementation code review (不改代码、不提交)

## Verdict

**PASS_WITH_FINDINGS** — 3 LOW severity findings, no correctness or breaking issues.

## Review Scope

按用户要求重点审查：

1. request/resolver 迁移是否破坏现有 Service/CLI 行为
2. quality gate status machine 是否与计划一致
3. BadParameter 行为是否合理
4. R2 audit 是否 fail closed
5. 旧 CLI/e2e/smoke 调用是否迁移
6. docs 是否以代码为准且不越界

## Findings

### LOW

**L1** — `fund_agent/services/fund_analysis_service.py:319`
`analyze()` docstring 的 Raises 节列出了 `QualityGateBlockedError` 但未列出 `QualityGateNotRunBlockedError`。两者都是同一层级的结构化异常，调用方可能需要分别 catch。当前 `ValueError` 笼统覆盖了它（因为是子类），但与 `QualityGateBlockedError` 显式列出的做法不一致。

**L2** — `fund_agent/services/__init__.py:29`
`FinalJudgment` 从 `fund_agent.services.fund_analysis_service` import，再上溯到 `fund_agent.fund.analysis` → `final_judgment.py`。计划要求 services re-export 必须从 `fund_agent.fund.analysis.final_judgment` 直接 import。当前链路上多了一跳，但单一类型定义点未变，services 层无独立 `FinalJudgment` 定义，功能等价。

**L3** — `fund_agent/services/fund_analysis_service.py:324-325`
`_check_pool_membership_before_extraction` 在 `_validate_request` 之前调用。若基金代码格式非法（如 `"ABC"`）且不在精选池 CSV 中（block 策略），会先触发 `QualityGateNotRunBlockedError("fund_code not found")` 而非 `ValueError("fund_code 必须是 6 位数字")`。两种都会阻断，但错误信息对用户的诊断价值不同——格式错误比"不在池中"更直接。建议调换调用顺序，先做格式校验再做池成员检查。

## Per-Scope Assessment

### 1. request/resolver 迁移是否破坏现有 Service/CLI 行为

**通过。** `FundAnalysisRequest` 根字段收窄为 product inputs，开发参数全部移入 `FundAnalysisDeveloperOverrides`。`_resolve_analyze_contract()` 正确实现了计划中的 resolver 伪代码：
- product mode 固定所有 dev 字段为 `None`、`quality_gate_policy="block"`、使用默认 source/golden 路径
- product mode + `developer_overrides is not None` → `ValueError`
- developer override mode 空对象等价于 `FundAnalysisDeveloperOverrides()`，所有字段 `None`，`quality_gate_policy` 回落 `"block"`
- 无 `extra_payload`，无 dict 兜底

CLI 构造 `FundAnalysisRequest` 时：
- 默认 `mode="product"`、`developer_overrides=None`
- `--dev-override` 时 `mode="developer_override"`、nested overrides 由 `_build_developer_overrides()` 构造

**未发现行为破坏。**

### 2. quality gate status machine 是否与计划一致

**通过。** 逐行对照计划第 3.6 节状态机表：

| policy | gate result | not-run reason | 计划行为 | 代码实现 | 一致 |
|---|---|---|---|---|---|
| `block` | `status=block` | `None` | 抛 `QualityGateBlockedError` | `fund_analysis_service.py:338-339` | ✓ |
| `block` | `None` | 非空 | 抛 `QualityGateNotRunBlockedError` | `fund_analysis_service.py:336-337` | ✓ |
| `block` | `status=pass/warn` | `None` | 继续报告，传 `pass/warn` | 不触发 raise，经 `_resolve_final_judgment_quality_gate_status` 返回 gate status | ✓ |
| `warn` | `status=pass/warn/block` | `None` | 继续报告 | 同上 | ✓ |
| `warn` | `None` | 非空 | 继续报告，传 `not_run` | `_resolve_final_judgment_quality_gate_status` 返回 `"not_run"` | ✓ |
| `off` | `None` | `policy=off` | 继续报告，传 `not_run` | `_run_quality_gate_if_enabled:587-588` 返回 `(None, "policy=off")` | ✓ |

`_resolve_final_judgment_quality_gate_status()` 正确归一化：`quality_gate_result` 与 `not_run_reason` 互斥校验 → `None` → `"not_run"` → gate status → 非法 status 抛 `ValueError`。

`derive_final_judgment()` 在 quality_gate_status 不在允许集合时 fail-closed（`final_judgment.py:84-85`）。

product mode 下 `quality_gate_policy` 固定为 `"block"`，不可通过 CLI 或 API 绕过（`_resolve_analyze_contract:464`）。

**未发现偏差。**

### 3. BadParameter 行为是否合理

**通过。** CLI `_build_developer_overrides()` 在 `dev_override=False` 且检测到任何 dev 参数时抛 `typer.BadParameter`（`cli.py:737-739`），错误信息列出所有误传参数并指向 `--dev-override`。

选择 `BadParameter` 的理由与计划一致：
- 这是 CLI 参数用法错误，不是 quality gate 或数据质量阻断
- Typer 生成标准非零退出，保留参数定位
- 与退出码 2 的质量阻断语义分离

`_has_developer_override_options()` 正确识别所有 14 个 dev 参数，包括 `quality_gate_policy != "block"`（`cli.py:663`）。`block` 是唯一合法的 product mode 值，不会被误判为 dev option。

**未发现偏差。**

### 4. R2 audit 是否 fail closed

**通过。** `audit_programmatic.py` 的 R2 审计链路：

1. 必需输入检查（`_audit_required_inputs:185-208`）：
   - `final_judgment is None` → R2 fail（`location="final_judgment"`）
   - `derived_final_judgment is None` → R2 fail（`location="derived_final_judgment"`）
   - `final_judgment_source is None` → R2 fail（`location="final_judgment_source"`）
   - 三项全部缺失时三条 R2 issue 同时触发

2. 一致性检查（`_audit_final_judgment:596-620`）：
   - `source == "derived"` 且 `selected != derived` → R2 fail
   - `source == "developer_override"` 且 `selected != derived` → R2 fail（明确标注"开发覆盖与系统派生判断冲突"）
   - `source` 既非 `derived` 也非 `developer_override` → R2 fail
   - 保留原有红灯/全绿一致性规则

3. Service 层 fail-closed（`fund_analysis_service.py:416-418`）：
   - `audit_result.passed == False` → 抛 `ValueError`
   - 任何单条 R2 issue 都会导致整条分析链路失败

4. 类型定义统一：audit 模块已删除本地 `FinalJudgment` Literal 定义，统一从 `fund_agent.fund.analysis.final_judgment` import（`audit_programmatic.py:15`）。

**R2 在三个层级（输入缺失、语义冲突、Service 阻断）均为 fail-closed。**

### 5. 旧 CLI/e2e/smoke 调用是否迁移

**通过。** 逐个检查：

- **CLI 测试** (`tests/ui/test_cli.py`)：
  - 新增 `test_analyze_cli_default_product_request` — 验证默认 product mode、`developer_overrides is None`
  - 新增 `test_analyze_cli_rejects_dev_options_without_dev_override` — 验证 `--equity-position` 无 `--dev-override` 触发 `BadParameter`
  - 新增 `test_analyze_cli_rejects_quality_gate_policy_without_dev_override` — 验证 `--quality-gate-policy off` 无 `--dev-override` 触发 `BadParameter`
  - 旧 `test_analyze_cli_calls_service_and_prints_report` 已补 `--dev-override`，断言改为 `last_request.developer_overrides`

- **P3 CLI e2e** (`tests/fund/integration/test_p3_cli_e2e_matrix.py`)：
  - 三只样本基金 `cli_args` 均新增 `--dev-override`
  - 移除 `--final-judgment` 标志，改为依赖 Capability 派生

- **Smoke 脚本** (`scripts/selected_funds_smoke.py:274`)：
  - `build_analyze_command()` 已包含 `--dev-override`
  - Smoke 测试 (`tests/scripts/test_selected_funds_smoke.py`) 断言 `"--dev-override" in command`

- **Service 测试** (`tests/services/test_fund_analysis_service.py`)：
  - `_developer_request()` helper 构造 `mode="developer_override"` + nested `FundAnalysisDeveloperOverrides`
  - 新增 product mode 最小请求路径验证

- **Template 测试** (`tests/fund/template/test_renderer.py`)：
  - `_render_input()` 改为构造 `FinalJudgmentDecision` 而非直接传 `final_judgment` 字符串
  - 审计输入断言新增 `derived_final_judgment` 和 `final_judgment_source`

**所有旧调用点已迁移，无遗漏。**

### 6. docs 是否以代码为准且不越界

**通过。** 逐文档检查：

- **`README.md`**：5 分钟跑通命令从 13 个参数收窄为 `fund-analysis analyze 004393 --report-year 2024`；参数表移除所有 dev 参数；明确 product mode 和 `--dev-override` 的定位；quality gate 说明补充 `--dev-override` 限制。**未把 developer override 写进用户成功路径。**
- **`fund_agent/README.md`**：Service 边界描述新增 mode 解析和 quality gate 归一化；Fund Capability 边界新增最终判断派生。**未越界到 Engine/Fund 内部实现。**
- **`fund_agent/fund/README.md`**：R2 描述从"最终判断与检查清单信号矛盾"更新为"selected/derived/source 与检查清单信号矛盾"；renderer 输入从 `final_judgment` 更新为 `FinalJudgmentDecision`；新增最终判断派生 policy 和开发者覆盖冲突审计说明。**以代码为准，不设计未来。**
- **`docs/design.md`**：核心契约表新增 `FinalJudgmentDecision` 行；`FundAnalysisRequest` 描述从罗列字段改为 product/developer override 双层说明；错误处理矩阵补充最终判断 fail-safe。**不写未实现的自动映射能力。**
- **`tests/README.md`**：新增 `test_final_judgment.py` 条目；更新 audit/Service/CLI/smoke 测试覆盖描述。**与当前测试文件一致。**

**所有文档更新均为描述当前实现，无越界、无未来承诺、无新旧术语并存。**

## Positive Observations

1. **`FinalJudgment` / `FinalJudgmentSource` / `FinalJudgmentDecision` 单一定义点**在 `fund_agent/fund/analysis/final_judgment.py`。renderer（`renderer.py:18`）和 audit（`audit_programmatic.py:15`）均从此 import，已删除各自的重复 Literal 定义。
2. **`derive_final_judgment()` 优先级正确**：`suggest_replace` 规则（否决项、红灯、-20% 越界）在 `needs_attention` 规则（gate block/not_run、黄灯/灰灯/watch）之前求值，`worth_holding` 仅在无任何负面信号时返回，未命中时 fail-safe 默认 `needs_attention`。
3. **`_check_pool_membership_before_extraction()` 性能优化**：block 策略下在年报抽取前先做轻量 CSV 成员检查，避免浪费昂贵 I/O。
4. **无 `extra_payload`、无 dict 兜底**：所有参数显式声明在 `FundAnalysisRequest` 或 `FundAnalysisDeveloperOverrides` 中。
5. **无新增 PDF/cache/filesystem 直接访问**：Service、UI、renderer、final_judgment 均未绕过 `FundDocumentRepository`。
6. **测试覆盖完整**：88 targeted + 365 full suite 全部通过，ruff 通过。

## Review Checklist (from plan §9)

| 检查项 | 状态 |
|---|---|
| product mode 最小输入，不暴露 `final_judgment` 为普通用户输入 | ✓ |
| developer override 显式 `--dev-override`，与 product path 分离 | ✓ |
| `FundAnalysisRequest` 无 `extra_payload` 或 dict 兜底 | ✓ |
| final judgment 派生在 Fund Capability，不在 UI | ✓ |
| R2 同时审计 derived judgment 和 developer override 冲突 | ✓ |
| quality gate product mode 保持 block fail-closed，warn/off 仅限 dev override | ✓ |
| Service/UI/renderer/audit 无直接 PDF/cache/filesystem 访问 | ✓ |
| 未引入外部 Dayu runtime/LLM/Host/Engine/tool loop | ✓ |
| 测试覆盖 product minimal path、dev override path、final judgment policy、R2 conflict、CLI gating | ✓ |
| README/design/doc 只描述当前实现，不写未来能力 | ✓ |
