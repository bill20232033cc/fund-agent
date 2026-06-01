# MVP real provider smoke acceptance controller judgment

日期：2026-05-31

Phase：`MVP real-provider stabilization and score-loop phase`

Gate：`MVP real provider smoke acceptance gate`

角色：Phaseflow controller。本文记录真实 provider smoke acceptance 裁决，不 push、不创建或更新 PR、不 merge、不 release。

## Judgment

结论：`blocked`

分类：`provider_runtime / timeout`

底层 stop reason：`llm_timeout`

`fund-analysis analyze 006597 --report-year 2024 --use-llm` 未达到 Gate B acceptance：未输出完整 0-7 章，也未形成全部章节审计状态。命令 fail-closed，stdout empty，没有 deterministic fallback。

## Evidence

- CLI stdout：`reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024.stdout`
- CLI stderr：`reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024.stderr`
- Service diagnostic：`reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024-diagnostic.json`

CLI smoke：

- Command：`uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- Exit code：`1`
- stdout：empty
- stderr：`LLM 分析未完成`，final assembly 聚合 issues 为 `chapter_not_accepted / missing_accepted_draft / missing_accepted_conclusion`
- deterministic fallback：absent

Service diagnostic summary：

- `orchestration_status=partial`
- `final_assembly_status=incomplete`
- Chapter 1：`status=accepted`，`stop_reason=none`，audit accepted
- Chapter 2：`status=failed`，`stop_reason=llm_timeout`
- Chapters 3-6：`status=skipped`，`stop_reason=dependency_missing`

## Acceptance Check

- 输出完整 0-7 章：FAIL
- 证据锚点：not accepted as full report
- 章节审计状态：partial；chapter 1 accepted，chapter 2 timeout，chapter 3-6 skipped
- 无 deterministic fallback：PASS
- 失败分类精确：PASS，`provider_runtime / timeout`，stop reason `llm_timeout`
- 不归因为 provider config：PASS；provider/auth 已由上一 gate 验证，当前真实 run 到达 provider runtime timeout

## Controller Decision

Gate B 不通过，但 blocker 已满足可修复分类要求。当前不应回退到 provider/auth 配置排查，也不应放松 writer/auditor 审计规则。

下一最小入口：

1. Rerun Gate B smoke 一次，判断 timeout 是否偶发。
2. 若连续复现，进入最小 provider runtime timeout hardening：增大 `FUND_AGENT_LLM_TIMEOUT_SECONDS`、引入 bounded retry/backoff、或降低单章 provider request runtime cost。
3. 若 timeout 消失后出现新分类，再按新分类进入下一最小 gate：`prompt_contract`、`audit_parse`、`fact_gap`、`code_bug` 或 `unknown`。

## Gate C Eligibility

尽管 Gate B blocked，Gate C 可继续作为 design-only gate 推进，因为用户指定 Gate B blocked 时 Gate C 可只做 design，并必须保留 blocked reason 和下一最小入口。本 judgment 即为 Gate C 的前置 blocker 输入。

## Self-check

- 未修改 PR 状态、未 push、未 merge、未 release。
- 未记录 API key、Authorization header、完整 provider response 或完整 writer draft。
- 未修改 golden / fixtures / score / quality gate。
- 未把弱证据或缺证据包装成通过。
