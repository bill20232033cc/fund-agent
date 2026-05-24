# Aggregate Deep Review: P19-S6 Production Validation

## Scope

- **Mode**: current changes (aggregate review, not standard deepreview)
- **Branch**: `phase/p19-s6-production-validation`
- **Base**: `origin/main` at `bbec908`
- **Output file**: `docs/reviews/p19-s6-aggregate-deepreview-ds-20260523.md`
- **Gate**: P19-S6 aggregate review before ready-to-open-draft-PR
- **Design truth**: `docs/design.md` §11 / §12
- **Control truth**: `docs/implementation-control.md`
- **Included scope**:
  - Full diff `origin/main...HEAD` (4 commits: `7968ed8`, `a6e73bf`, `27eb08a`, `08fc354`)
  - Accepted plan: `docs/reviews/p19-s6-production-validation-plan-20260523.md`
  - Accepted plan reviews: `docs/reviews/plan-review-20260523-182056.md`, `docs/reviews/plan-review-20260523-182146.md`
  - Accepted implementation artifact: `docs/reviews/p19-s6-production-validation-implementation-20260523.md`
  - Accepted code review: `docs/reviews/code-review-20260523-183037.md`
  - Test files: `tests/services/test_fund_analysis_service.py`, `tests/fund/integration/test_p3_cli_e2e_matrix.py`
  - Doc file: `tests/README.md`, `docs/implementation-control.md`
- **Excluded scope**:
  - Unrelated untracked repo-level deepreview files (`docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`, `docs/reviews/agentds-repo-deepreview-20260523.md`, `docs/reviews/agentglm-repo-deepreview-20260523.md`, `docs/reviews/controller-judgment-repo-deepreview-20260523.md`)
  - P19-S4 deferred artifacts, P19-S5 closed artifacts, unrelated phase artifacts
  - Production code (no production files changed in this diff)
- **Parallel review coverage**: 无。本次 aggregate review 由主 reviewer 独立完成，未使用 subagent。

## Conclusion

**PASS_WITH_FINDINGS**

P19-S6 实现严格遵循已接受计划，零生产代码变更，全部改动限定在测试与文档。两条低严重度 finding 涉及 plan slice 隐式覆盖与 CLI 负向路径缺位，均不阻塞 ready-to-open-draft-PR。无设计边界违规、无温度计估值集成安全风险、无生产行为变更。

## Findings

### 1-未修复-低-S6-2/S6-3/S6-4 三个 plan slice 无新增专属测试，完全依赖 P19-S5 存量覆盖

- **入口/函数**: P19-S6 计划 slices S6-2 (Thermometer CLI matrix)、S6-3 (concurrency regression guard)、S6-4 (public-page comparison boundary)
- **文件(行号)**: `docs/reviews/p19-s6-production-validation-plan-20260523.md` line 75–156
- **输入场景**: 实现阶段按计划条件语言（"Keep or add"、"only if current tests do not already fail"、"document that evidence and do not add duplicate tests"）判定存量 P19-S5 测试已满足要求，未新增任何专属测试。
- **实际分支**: 实现 artifact 与 code review 均接受了存量覆盖即充分的结论；`tests/ui/test_cli.py`、`tests/services/test_thermometer_service.py`、`tests/fund/data/test_thermometer_source.py`、`tests/fund/data/test_thermometer.py` 零 diff 变更。
- **预期行为**: 计划允许条件性跳过新增测试，但 aggregate review 应独立验证每个 slice 确有可追溯的覆盖证据。
- **实际行为**: 三个 slice 的覆盖证据仅来自 code review 中一条验证结果行（`64 passed`、`60 passed`），没有逐项映射 slice 要求到具体已有测试用例的记录。未来若 P19-S5 测试因重构被移除或修改，这三个 slice 的回归保护会静默消失。
- **直接证据**:
  - `docs/reviews/p19-s6-production-validation-implementation-20260523.md` 的 Changes 节只列出了 S6-1 和 S6-6 的实际文件变更，未提及 S6-2/S6-3/S6-4。
  - `docs/reviews/code-review-20260523-183037.md` 的 Validation 节给出了组合测试通过数，但未逐 slice 核对。
  - `git diff origin/main...HEAD -- tests/ui/test_cli.py tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer.py` 返回空。
