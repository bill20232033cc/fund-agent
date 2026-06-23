# Plan Review — Evidence Confirm Default-on Policy Plan

## Review Metadata

- **Reviewer role**: AgentDS independent plan reviewer
- **Reviewed target**: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`
- **Work unit**: Evidence Confirm Productionization default-on Evidence Confirm policy
- **Current gate**: plan review
- **Review date**: 2026-06-23
- **Design truth**: `docs/design.md`
- **Control truth**: `docs/implementation-control.md`, `docs/current-startup-packet.md`
- **Goal-confirmation**: `docs/reviews/evidence-confirm-productionization-release-readiness-goal-confirmation-20260623.md`
- **Requirements audit**: `docs/reviews/evidence-confirm-productionization-release-readiness-requirements-audit-20260623.md`
- **Review scope**: adversarially evaluate whether the plan is code-generation-ready; whether default `warn` is justified; whether checklist `off` is a safe scoped choice; whether developer override remains bounded; whether tests prove product default behavior; whether docs/control sync is sufficient; whether boundaries remain intact

## Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|--------|
| A1 | Default `warn` for `analyze` is the correct release-readiness step (not `block`) | Supported — multi-sample live coverage and provider-backed semantic quality remain unproven per control truth; `warn` makes EC visible without converting unproven coverage into a hard blocker |
| A2 | Product default change only affects `analyze` CLI command | **Falsified** — `_resolve_analyze_contract()` product branch also serves `analyze_multi_year_annual()` → `analyze-annual-period` CLI; see Finding 1 |
| A3 | Developer override path remains bounded and doesn't leak into product mode | Supported — CLI rejects `--evidence-confirm-policy` without `--dev-override` (line 3037-3064); Service rejects `developer_overrides` in product mode (line 1568-1570) |
| A4 | `_effective_evidence_confirm_policy()` checklist `off` behavior is unchanged | Supported — plan explicitly keeps this invariant (plan line 125); function is not in allowed file change list for behavior changes |
| A5 | Existing ECQ mapping in `quality_gate_integration.py` is sufficient for product default `warn` | Supported — `_ecq_policy_severity()` already maps non-`block` policy to `SEVERITY_WARN` (line 304-308 in quality_gate_integration.py); existing test `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` already covers this path (line 262) |
| A6 | `_echo_evidence_confirm_summary()` already handles `warn` policy output correctly | Supported — function is called unconditionally at CLI line 902; it reads `summary.status` / `summary.policy` / `summary.checked_fact_count` etc. which are policy-agnostic fields |
| A7 | No new CLI flag or product opt-out is needed | Supported — plan explicitly rejects `--no-evidence-confirm` (plan line 207) |
| A8 | `_raise_evidence_confirm_block_if_required()` correctly handles `warn` as no-op | Supported — line 1748 checks `summary.policy == "block"`, so warn is a no-op |
| A9 | `analyze_with_llm()` path is unaffected or separately handled | **Unacknowledged** — LLM paths call `_run_analysis_core()` → `_resolve_analyze_contract()`, so they also inherit default `warn`; plan doesn't discuss this; see Finding 1 |

## Findings

### 1-未修复-中-`_resolve_analyze_contract()`产品分支变更影响范围未完全声明

- **位置**: 计划 First-principles Judgment 第 29-37 行、Non-goals 第 67-75 行、Slice EC-DO-1 Exact changes 第 155-164 行
- **问题类型**: 范围漂移
- **当前写法**: 计划声明 "Default-on should apply to `analyze` only in this work unit"（第 29 行），且非目标仅列出 `checklist`，未提及 `analyze-annual-period` 或 `analyze_with_llm` 路径
- **反例/失败场景**: `_resolve_analyze_contract()` 的 product 分支服务于所有走 `_run_analysis_core()` 的调用方：
  1. `analyze()` → `_run_analysis_core()`（product mode）
  2. `checklist()` → `_run_analysis_core()`（product mode，但 `_effective_evidence_confirm_policy(command_source="checklist")` 固定返回 `"off"`，不受影响）
  3. `analyze_multi_year_annual()` → `analyze()` → `_run_analysis_core()`（`_multi_year_developer_overrides()` 在 quality gate 全默认时返回 `None`，导致 `mode="product"`，见 `fund_agent/services/fund_analysis_service.py:1824-1831`、`863`）
  4. `analyze_with_llm()` → `_run_analysis_core()`（product mode，见 `fund_agent/services/fund_analysis_service.py:930`）
  5. `analyze_with_llm_hosted()` → `analyze_with_llm_execution()` → `analyze_with_llm()` → 同上

  路径 3 会导致 `analyze-annual-period` CLI 默认运行 Evidence Confirm。路径 4/5 会导致 `--use-llm` 路径默认运行 Evidence Confirm。计划未声明这些影响，也未为它们指定测试
- **为什么有问题**: 与 success signal 第 1 条 "default product `fund-analysis analyze` runs repository-bounded Evidence Confirm" 冲突——该表述暗示只有 `analyze` 受影响，但代码事实是共享 product 分支影响多条路径。`checklist` 不受影响是因为 `_effective_evidence_confirm_policy()` 做了显式路径区分，但 `analyze-multi-year-annual` 和 `analyze_with_llm` 没有类似保护
- **直接证据**:
  - `fund_agent/services/fund_analysis_service.py:1568-1587` — `_resolve_analyze_contract()` product 分支，计划要改为 `evidence_confirm_policy="warn"`
  - `fund_agent/services/fund_analysis_service.py:853-866` — `analyze_multi_year_annual()` 构造 `FundAnalysisRequest(mode="product", ...)`
  - `fund_agent/services/fund_analysis_service.py:930` — `analyze_with_llm()` 调用 `self._run_analysis_core(replace(request, command_source="analyze"))`
  - `fund_agent/services/fund_analysis_service.py:1658-1683` — `_effective_evidence_confirm_policy()` 只区分 `analyze`/`checklist`，不区分 `analyze-annual-period`/`analyze_with_llm`
  - 计划 line 29: "Default-on should apply to `analyze` only in this work unit"
  - 计划 non-goals line 67-75: 未提及 `analyze-annual-period` 或 LLM 路径
- **影响**: 实施 Agent 可能漏写受影响路径的测试；product 用户使用 `analyze-annual-period` 或 `--use-llm` 时默认看到 Evidence Confirm 输出但计划未声明此行为；后续若需要为不同路径配不同默认策略，缺乏文档记录
- **建议改法和验证点**:
  1. 在计划中显式声明：`analyze-annual-period` 和 `analyze_with_llm` 路径是否也接受默认 `warn`
  2. 若接受：补充对应的产品默认路径 test（至少各一个）
  3. 若不接受：在对应路径中显式 override `evidence_confirm_policy="off"` 或修改 `_effective_evidence_confirm_policy()` 增加路径区分
- **修复风险（低）**:
- **严重程度（中）**:

### 2-未修复-低-开发覆盖模式中`--dev-override`单独使用会静默禁用Evidence Confirm

- **位置**: 计划 Contract And State-machine Changes 第 120-126 行、Risks And Open Questions 第 325 行
- **问题类型**: 契约缺失
- **当前写法**: 计划第 325 行说明 developer override 可以显式 `off`，但未声明 `--dev-override` 单独使用（不传 `--evidence-confirm-policy`）时的行为
- **反例/失败场景**: 开发者执行 `fund-analysis analyze 110011 --dev-override` 时，CLI 默认 `evidence_confirm_policy="off"`（`fund_agent/ui/cli.py:753`）。`_has_developer_override_options()` 仅在 `evidence_confirm_policy != "off"` 时标记（line 2207），纯 `--dev-override` 不触发任何 provided option。`_build_developer_overrides()` 仍构造 `FundAnalysisDeveloperOverrides(evidence_confirm_policy="off")`，导致 developer 模式下 Evidence Confirm 被静默禁用——开发者可能未意识到已关闭 EC
- **为什么有问题**: 非 bug（计划有意保持 developer sandbox 的 `off` 默认），但耦合关系不透明。产品默认 `warn` 与 developer 默认 `off` 之间的差异应显式声明，避免开发者误以为 `--dev-override` 保留了产品默认
- **直接证据**:
  - `fund_agent/ui/cli.py:747-753` — CLI `--evidence-confirm-policy` 默认值为 `"off"`
  - `fund_agent/ui/cli.py:2207` — `evidence_confirm_policy != "off"` 时标记为 provided
  - `fund_agent/ui/cli.py:2275-2278` — provided_options 为空但 `dev_override=True` 时不报错，构造默认 overrides
- **影响**: 低。文档读者可能误以为 developer 模式保持产品默认
- **建议改法和验证点**: 在 Risks 章节添加一句："不带 `--evidence-confirm-policy` 的 `--dev-override` 使用 CLI 默认值 `off`，会静默禁用 Evidence Confirm。这是 developer sandbox 的预期行为"
- **修复风险（低）**:
- **严重程度（低）**:

### 3-未修复-低-docstring更新目标位置未枚举

- **位置**: 计划 Slice EC-DO-1 Exact changes 第 159 行
- **问题类型**: 不可直接实施
- **当前写法**: "Update docstrings/comments that say Evidence Confirm is developer-only so they say product `analyze` default is warn and developer override can override it."
- **反例/失败场景**: 实施 Agent 需自行搜索全部 "developer" / "developer-only" / "opt-in" 提及并判断是否需要更新。当前代码中至少 3 处 docstring 明确将 EC 描述为 developer-only：
  - `_run_evidence_confirm_if_enabled()` docstring（line 1313）："按 developer override 策略运行 Evidence Confirm"
  - `_effective_evidence_confirm_policy()` docstring（line 1664-1666）："Slice 2 只开放 `analyze()` developer override opt-in；`checklist()` 在本 slice 固定为 `off`"
  - `FundAnalysisDeveloperOverrides.evidence_confirm_policy` 字段 docstring（line 226）："Evidence Confirm 生产集成策略；只在 developer override mode 生效"
- **为什么有问题**: 模糊指令迫使实施 Agent 自行判断范围，可能遗漏关键 docstring；若遗漏 `_effective_evidence_confirm_policy` 的 docstring，后续读者会读到过时的"Slice 2 只开放 analyze developer override opt-in"描述
- **直接证据**: 上述 3 处代码引用
- **影响**: 实施 Agent 可能漏更新，导致文档与代码行为不一致
- **建议改法和验证点**: 在计划中列出上述 3 处具体 docstring 及建议的更新措辞
- **修复风险（低）**:
- **严重程度（低）**:

## Architecture Boundary Review

逐层检查四层边界 `UI -> Service -> Host -> Agent`：

| 边界 | 检查结果 |
|------|---------|
| Service → Fund (Agent 层) | 计划不新增 Service 对 repository/PDF/cache/source/parser/provider 的直接访问。`_run_evidence_confirm_if_enabled()` 继续通过注入 runner 调用，只消费 `project_chapter_facts(structured_data)`。**边界完整** |
| UI → Service | CLI 只更新 help text、移除旧 no-EC-lines 断言。不新增 flag、不添加 product opt-out。**边界完整** |
| Service → Quality Gate (Agent 层) | 计划不修改 `score.json` schema，ECQ 映射继续通过 `_ecq_policy_severity()` 处理。现有 `warn→SEVERITY_WARN` 逻辑已覆盖。**边界完整** |
| Service → Renderer (Agent 层) | 计划不向 report Markdown 注入 EC 内容。**边界完整** |
| Host 层 | 计划不引入 Host 层变更。**无影响** |

## Best-Practice Review

- **Default 策略**: `warn` 而非 `block` 有充分证据支撑——requirements audit 和 control truth 均记录 multi-sample live coverage 和 provider-backed semantic quality 为 unproven。`warn` 使 EC 对产品用户可见但不将未证明覆盖转化为硬阻断。正确选择
- **变更集中度**: 单点变更 `_resolve_analyze_contract()` 的默认值，blast radius 最小
- **测试覆盖**: 计划指定了 5 场景的 Service 测试（pass/fail/checklist-off/block-block/product-reject）和 5 场景的 CLI 测试（default-summary/reject/block-exit/checklist-help/checklist-reject），覆盖 happy path 和 2 条 failure path
- **Stop conditions**: 每个 slice 有显式 stop condition，防止 scope creep

## Overengineering Review

计划未引入新 abstraction、layer、builder、wrapper、protocol、migration、schema 扩展或 future hook。无过度设计。

## Overcoupling Review

- `_resolve_analyze_contract()` product 分支被多条路径共享（见 Finding 1），但这是现有代码结构，非本计划引入的耦合
- `checklist` 通过 `_effective_evidence_confirm_policy()` 显式解耦
- Quality gate、renderer、CLI 各自独立修改，无跨层穿透

## Open Questions

1. `analyze-annual-period` 和 `analyze_with_llm` 路径默认是否也应启用 Evidence Confirm？计划未声明。需 plan author 确认意图（见 Finding 1）
2. 产品默认 `warn` 的 stderr 输出对首次用户是否需要额外说明？现有 `_echo_evidence_confirm_summary()` 字段（status/policy/checked_facts/failed_facts/auditability_score）对非开发者可能不直观——但不阻塞实施

## Residual Risks

| Risk | Severity | Tracking |
|------|----------|----------|
| 未声明的受影响路径缺少测试 | 中 | 本次实施澄清后补测试或显式排除 |
| Docstring 更新不完整 | 低 | 实施后 `grep -n 'developer.*override.*Evidence\|developer.only.*Evidence\|Slice 2' fund_agent/services/fund_analysis_service.py` 验证 |
| 用户首次看到 EC stderr 不理解 | 低 | 后续 UX gate |

## Verdict

**PLAN_REVIEW_PASS_WITH_FINDINGS**

计划结构清晰、架构边界完整、变更范围最小、默认 `warn` 策略有理有据。一个中严重度 finding（产品分支影响范围未完全声明）需要 plan author 澄清意图后即可进入实施。三个低严重度 finding 不阻塞实施。
