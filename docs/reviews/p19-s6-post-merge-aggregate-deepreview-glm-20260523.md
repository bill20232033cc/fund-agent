# Code Review

## Scope

- Mode: current changes (post-merge aggregate reconciliation review)
- Branch: `main` at `3769def`
- Base: `main` at `bbec908` (pre-P19-S6)
- Output file: `docs/reviews/p19-s6-post-merge-aggregate-deepreview-glm-20260523.md`
- Included scope:
  - PR 14 merge commit `45bea3e` (4 source commits: `7968ed8`, `a6e73bf`, `27eb08a`, `08fc354`)
  - Closeout commit `3769def`
  - `docs/implementation-control.md` Startup Packet / 台账 / resume checklist
  - `docs/reviews/p19-s6-production-validation-plan-20260523.md` (accepted plan)
  - `docs/reviews/p19-s6-production-validation-implementation-20260523.md`
  - `docs/reviews/code-review-20260523-183037.md`
  - `docs/reviews/p19-s6-aggregate-deepreview-ds-20260523.md`
  - `tests/README.md`
  - `tests/fund/integration/test_p3_cli_e2e_matrix.py`
  - `tests/services/test_fund_analysis_service.py`
- Excluded scope:
  - Untracked repo-level deepreview files (`docs/design0522.md`, `docs/implementation-control0522.md`, `docs/reviews/agentds-repo-deepreview-20260523.md`, `docs/reviews/agentglm-repo-deepreview-20260523.md`, `docs/reviews/controller-judgment-repo-deepreview-20260523.md`)
  - `docs/repo-audit-20260521.md`
  - Production code (`fund_agent/`) — verified zero diff
- Parallel review coverage: 无。本次 aggregate review 由主 reviewer 独立完成，未使用 subagent。

## Findings

### 1-未修复-低-closeout commit 遗留 control doc prose 行与 Startup Packet 表字段不一致

- **入口/函数**: `docs/implementation-control.md` 文件头部 prose "当前状态" 行
- **文件(行号)**: `docs/implementation-control.md` line 9
- **输入场景**: Closeout commit `3769def` 更新了 Startup Packet 表的 `Current gate`、`Next entry point`、`Current phase` 三个字段，但未同步更新文件头部 prose "当前状态" 行。
- **实际分支**: Closeout commit diff 只修改了 Startup Packet 表内 3 行、台账 P19 状态行和 resume checklist 末尾追加，未触及 line 9 的 prose 概述。
- **预期行为**: Prose "当前状态" 应与 Startup Packet 表字段保持一致，反映 P19 已关闭、当前处于 release maintenance 阶段。
- **实际行为**: Line 9 仍然写的是 `P19-S6 production validation code review accepted on branch；next entry point is P19-S6 aggregate review / ready-to-open-draft-PR reconciliation`，与表中 `Current gate: P19 closed`、`Next entry point: release maintenance`、`Current phase: release maintenance` 矛盾。Startup Packet `Branch` 字段仍为 `phase/p19-s6-production-validation`，该分支已通过 PR 14 合并。
- **直接证据**:
  - `git diff 45bea3e 3769def` 只修改了 `docs/implementation-control.md` 的 Startup Packet 表格行、台账行和 resume checklist，未触及 line 9。
  - Line 9 当前内容: `P19-S6 production validation code review accepted on branch；next entry point is P19-S6 aggregate review / ready-to-open-draft-PR reconciliation；P0-P19-S5 已合入主线并在下方台账归档`
  - 表字段当前内容: `Current gate: P19 closed`、`Next entry point: release maintenance`、`Current phase: release maintenance`
  - `Branch` 字段: `phase/p19-s6-production-validation`（已合并分支）
- **影响**: 文档内部不一致可能误导 future session 对当前状态的判断。但 Startup Packet 表字段是结构化真源，prose 行不是，实际影响很小。
- **建议改法和验证点**: 将 line 9 更新为与表字段一致，例如 `P19 closed；P0-P19-S6 已合入主线并在下方台账归档；当前处于 release maintenance 阶段`。同时考虑将 `Branch` 字段更新为 `main` 或空值。
- **修复风险（低）**: 纯文档修正。
- **严重程度（低）**: 结构化表字段是正确的真源，prose 行只是概述。

## Plan Compliance

逐 slice 核对：

