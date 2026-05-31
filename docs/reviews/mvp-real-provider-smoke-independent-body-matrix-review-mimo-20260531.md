# MVP Real Provider Smoke Independent Body Matrix Review — MiMo

## Gate / Role

- Gate: `MVP real provider smoke acceptance rerun with independent body chapter matrix`
- Role: Gateflow review worker (MiMo)，evidence review only.
- Date: 2026-05-31.
- Branch: `codex/local-reconciliation`.
- Scope: evidence review；不改代码、不运行真实 provider、不 push、不改 PR 状态。

## Verdict

**PASS**

Gate evidence 满足全部 7 项 review criteria。Gate 本身 blocked（非 acceptance），但 evidence 证明了 independent body chapter matrix 行为正确、fail-closed 安全、blocker 分类精确。

## Review Criteria 逐项裁决

### 1. 真实 provider CLI smoke exit 1、stdout empty、无 deterministic fallback

**PASS**

| 证据源 | 值 | 结论 |
|---|---|---|
| `real-provider-cli.exit` | `exit_code=1` | exit 1 ✅ |
| `real-provider-cli.stdout` | empty (文件存在但无内容) | stdout empty ✅ |
| `real-provider-cli.stderr` | `orchestration_status=partial, final_assembly_status=incomplete` | 无 deterministic fallback ✅ |
| `service-diagnostic.json` | `deterministic_fallback_observed: false` | 确认无 fallback ✅ |

真实 CLI 命令 `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` 到达了真实 provider，未回退到 deterministic 模式。

### 2. Chapters 1-6 独立执行，generated=[1..6]、skipped=[]，不再 synthetic dependency_missing

**PASS**

| 证据源 | 值 | 结论 |
|---|---|---|
| `service-diagnostic.json` `generated_chapter_ids` | `[1, 2, 3, 4, 5, 6]` | 全部 6 章生成 ✅ |
| `service-diagnostic.json` `skipped_chapter_ids` | `[]` | 无跳过 ✅ |
| `service-diagnostic.json` `chapter_summary_matrix` | 6 行，每行独立 `status/stop_reason/failure_category` | 独立执行 ✅ |
| `real-provider-cli.stderr` `chapter_matrix` | `1:accepted/…;2:accepted/…;3:failed/…;4:…;5:…;6:…` | 无 `dependency_missing` ✅ |
| 前 gate judgment (`mvp-independent-body-chapter-execution-controller-judgment`) | `dependency_missing` only used for true dependency | 代码层已修复 ✅ |

对比前一 gate（`mvp-real-provider-smoke-acceptance-controller-judgment-20260531`）中 `Chapters 3-6: status=skipped, stop_reason=dependency_missing`，本次 rerun 已消除 synthetic skip。Chapters 2-6 不再因 chapter 1 失败而被标记 `dependency_missing`。

### 3. Blocker 分类 provider_runtime_timeout 由直接 runtime diagnostic 支撑

**PASS**

`service-diagnostic.json` `runtime_diagnostics.chapter_runtime_matrix` 为每个 failed chapter 提供了直接 runtime 证据：

| Chapter | error_type | provider_runtime_category | elapsed_ms (max) | provider attempts |
|---|---|---|---:|---|
| 1 | `ReadTimeout` | `timeout` | 60081 | writer 2/2 |
| 2 | `ReadTimeout` | `timeout` | 60080 | writer 2/2 |
| 3 | `ReadTimeout` | `timeout` | 60060 | auditor 2/2 |
| 5 | `ReadTimeout` | `timeout` | 60030 | auditor 2/2 |
| 6 | `ReadTimeout` | `timeout` | 60087 | writer 2/2 |

- 每个 failed chapter 均有 `error_type=ReadTimeout`，`provider_runtime_category=timeout`。
- 所有 elapsed_ms 均在 60s 附近，与 provider timeout 阈值一致。
- Chapter 4 accepted，无 runtime diagnostic（正确行为）。
- blocker 分类 `provider_runtime_timeout` 有直接 runtime 证据支撑，非推断。

### 4. 无应判 code_bug/prompt_contract/audit_parse/fact_gap 的证据

**PASS**

- 所有 failed chapter 的 `failure_category=llm_timeout`，`stop_reason=llm_timeout`。
- `service-diagnostic.json` `prompt_contract_diagnostics.chapter_phase_matrix` 中所有 chapter 的 `phases: []`，无 prompt_contract 阶段失败记录。
- Chapter 4 accepted 证明 writer→auditor 链路在正常 provider 响应下可正常工作。
- `ReadTimeout` 是 provider 侧响应超时，不是代码逻辑错误、prompt 契约违反、审计解析失败或事实缺口。
- `attempt_count=0` for chapters 1/2/6 表示 writer 超时在 `ChapterAttemptRecord` 创建之前，这是 writer primitive 的 timeout handling 行为，非 code_bug。

### 5. Final assembly fail-closed

**PASS**

| 证据源 | 值 | 结论 |
|---|---|---|
| `service-diagnostic.json` `final_assembly_status` | `incomplete` | 未组装完整报告 ✅ |
| `service-diagnostic.json` `report_markdown_present` | `false` | 无报告输出 ✅ |
| `service-diagnostic.json` `accepted_chapter_ids` | `[4]` | 仅 1/6 章 accepted ✅ |
| `service-diagnostic.json` `final_assembly_issue_summary` | 16 blocking issues | 每个未 accepted chapter 产生 `not_accepted/missing_accepted_draft/missing_accepted_conclusion` ✅ |
| `real-provider-cli.exit` | `exit_code=1` | CLI 非零退出 ✅ |
| `real-provider-cli.stdout` | empty | 无报告写入 stdout ✅ |

