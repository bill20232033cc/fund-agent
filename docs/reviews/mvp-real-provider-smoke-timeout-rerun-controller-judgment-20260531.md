# MVP real provider smoke timeout rerun controller judgment

日期：2026-05-31

Gate：`MVP real provider smoke acceptance rerun / provider runtime timeout hardening gate`

角色：Phaseflow controller。本文记录 timeout rerun 裁决，不实现代码，不 push、不创建或更新 PR、不 merge、不 release。

## Judgment

结论：`timeout_reproduced`

分类：`provider_runtime / timeout`

底层 stop reason：`llm_timeout`

`006597 / 2024 --use-llm` 真实 provider rerun 仍未通过完整 0-7 章 acceptance，且没有 deterministic fallback。timeout 位置与上一轮不同，说明当前 blocker 是 provider runtime / request duration / bounded retry policy，而不是单一章节事实缺口或 provider auth/config。

## Evidence

- CLI stdout：`reports/mvp-local-acceptance/20260531-provider-timeout-rerun/real-provider-rerun.stdout`
- CLI stderr：`reports/mvp-local-acceptance/20260531-provider-timeout-rerun/real-provider-rerun.stderr`
- Service diagnostic：`reports/mvp-local-acceptance/20260531-provider-timeout-rerun/real-provider-rerun-diagnostic.json`

CLI rerun：

- Command：`uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- Exit code：`1`
- stdout：empty
- deterministic fallback：absent
- stderr：final assembly incomplete

Service diagnostic summary：

- `orchestration_status=blocked`
- `final_assembly_status=incomplete`
- Chapter 1：`status=failed`，`stop_reason=llm_timeout`，`attempts=2`
  - attempt 0 writer drafted, audit failed, repair decision `regenerate`
  - attempt 1 writer drafted, final run failed `llm_timeout`
- Chapters 2-6：`status=skipped`，`stop_reason=dependency_missing`

Comparison to previous Gate B evidence：

- Previous diagnostic: chapter 1 accepted; chapter 2 failed `llm_timeout`; chapters 3-6 dependency skipped.
- Current rerun: chapter 1 failed `llm_timeout` during regenerate path; chapters 2-6 dependency skipped.

Interpretation：timeout is reproducible and position-variable under real provider. It should be addressed as provider runtime timeout hardening, not as missing provider config, not as deterministic fallback, and not by relaxing writer/auditor safety rules.

## Next Smallest Entry

Start a `MVP provider runtime timeout hardening plan gate`.

Plan must cover:

- bounded retry/backoff for provider timeout only;
- timeout budget / env config strategy without logging secrets;
- per-request runtime diagnostics with no prompt/full draft/provider response leakage;
- preservation of max repair attempts and no infinite retry;
- no deterministic fallback;
- default deterministic `analyze/checklist` unchanged;
- real provider smoke acceptance rerun for `006597 / 2024 --use-llm`.

## Self-check

- No code changed by this judgment.
- No API key, Authorization header, full provider response or full writer draft recorded.
- No golden / fixtures / score / quality gate changed.
- No PR state changed.