| Slice | 计划要求 | 实现证据 | 判定 |
|-------|---------|---------|------|
| S6-1 | Service 正路径 000300/000905，负路径 399006/歧义/显式覆盖；CLI e2e 正路径 + 温度计免责声明 | `test_fund_analysis_service.py` 新增 4 个测试覆盖 000300/000905/399006/歧义；`test_p3_cli_e2e_matrix.py` 新增 1 个 CLI e2e 正路径 | **通过** |
| S6-2 | Thermometer CLI 矩阵 (default/single/batch/partial unavailable/malformed) | P19-S5 存量测试覆盖，validation 确认 64+60 passed | **通过（存量覆盖）** |
| S6-3 | Concurrency regression guard | P19-S5 存量 sequential PE/PB 测试 | **通过（存量覆盖）** |
| S6-4 | Public-page comparison boundary | P19-S5 存量 `test_thermometer.py` adapter/parser 测试 | **通过（存量覆盖）** |
| S6-5 | Live smoke docs | `tests/README.md` 新增 smoke 命令与免责声明 | **通过** |
| S6-6 | Control/doc closeout | `implementation-control.md` 更新 gate/artifacts/resume checklist | **通过** |

计划要求不可做的事项逐项验证：

| Non-Goal | 验证 |
|----------|------|
| 不新增支持指数代码 | `git diff bbec908..3769def -- fund_agent/` 返回空 |
| 不重试 P19-S4 | `399006` 仅作为负向测试用例 |
| 不使用公开页抓取作为生产真源 | 零相关变更 |
| 不扩宽自动估值映射 | 仅 `index_fund` + exact `000300` 和 `enhanced_index` + exact `000905` |
| 不引入 Dayu/LLM/Evidence Confirm | 零相关变更 |
| 不改年报仓库访问边界 | 测试使用 fake repository |
| 不编辑 RR-13/CSV | 零变更 |
| 不在 extra_payload 放参数 | 零变更 |

## Design Boundaries

- **无新增支持指数代码**：零生产代码变更，000300/000905 之外无新指数。
- **无 P19-S4 重试**：399006 仅作为负向测试用例，不尝试接入数据源。
- **无公开页抓取作为生产真源或 fallback**：公开页代码路径零变更。
- **无扩宽自动估值映射**：仅 P19-S3 已接受的 exact identity 可触发。
- **无 Dayu/LLM/Evidence Confirm**：零相关变更。
- **无年报仓库访问边界变更**：测试使用 fake repository。
- **无 RR-13/CSV 编辑**：零变更。
- **无 extra_payload 参数**：零变更。
- **模块边界**：所有变更限定在 `tests/` 和 `docs/`，通过 fake extractor/thermometer/repository/nav_provider 隔离，不穿透访问 Capability 内部实现。

## Zero Production Behavior Change

`git diff bbec908..3769def -- fund_agent/` 返回空。PR 14 的 4 个 source commit 和 closeout commit 3769def 合计：

- `7968ed8` (plan): 仅新增 `docs/reviews/` 下的 plan/review artifacts，更新 `docs/implementation-control.md`
- `a6e73bf` (implement): 仅修改 `tests/` 和 `tests/README.md`
- `27eb08a` (test fix): 仅修改 `tests/services/test_fund_analysis_service.py`
- `08fc354` (code review accept): 仅更新 `docs/implementation-control.md`
- `3769def` (closeout): 仅更新 `docs/implementation-control.md`

零生产代码变更。所有 `fund_agent/` 下的模块、Service、Engine、Capability、UI、Config 均未被 touch。

## DS Findings Review

DS aggregate deepreview (`docs/reviews/p19-s6-aggregate-deepreview-ds-20260523.md`) 结论为 `PASS_WITH_FINDINGS`，两条低严重度 finding：

### DS Finding 1: S6-2/S6-3/S6-4 无新增专属测试

- **DS 判定**: 低严重度，不阻塞
- **独立验证**: 计划的 "Keep or add"、"only if current tests do not already fail"、"document that evidence and do not add duplicate tests" 条件语言明确授权了存量覆盖。P19-S5 已有覆盖 thermometer CLI 矩阵、sequential PE/PB、public-page adapter/parser 的测试。
- **本 reviewer 裁决**: **accepted** — 低严重度，计划条件语言已授权，无正确性问题。DS 建议在 residual risk 中记录具体存量测试到 slice 的映射是合理的，但不阻塞。

### DS Finding 2: CLI e2e 负向路径缺位

- **DS 判定**: 低严重度，不阻塞
- **独立验证**: 计划 line 64 写的是 "add a negative CLI or Service assertion"，"or" 语义明确允许 Service 层实现。Service 层已有 3 个负向测试（399006、歧义复合、主动基金）直接断言 `thermometer.calls == []`，不依赖灰灯间接推断。CLI 层是 thin wrapper，估值决策逻辑在 Service 层。
- **本 reviewer 裁决**: **accepted** — 低严重度，计划 "or" 语义已授权。建议在后续 production hardening 中追加 CLI 负向 e2e 用例，但不阻塞当前 gate。