Final assembly 在 `orchestration_status=partial` 时拒绝组装，正确 fail-closed。

### 6. Artifact 是否泄漏 secret 或 raw payload

**PASS**

- Secret scan `rg` 命令在 `reports/…/` 下无匹配（EXIT=1）。
- `service-diagnostic.json` 仅含 chapter metadata（id/status/category/elapsed_ms/prompt_chars/token counts），不含 API key、Authorization header、完整 prompt、draft markdown 或 provider response。
- `real-provider-cli.stderr` 仅含 compact safe summary（orchestration_status/chapter_matrix），不含 raw payload。
- `service-diagnostic.stdout` 和 `service-diagnostic.stderr` 均为空。
- `deterministic-analyze.stdout` 包含完整报告内容，但这是 deterministic 模式（非 LLM），不含 provider response。

### 7. Next smallest entry 是否合理

**PASS**

Evidence document 建议：`MVP provider runtime budget and prompt-cost calibration gate`

合理性分析：

- 不重访 provider config/auth（已由前 gate 验证）：合理。
- 不放松 evidence/ITEM_RULE/candidate facet/transaction advice/E2 deferred/audit safety：合理。
- 聚焦 prompt cost reduction（chapters 2/6 的 104K/116K user_prompt_chars）和 per-chapter runtime budget：直接对应 timeout 根因。
- 保留 final assembly fail-closed：安全。

## Residual Risks

### R1: CLI stderr `first_failed_chapter_id` 与 chapter matrix 对齐问题（信息级）

CLI stderr 显示 `first_failed_chapter_id=3`，但 chapter matrix 中 chapters 1-2 显示 `status=accepted`。在 sequential 执行下，`first_failed_chapter_id=3` 表示 chapters 1-2 先完成（accepted），chapter 3 首次失败——这与 matrix 一致。但 `first_failed_runtime_operation=auditor` 仅反映 chapter 3 的失败阶段，不反映其他 chapter 的失败阶段。非 blocking，但后续 diagnostic 可考虑区分 "first_failed" vs "first_rejected" 语义。

### R2: Extreme writer prompt sizes for chapters 2 and 6（关键 residual）

Chapters 2 和 6 的 `user_prompt_chars` 分别为 104,256 和 116,223（approx tokens ~26K/~29K），远超其他 chapter。这些 prompt 包含完整年报提取数据作为 context。在 60s provider timeout 下，大 prompt + 长输出需求几乎必然超时。这是下一 gate 的主要优化目标。

### R3: Chapter 1 prompt 小但 writer 超时（低风险）

Chapter 1 的 `user_prompt_chars=8,719`（approx tokens ~2.2K）相对较小，但仍 writer timeout。两次 attempt 均在 ~60s 处 `ReadTimeout`。可能原因：provider 侧冷启动、排队延迟、或网络抖动。低风险，但在 runtime budget calibration 中应考虑 per-chapter timeout 弹性。

### R4: Two separate live-provider runs produce different chapter outcomes（信息级）

CLI smoke 和 service diagnostic 是两次独立的 live-provider run，chapter outcomes 不同（CLI: ch1-2 accepted, ch3-6 failed; Diagnostic: ch4 accepted, ch1-3/5-6 failed）。这是真实 provider 的正常行为变异，非 evidence 问题。后续 gate 应以单次 run 的 evidence 为准，不混用两次 run 的 chapter outcomes。

### R5: `attempt_count=0` for chapters 1/2/6 的 writer timeout 处理（低风险）

Chapters 1、2、6 的 `attempt_count=0` 表示 writer 在 `ChapterAttemptRecord` 创建之前就超时了。Runtime diagnostic 仍正确记录了 provider attempt 级别的 `ReadTimeout`，但 `attempt_count=0` 可能影响下游 score-loop 或 repair 逻辑的计数。低风险，后续可审计。

## Findings Summary

| # | Severity | Location | Finding |
|---|---|---|---|
| F1 | INFO | `real-provider-cli.stderr` | `first_failed_chapter_id=3` 语义精确但仅反映第一个 failed chapter 的 auditor 阶段，不反映 chapters 1-2 已 accepted 的全局状态 |
| F2 | RESIDUAL | `service-diagnostic.json` chapters 2/6 | `user_prompt_chars` 104K/116K 导致 writer timeout 几乎必然，需 prompt cost calibration |
| F3 | INFO | `service-diagnostic.json` chapter 1 | 小 prompt（8.7K chars）仍 writer timeout，可能为 provider 侧偶发延迟 |
| F4 | INFO | CLI vs diagnostic | 两次独立 run 的 chapter outcomes 不同，属正常 provider 行为变异 |
| F5 | INFO | `service-diagnostic.json` chapters 1/2/6 | `attempt_count=0` 但 runtime diagnostic 有记录，下游 score-loop 应兼容此模式 |

无 blocking finding。

## Self-check

- 未修改代码、未运行 provider、未 push、未改 PR 状态。
- 未记录或输出 API key、Authorization header、完整 prompt、draft markdown 或 raw provider response。
- 未修改 golden/fixtures/score/quality gate。
- 未把弱证据或缺证据包装成通过。
