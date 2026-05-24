# Release Maintenance Audit Rule Taxonomy Clarification

> Date: 2026-05-24
> Branch: `codex/audit-taxonomy-clarification`
> Work unit: document-only audit rule taxonomy clarification
> Result: accepted locally

## Scope

本次只关闭仓库级 residual：`Audit rule code taxonomy clarification`。

目标是把三类规则口径分清：

- 报告级三层审计目标：P/C/L/R/E 规则码。
- 当前 MVP 程序审计：`P1/P2/P3/C2/L1/R1/R2`，由 `run_programmatic_audit()` 执行。
- 字段质量门控：`FQ0-FQ6`，由 quality gate 消费 `score.json` 执行。

## Current-State Evidence

- `fund_agent/fund/audit/audit_programmatic.py` 的 `AuditRuleCode` 和 `_CHECKED_RULES` 只包含 `P1/P2/P3/C2/L1/R1/R2`。
- `docs/design.md` 第 5.2 节已列出完整三层目标，其中 `E1/E2/E3/C1/L2` 标为 v2。
- `fund_agent/fund/README.md` 已在 `run_programmatic_audit()` 小节说明 C2 的确定性边界，并声明 E1/E2/E3 后续审计。
- `README.md` 原“当前能力”摘要漏写 `C2`，会让 reviewer 误判当前程序审计缺少已实现规则。

## Changes

- `README.md` 当前能力摘要补齐 `C2`。
- `docs/design.md` 第 5.2 节新增规则码口径说明，明确 P/C/L/R/E 与 FQ0-FQ6 不是同一 taxonomy。
- `fund_agent/fund/README.md` 明确当前程序审计只覆盖 `P1/P2/P3/C2/L1/R1/R2`，完整三层目标中的 `E1/E2/E3/C1/L2` 属于后续 LLM 审计 / Evidence Confirm / 语义复核层。
- `fund_agent/fund/README.md` 模块导读补齐 `contract_rules.py` 和 `C2`。

## Non-Goals

- 不修改 source code、tests、quality gate 规则或程序审计规则码。
- 不实现 LLM 审计、Evidence Confirm、E1/E2/E3/C1/L2 或修复闭环。
- 不改变 `ProgrammaticAuditResult.checked_rules`。
- 不改变 Host/Agent 边界、Dayu dependency gate、`extra_payload` 纪律或 004393/2024 quality gate 调查。

## Validation

- `rg -n "程序审计规则：P1/P2/P3/C2/L1/R1/R2|规则码口径|完整三层审计目标仍包含 E1/E2/E3、C1 和 L2|audit_programmatic.py.*contract_rules.py" README.md docs/design.md fund_agent/fund/README.md`
- `git diff --check`

Both checks passed. Full test suite was not run because no code, config, runtime behavior, or tests changed.