- **影响**: 三个 slice 的回归保护完全依赖 P19-S5 测试不被意外削弱。当前不构成缺陷，但属于 residual risk 记录不完整。
- **建议改法和验证点**: 不要求新增代码。建议在 control doc 或本 artifact 的 Residual Risk 中显式记录 S6-2/S6-3/S6-4 的存量测试映射（例如 S6-2 → `test_cli.py` 的 `test_thermometer_json_default`、`test_thermometer_index_000300_json` 等），使未来维护者可快速定位。
- **修复风险（低）**: 纯文档补强。
- **严重程度（低）**: 计划的条件语言已授权此行为，当前无正确性问题。

### 2-未修复-低-CLI e2e 负向路径仅有 Service 层覆盖，缺少 CLI 层回归

- **入口/函数**: `test_p19_s6_cli_auto_valuation_uses_exact_index_thermometer` 及其覆盖范围
- **文件(行号)**: `tests/fund/integration/test_p3_cli_e2e_matrix.py` line 655–695；`tests/services/test_fund_analysis_service.py` line 588–653
- **输入场景**: 用户对 510300（沪深300ETF）省略 `--valuation-state`，触发 CLI → Service → thermometer 自动估值正路径。
- **实际分支**: CLI e2e 只覆盖了 exact `000300` 正路径。计划要求的 "negative CLI or Service assertion" 选择了 Service 层实现（`test_fund_analysis_service_unsupported_exact_index_does_not_call_thermometer`、`test_fund_analysis_service_ambiguous_supported_indices_do_not_call_thermometer`）。
- **预期行为**: 计划写的是 "add a negative CLI or Service assertion"，Service 层实现符合"or"语义。但 CLI 层缺少对 unsupported/ambiguous 场景的端到端验证，无法证明 CLI 参数解析→Service 编排→灰灯输出的完整链路在负向场景下不会意外调用温度计。
- **实际行为**: CLI 负向路径未被端到端测试。如果未来 CLI 参数解析或 Service 装配逻辑引入回归（例如错误地为 399006 触发了温度计调用），Service 层单测可能捕获，但 CLI 层的参数传递链路不会被测试。
- **直接证据**:
  - `tests/fund/integration/test_p3_cli_e2e_matrix.py` 只有一个新增测试函数 `test_p19_s6_cli_auto_valuation_uses_exact_index_thermometer`，仅覆盖正路径。
  - 计划 `docs/reviews/p19-s6-production-validation-plan-20260523.md` line 64: "add a negative CLI or Service assertion"。
  - 实现选择了 Service 层，符合计划的 "or" 措辞。
- **影响**: CLI 层负向回归盲区。当前风险很低，因为 CLI 层只是 thin wrapper，不包含估值决策逻辑。
- **建议改法和验证点**: 不阻塞当前 gate。可在后续 production hardening 中追加一条 CLI e2e 负向用例（例如对 QDII 基金 110011 去掉 `--valuation-state`，断言输出包含灰灯且不调用温度计）。
- **修复风险（低）**: 纯测试追加。
- **严重程度（低）**: 计划"or"语义已授权；CLI 层是 thin wrapper，估值逻辑在 Service 层已有充分覆盖。

## Plan Compliance

逐 slice 核对：