## Tests Adequacy

**已覆盖**：

- Service 层自动估值正路径 (000300, 000905) 与负路径 (399006, 歧义复合, 主动基金) — 直接断言 `thermometer.calls`
- CLI e2e 自动估值正路径 (510300 → 000300) — 经过真实 Typer CLI → Service → fake thermometer
- 显式估值短路、unavailable、温度计不可用、计算错误、identity mismatch、contract error (None/batch/snapshot) — `pytest.raises`
- 温度计免责声明与 external_api evidence anchor 渲染 — 字符串断言
- 8 章完整性 + 程序审计 (P1/P2/P3/C2/L1/R1/R2) — 结构化断言
- force_refresh/cache_dir 参数转发 — 字段级断言

**验证结果**（本 reviewer 在 main 上重新运行确认）：

- `pytest tests/fund/analysis/test_valuation_state.py tests/services/test_fund_analysis_service.py -q` → 43 passed
- `pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q` → 2 passed
- `ruff check fund_agent tests` → All checks passed

与 PR 14 code review artifact 记录的 599 passed / ruff passed / diff check passed 一致。

**未覆盖（已知 & 已记录）**：

- CLI e2e 负向路径 (DS Finding 2, 低, accepted)
- S6-2/S6-3/S6-4 无新增专属测试 (DS Finding 1, 低, accepted)
- 真实 akshare/native dependency 可用性 (设计上 opt-in live smoke)
- 公开页方向比较精确数值 (设计上只做 directional comparison)

## Control State Consistency

逐项核对 closeout commit `3769def` 后的 control doc 内部一致性：

| 字段 | 值 | 与事实一致性 |
|------|------|------------|
| Startup Packet `Branch` | `phase/p19-s6-production-validation` | 已合并分支名，历史记录性质，低优先级 |
| Startup Packet `Current gate` | `P19 closed` | 一致 — PR 14 已合并 |
| Startup Packet `Next entry point` | `release maintenance` | 一致 |
| Startup Packet `Current phase` | `release maintenance` | 一致 |
| 台账 P19 行状态 | `done` | 一致 |
| 台账 P19 行 Next action | `P19 closed; release maintenance` | 一致 |
| Resume checklist 新增行 | P19-S6 merged through PR 14... | 一致 |
| Line 9 prose "当前状态" | `P19-S6 production validation code review accepted on branch` | **不一致** — 见 Finding 1 |

Resume checklist 历史记录完整：P17-S1 → PR 12 → P19-S5 → P19-S6 逐条可追溯。

## Adversarial Failure Pass

- **生产代码零变更**：无法引入 regression、data loss、race condition 或 privilege escalation
- **测试隔离**：所有新增测试使用 fake extractor/thermometer/repository/nav_provider，不触发网络或文件系统副作用
- **Fake thermometer 契约守卫**：`_FakeThermometerService.run()` 内有 `assert request.index_code is not None` 和 `assert request.index_codes is None`，防止测试误传批量请求
- **负向断言直接性**：unsupported/ambiguous 测试断言 `thermometer.calls == []`，不依赖灰灯间接推断
- **Fail-closed 全覆盖**：identity mismatch、contract error、calculation error 均有 `pytest.raises(ValueError)` 断言
- **Closeout commit 只改文档**：`git diff 45bea3e 3769def` 只涉及 `docs/implementation-control.md`，无代码变更
- **Prose 行不一致**（Finding 1）：不阻塞但应修正

## Open Questions

无。

## Residual Risk

- **Control doc prose 行与表字段不一致**（Finding 1）：低严重度，应在下次 release maintenance session 修正
- **S6-2/S6-3/S6-4 存量覆盖映射未文档化**（DS Finding 1）：建议在 control doc 或本 artifact 中记录具体存量测试到 slice 的映射
- **CLI 负向路径无 e2e 覆盖**（DS Finding 2）：可在后续 production hardening 中追加
- **真实 akshare/native dependency 可用性**：仅能通过 opt-in live smoke 验证，不在 CI 中运行
- **公开页方向比较**：仅作为合理性信号，不承诺精确数值复刻
- **P19-S4 扩展指数覆盖**：仍处于 deferred 状态
- **Startup Packet Branch 字段**：仍指向已合并的 `phase/p19-s6-production-validation`，应在下次 session 更新
