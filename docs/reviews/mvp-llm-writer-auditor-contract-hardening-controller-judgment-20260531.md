# MVP LLM writer/auditor contract hardening controller judgment

日期：2026-05-31

Phase：`MVP real-provider stabilization and score-loop phase`

Gate：`MVP LLM writer/auditor contract hardening gate`

角色：Phaseflow controller。本文记录本地 gate 裁决，不 push、不创建或更新 PR、不 merge、不 release。

## Judgment

结论：`local_accepted_with_next_gate_timeout_blocker`

Gate A 目标已达成：writer/auditor 输出协议已经更可控，真实 provider 下的剩余失败能够稳定分类到 `llm_timeout`，且没有 deterministic fallback。完整 0-7 章真实 provider acceptance 尚未通过，归属下一 gate `MVP real provider smoke acceptance gate`。

## Evidence

- Plan：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`
- Plan judgment：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-controller-judgment-20260531.md`
- Implementation evidence：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-implementation-evidence-20260531.md`
- MiMo code review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-review-mimo-20260531.md`
- GLM code review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-review-glm-20260531.md`
- MiMo re-review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-rereview-mimo-20260531.md`
- GLM re-review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-code-rereview-glm-20260531.md`
- Controller real-provider evidence：
  - `reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024.stderr`
  - `reports/mvp-local-acceptance/20260531-writer-auditor-contract-hardening/real-provider-006597-2024-diagnostic.json`

## Validation

- `uv run ruff check .`：PASS。
- `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_provider.py tests/ui/test_cli.py -q`：PASS，`155 passed`。
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`：PASS，`1127 passed`，coverage `91.77%`。
- Missing-config `--use-llm` smoke：PASS fail-closed，exit code `1`，stdout empty，无 deterministic fallback。
- Real provider CLI smoke `006597 / 2024 --use-llm`：exit code `1`，stdout empty，无 deterministic fallback；CLI stderr 仍是 final assembly 聚合错误。
- Real provider Service diagnostic：`orchestration_status=partial`，`final_assembly_status=incomplete`；chapter 1 `accepted`，chapter 2 `failed stop_reason=llm_timeout`，chapters 3-6 `skipped stop_reason=dependency_missing`。
- Secret leak check：本次 Gate A artifacts / reports 未记录真实 API key、Authorization header value、完整 provider response 或完整 writer draft；命中项均为安全说明、测试 fake secret、变量名或代码常量。

## Findings Judgment

Blocking findings：无。

Info residuals accepted：

- Candidate facet 否定句可能被 regex 保守误杀：当前 writer 推荐 disclaimer 已规避；误杀优于 asserted candidate facet 漏放。
- Provider runtime stop reason 使用 exception type name 字符串匹配：当前无子类化，fallback 仍 fail-closed；后续可考虑 category 属性。
- `_sanitize_text` 对 `prompt` 词过度脱敏：安全方向正确，可能降低 message 可读性但不影响本 gate。
- CLI incomplete message 仍聚合 final assembly issue，章节级 stop reason 需 Service diagnostic 才能看到：Gate A 接受为本地 evidence 能分类；若 Gate B 要 CLI 直接显示分类，可作为后续最小修复入口。

## Next Gate Entry

进入 `MVP real provider smoke acceptance gate` 时，当前直接证据为：

- `006597 / 2024` 未达到完整 0-7 章 acceptance。
- 已接受 chapter 1，说明 writer/auditor contract hardening 对真实模型生效。
- 当前 blocker 是 chapter 2 provider runtime timeout：分类 `provider_runtime / timeout`，底层 stop reason `llm_timeout`。

下一最小入口：

1. 先做 Gate B rerun，确认 `llm_timeout` 是否偶发。
2. 若连续复现，最小修复入口是 provider timeout/retry/budget policy 或 chapter 2 prompt/runtime cost diagnostic，不是 provider auth/config，也不是放松 writer/auditor 审计。

## Self-check

- 未修改 PR 状态、未 push、未 merge、未 release。
- 未进入 Gate 5 dayu/Host/Agent。
- 未修改 golden / fixtures / score / quality gate。
- 默认 deterministic analyze/checklist 行为保持不变。