| Slice | 计划要求 | 实现证据 | 判定 |
|-------|---------|---------|------|
| S6-1 | Service 正路径 000300/000905，负路径 399006/歧义/显式覆盖；CLI e2e 正路径 + 温度计免责声明 | `test_fund_analysis_service.py` 新增 4 个测试；`test_p3_cli_e2e_matrix.py` 新增 1 个测试 | **通过** |
| S6-2 | Thermometer CLI 矩阵 (default/single/batch/partial unavailable/malformed) | P19-S5 存量测试，validation 确认 64+60 passed | **通过（存量覆盖）** |
| S6-3 | Concurrency regression guard | P19-S5 存量 sequential PE/PB 测试 | **通过（存量覆盖）** |
| S6-4 | Public-page comparison boundary | P19-S5 存量 `test_thermometer.py` adapter/parser 测试 | **通过（存量覆盖）** |
| S6-5 | Live smoke docs | `tests/README.md` 新增 smoke 命令与免责声明 | **通过** |
| S6-6 | Control/doc closeout | `implementation-control.md` 更新 gate/artifacts；`tests/README.md` 同步 | **通过** |

## Design Boundaries

- **无新增支持指数代码**：diff 中零生产代码变更，`000300`/`000905` 之外无新指数。
- **无 P19-S4 重试**：`399006` 仅作为负向测试用例，不尝试接入数据源。
- **无公开页抓取作为生产真源或 fallback**：公开页代码路径零变更。
- **无扩宽自动估值映射**：仅 `index_fund` + exact `000300` 和 `enhanced_index` + exact `000905` 可触发。
- **无 Dayu/LLM/Evidence Confirm**：零相关变更。
- **无年报仓库访问边界变更**：测试使用 fake repository。
- **无 RR-13/CSV 编辑**：零变更。
- **无 extra_payload 参数**：零变更。
- **模块边界**：测试代码均在 `tests/` 下，通过 fake extractor/thermometer/repository 隔离，不穿透访问 Capability 内部实现。

## Thermometer Valuation Integration Safety

逐项验证自动估值温度计集成安全：

| 场景 | 测试覆盖 | 断言 |
|------|---------|------|
| 沪深300 index_fund + exact 000300 | Service + CLI e2e | `source=="self_owned_thermometer"`, `index_code=="000300"` |
| 中证500 enhanced_index + exact 000905 | Service | `source=="self_owned_thermometer"`, `index_code=="000905"` |
| 不支持的 exact code 399006 | Service | `source=="unavailable_mapping"`, `calls==[]` |
| 复合基准歧义 (沪深300+中证500) | Service | `source=="unavailable_mapping"`, `calls==[]` |
| 主动基金不调用 | Service | `source=="unavailable_mapping"`, `calls==[]` |
| 显式 --valuation-state 短路 | Service | `source=="explicit_user_input"`, `calls==[]` |
| 显式 unavailable 手动灰灯 | Service | `source=="explicit_user_input"`, signal==gray |
| 温度计读数 unavailable | Service | `source=="unavailable_thermometer"` |
| 温度计计算错误→灰灯 | Service | `source=="unavailable_thermometer"`, reason 包含错误信息 |
| 返回指数与目标不一致→ValueError | Service | `pytest.raises(ValueError)` |
| Provider 返回 None/批量/快照→ValueError | Service | `pytest.raises(ValueError)`, 参数化 3 种非法值 |
| CLI 报告含温度计免责声明 | CLI e2e | `"本温度计基于有知有行公开方法论独立计算" in output` |
| CLI 报告含 external_api 证据锚点 | CLI e2e | `"外部数据(external_api)§thermometer" in output` |
| force_refresh 转发 | CLI e2e + Service | `thermometer.calls[0].force_refresh is True` |
| cache_dir 转发 | Service | `thermometer.calls[0].cache_dir == tmp_path` |

全部场景有直接断言覆盖，无间接证据替代。

## No Production Behavior Change

`git diff origin/main...HEAD -- fund_agent/` 返回空。本次分支的 4 个 commit 中：

- `7968ed8` (plan): 仅新增 `docs/reviews/` 下的 plan/review artifacts，更新 `docs/implementation-control.md`
- `a6e73bf` (implement): 仅修改 `tests/` 和 `tests/README.md`
- `27eb08a` (test fix): 仅修改 `tests/services/test_fund_analysis_service.py`
- `08fc354` (code review accept): 仅更新 `docs/implementation-control.md`

