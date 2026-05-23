# Code Review

## Scope

- Mode: PR
- PR: 16 — "Codex/checklist host engine design"
- URL: https://github.com/bill20232033cc/fund-agent/pull/16
- Author: bill20232033cc
- Head branch: `codex/checklist-host-engine-design` @ 23a3c32
- Base branch: `main` @ 3769def
- CI: test pass (20s)
- Output file: `docs/reviews/release-maintenance-pr-review-mimo-20260524.md`
- Included scope: PR 16 full diff (115 files, +5271/-8396)
- Excluded scope: local untracked `review_report.md` (not in PR diff)
- Parallel review coverage: 4 subagents reviewed (1) `fund_analysis_service.py` correctness, (2) `cli.py` + UI tests, (3) architecture guardrails, (4) terminology consistency

## Verdict

**PASS_WITH_FINDINGS**

PR 16 可以合入。三项低严重程度 finding 均为 docstring/doc 术语残留，不阻断 correctness、stability 或 architecture boundary。

## PR 内容概述

本 PR 包含三类改动：

1. **架构术语对齐**：将 AGENTS.md、README.md、design.md、implementation-control.md 及所有 fund_agent/ README 和 docstring 从旧六层术语（Application / Runtime / Engine / Capability）统一为 Dayu 四层（UI / Service / Host / Agent / fund_agent/fund）。
2. **checklist 独立 Service 入口**：在 `FundAnalysisService` 中提取 `_run_analysis_core()` 作为 analyze 与 checklist 的共享确定性分析核心；checklist 路径复用同一 quality gate、risk check、stress test、checklist 和 final judgment，只省略 8 章模板渲染与程序审计。
3. **文档清理与工程基线**：删除 20+ 过期文档；CI 增加 `--cov-fail-under=50` 覆盖率门槛；`pyproject.toml` 增加 `pythonpath = ["."]`。

## Guardrail Validation

| Guardrail | Result | Evidence |
|-----------|--------|----------|
| 无 `fund_agent/host` 或 `fund_agent/agent` 占位包 | **PASS** | PR diff 中无 `fund_agent/host/` 或 `fund_agent/agent/` 文件 |
| 无 `dayu.host` / `dayu.engine` 代码依赖 | **PASS** | `grep -r "dayu\.host\|dayu\.engine\|from dayu" fund_agent/` 仅在 README 文档中出现，无代码 import |
| 确定性路径 UI → Service → `fund_agent/fund` | **PASS** | `fund_agent/services/` 和 `fund_agent/ui/` 中无 `fund_agent.host` 或 `fund_agent.agent` import |
| 无显式参数隐藏在 `extra_payload` | **PASS** | 所有 `extra_payload` 出现均为 docstring 中的禁止声明 |
| `pyproject.toml` 无新 dayu 依赖 | **PASS** | 唯一改动为 `[tool.pytest.ini_options]` 增加 `pythonpath = ["."]` |
| `review_report.md` 不在 PR diff 中 | **PASS** | `git diff main...HEAD --name-only | grep review_report` 无结果 |

## Findings

### 1-未修复-低-docstring 残留旧术语 Engine/Runtime

- **入口/函数**: `fund_agent/fund/_value_utils.py` 模块 docstring
- **文件(行号)**: `fund_agent/fund/_value_utils.py:4`
- **输入场景**: 任何读取该模块 docstring 的开发者或工具
- **实际分支**: docstring 写"不依赖 Service、Engine、Runtime 或 UI 层"
- **预期行为**: 术语应统一为"不依赖 Service、Host 或 UI 层"（Engine/Runtime 是旧六层术语）
- **实际行为**: "Engine、Runtime" 旧术语残留
- **直接证据**: 第 4 行 `不依赖 Service、Engine、Runtime 或 UI 层`
- **影响**: 仅文档准确性；不影响运行时 correctness
- **建议改法和验证点**: 将 "Engine、Runtime" 改为 "Host"；grep 确认无其他 Engine/Runtime 残留
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 2-未修复-低-implementation-control.md P11 设计事实残留旧术语

- **入口/函数**: `docs/implementation-control.md` P11 设计事实段落
- **文件(行号)**: `docs/implementation-control.md:572`（及 519、536、539 行）
- **输入场景**: 开发者或 Agent 读取实施总控文档 P11 段落
- **实际分支**: 写 "Fund Capability" 而非 "Agent 层 fund_agent/fund"
- **预期行为**: 术语应统一为 Agent 层 `fund_agent/fund`
- **实际行为**: "Fund Capability" 旧术语残留
- **直接证据**: 第 572 行 "`fund-analysis analyze` remains deterministic UI -> Service -> Fund Capability"
- **影响**: 仅文档准确性；该段落在 Phase 历史记录区域，影响较低
- **建议改法和验证点**: 将 "Fund Capability" 改为 "Agent 层 `fund_agent/fund`"；Startup Packet 第 19 行已声明 archive 段落旧术语为历史证据，不阻断
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 3-未修复-低-_echo_quality_gate_summary 鸭子类型跨结果类型

- **入口/函数**: `_echo_quality_gate_summary(result)` 在 `fund_agent/ui/cli.py`
- **文件(行号)**: `fund_agent/ui/cli.py:1121`（`# type: ignore[no-untyped-def]`）
- **输入场景**: `analyze` 和 `checklist` 命令都调用该函数输出 quality gate 摘要
- **实际分支**: 函数通过鸭子类型访问 `result.quality_gate_result` 和 `result.quality_gate_not_run_reason`
- **预期行为**: `FundAnalysisResult` 和 `FundChecklistResult` 应通过共享 Protocol 或基类声明 quality gate 字段
- **实际行为**: 两个结果类型各自独立声明相同字段，函数用 `# type: ignore` 绕过类型检查
- **直接证据**: `cli.py:1121` 的 `# type: ignore[no-untyped-def]`；`FundAnalysisResult` 和 `FundChecklistResult` 各自包含 `quality_gate_result` 和 `quality_gate_not_run_reason`
- **影响**: 仅 maintainability；运行时 correctness 无问题（测试已覆盖）
- **建议改法和验证点**: 提取 `_HasQualityGateInfo` Protocol，让两个结果类型显式实现；移除 `# type: ignore`
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

无。

## Residual Risk

- CI 覆盖率门槛设为 50%（`--cov-fail-under=50`），这是较低的基线。未来应逐步提升至 AGENTS.md 要求的 80% 单文件覆盖率目标。当前不阻断本 PR。
- 20+ 被删除的过期文档（`docs/20260430/`、`docs/fund-agent-mvp-plan.md` 等）是合理的文档清理，但未在 PR description 中说明删除原因。不影响 correctness。

## PR Gate Recommendation

**PASS** — 建议合入。三项 finding 均为低严重程度的 docstring/doc 术语残留，可在后续 cleanup commit 中修复，不阻断本 PR。