零生产代码变更。所有 `fund_agent/` 下的模块、Service、Engine、Capability、UI、Config 均未被 touch。

## Test Adequacy

**已覆盖**：
- Service 层自动估值正路径 (000300, 000905) 与负路径 (399006, 歧义复合, 主动基金)
- CLI e2e 自动估值正路径 (510300 → 000300)
- 显式估值短路、unavailable、温度计不可用、计算错误、identity mismatch、contract error
- 温度计免责声明与 evidence anchor 渲染
- 8 章完整性 + 程序审计 (P1/P2/P3/C2/L1/R1/R2)
- force_refresh/cache_dir 参数转发

**未覆盖（已知 & 已记录）**：
- CLI e2e 负向路径 (见 Finding 2)
- S6-2/S6-3/S6-4 无新增专属测试 (见 Finding 1)
- 真实 akshare/native dependency 可用性 (设计上 opt-in live smoke，不进入 CI)
- 公开页方向比较精确数值 (设计上只做 directional comparison)

**验证结果**（来自 code review artifact）：
- Service/analyze: 43 passed
- P3 CLI e2e: 2 passed
- Thermometer data: 60 passed
- Service/UI: 64 passed
- Full suite: 599 passed
- ruff: passed
- git diff --check: passed

## README Sync

- `tests/README.md`:
  - Service 测试描述更新为包含沪深300/中证500 exact identity 调用 ✅
  - P3 CLI e2e 描述更新为包含 P19-S6 自动估值样本 ✅
  - 新增 P19-S6 确定性回归组合命令 ✅
  - 新增 live smoke 命令与免责声明 ✅
  - 维护约定更新：fake thermometer 加入隔离列表 ✅
  - Service 测试约定更新：显式断言 unsupported/ambiguous 不调用温度计 ✅
- `docs/implementation-control.md`:
  - Startup Packet 更新 branch/gate/next entry point ✅
  - P19-S6 artifacts 录入台账 ✅
  - Resume checklist 更新 P19-S6 历史 ✅

未触发更新的 README（符合计划）：
- root `README.md`：无 user-visible command 变更
- `fund_agent/fund/README.md`：Fund capability 行为未变
- `fund_agent/engine/README.md`：Engine 未变

## Adversarial Failure Pass

- **生产代码零变更**：无法引入 regression、data loss、race condition、privilege escalation
- **测试隔离**：所有新增测试使用 fake extractor/thermometer/repository/nav_provider，不触发网络/文件系统副作用
- **Fake thermometer 契约守卫**：`_FakeThermometerService.run()` 内有 `assert request.index_code is not None` 和 `assert request.index_codes is None`，防止测试误用批量请求
- **负向断言直接性**：unsupported/ambiguous 测试断言 `thermometer.calls == []`，不依赖灰灯间接推断
- **Fail-closed 全覆盖**：identity mismatch、contract error (None/batch/snapshot)、calculation error 均有 `pytest.raises` 断言
- **force_refresh 转发验证**：CLI e2e 断言 `thermometer.calls[0].force_refresh is True`，确保 `--force-refresh` 穿透到温度计层

## Open Questions

无。

## Residual Risk

- **S6-2/S6-3/S6-4 存量覆盖映射未文档化**（Finding 1）：三个 slice 无新增专属测试，依赖 P19-S5 测试持续通过。建议在 control doc 中记录具体存量测试到 slice 的映射。
- **CLI 负向路径无 e2e 覆盖**（Finding 2）：unsupported/ambiguous 场景仅在 Service 层验证，CLI 薄层存在理论上的回归盲区。
- **真实 akshare/native dependency 可用性**：仅能通过 opt-in live smoke 验证，不在 CI 中运行。这是设计决策，不是缺陷。
- **公开页方向比较**：仅作为合理性信号，不承诺精确数值复刻。这是设计决策，不是缺陷。
- **P19-S4 扩展指数覆盖**：仍处于 deferred 状态，不在 P19-S6 scope 内。
