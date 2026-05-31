# MVP Real Provider Smoke Independent Body Matrix Evidence Review (GLM)

## Gate / Role

- Gate: `MVP real provider smoke acceptance rerun with independent body chapter matrix`
- Role: Gateflow review worker (GLM), evidence review only.
- Date: 2026-05-31.
- Branch: `codex/local-reconciliation`.
- Scope: review only; no code change, no real provider run, no push, no PR state change.

## Evidence Under Review

- Evidence doc: `docs/reviews/mvp-real-provider-smoke-independent-body-matrix-evidence-20260531.md`
- CLI raw: `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/real-provider-cli.{stdout,stderr,exit}`
- Service diagnostic: `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/service-diagnostic.json`
- Baseline docs: `docs/current-startup-packet.md`, `docs/implementation-control.md`, controller judgment `docs/reviews/mvp-independent-body-chapter-execution-controller-judgment-20260531.md`

## Verdict: PASS

Evidence 准确反映了真实 provider smoke rerun 结果，independent body chapter matrix 已验证，blocker 分类正确，无 secret 泄漏。Gate B smoke acceptance 仍为 blocked（无完整 0-7 报告），但 evidence 本身作为诊断产物通过 review。

## Criterion-by-Criterion Findings

### 1. 真实 provider CLI smoke exit 1、stdout empty、无 deterministic fallback

**PASS。**

- `real-provider-cli.exit` 内容为 `exit_code=1`，与 evidence 文档声称一致。
- `real-provider-cli.stdout` 为 0 字节空文件，与 evidence 文档声称的 `stdout bytes: 0` 一致。
- `real-provider-cli.stderr` 包含 `orchestration_status=partial`、`final_assembly_status=incomplete`，与 evidence 表格一致。
- `service-diagnostic.json` 中 `deterministic_fallback_observed: false`，确认无 deterministic fallback。
- `report_markdown_present: false`，确认无最终报告输出。

### 2. Chapters 1-6 独立执行，generated=[1..6]、skipped=[]，不再 synthetic dependency_missing

**PASS。**

- `service-diagnostic.json` 第 9-16 行：`generated_chapter_ids: [1, 2, 3, 4, 5, 6]`。
- 第 17 行：`skipped_chapter_ids: []`。
- `chapter_summary_matrix`（第 21-105 行）包含全部 6 个 chapter 独立行，每行有各自的 `status`/`stop_reason`/`failure_category`/`failure_subcategory`。
- CLI stderr 的 `chapter_matrix` 也包含 6 个独立条目，无 `dependency_missing`。
- 全文搜索确认无任何 `dependency_missing` 出现在 evidence 或原始文件中。

**独立执行已验证：chapter 1 writer timeout 不再导致 chapter 2-6 被跳过。**

### 3. Blocker 分类 provider_runtime_timeout 由直接 runtime diagnostic 支撑

**PASS。**

- `chapter_runtime_matrix` 中所有失败 chapter 的每个 provider attempt 均为：
  - `error_type: "ReadTimeout"`（service-diagnostic.json 第 153、173、199、218、253、269、312、328、362、378 行）
  - `provider_runtime_category: "timeout"`
  - `elapsed_ms` 在 60003-60087ms 范围，全部命中 60s 超时边界
  - `status_code: null`、`finish_reason: null`、`response_chars: null`：provider 未返回任何 HTTP 响应
- 无 `llm_rate_limited`、`llm_malformed_response`、`llm_network_error`、`audit_rule_too_strict` 或 `repair_budget_exhausted` 分类。
- Evidence 文档的 blocker classification 为 `provider_runtime_timeout`，完全由 runtime diagnostic 数据支撑。

### 4. 是否存在应判 code_bug / prompt_contract / audit_parse / fact_gap 的证据

**未发现。**

- 所有 `failure_category` 值为 `llm_timeout` 或 `null`（accepted chapter）。
- Chapter 4 在 service diagnostic 中 `status: "accepted"`、`stop_reason: "none"`、`write_statuses: ["drafted"]`、`audit_statuses: ["accepted"]`，证明 write-audit 管线端到端可成功。
- 无 `missing_required_structure`、`missing_required_output_marker`、`audit_parse` 失败、`candidate_facet_assertion` 或任何 prompt contract 相关分类。
- 无 `programmatic_audit`、`L1`、`C2` 或其他数值闭合失败。

**结论：当前 blocker 确为纯 runtime timeout，不存在被掩盖的 code_bug/prompt_contract/audit_parse/fact_gap。**

### 5. Final assembly 是否 fail-closed

**PASS。**

- `final_assembly_status: "incomplete"`。
- `accepted_chapter_ids: [4]`：仅 chapter 4 被接受。
- `final_assembly_issue_summary`（第 463-589 行）列出 16 个 blocking issue，覆盖 chapters 1/2/3/5/6 的 `chapter_not_accepted`、`missing_accepted_draft`、`missing_accepted_conclusion`。
- 无任何 blocking issue 针对 chapter 4（因为已 accepted）。
- `report_markdown_present: false` 确认 partial matrix 未被渲染为最终报告。

**Final assembly 正确 fail-closed：仅 1/6 body chapters accepted，不满足完整报告条件。**

### 6. Artifact 是否泄漏 secret 或 raw payload

**PASS。**

- `rg` secret pattern scan 对 `reports/mvp-real-provider-smoke-rerun/20260531-independent-body-matrix/` 和 evidence 文档返回 exit 1（无匹配）。
- `service-diagnostic.json` 中所有 failed attempt 的 `response_chars`、`request_id`、`finish_reason` 均为 `null`。
- 所有 prompt 相关字段仅为字符计数（`system_prompt_chars`、`user_prompt_chars`、`approx_prompt_tokens`），不含实际 prompt 内容。
- 无 `model_name`、`message`、API key、Authorization header。
- CLI stderr 仅包含 safe summary 格式。

### 7. Next smallest entry 是否合理

**PASS。**

Evidence 推荐 `MVP provider runtime budget and prompt-cost calibration gate`。理由充分：

- Chapter 2 writer `user_prompt_chars=104256`（~26086 tokens）、chapter 6 writer `user_prompt_chars=116223`（~29078 tokens），远超 chapter 3/5 auditor 的 ~1000 tokens。
- 极大 prompt 在 60s timeout 下几乎不可能完成，这是直接 runtime-cost 证据。
- Chapter 3/5 auditor prompt 仅 ~1000 tokens 也 timeout，说明 60s timeout 对当前 provider 本身可能偏紧。
- Chapter 4 端到端成功证明管线逻辑正确，下一步应聚焦 runtime budget 而非逻辑修复。
- 不 revisit provider config/auth、不放松 audit/ITEM_RULE/candidate facet 边界，scope 合理。

## Non-Blocking Observations

### N-1: CLI 与 service diagnostic 为两次独立 live-provider 运行，chapter 结果不同

- CLI run（~14:39）：chapters 1-2 accepted，chapters 3-6 failed（writer/auditor timeout）。
- Service diagnostic（~14:57）：chapter 4 accepted，chapters 1-3/5-6 failed。
- Evidence 文档第 89 行正确注释："the CLI smoke and service diagnostic are separate live-provider runs and may differ by chapter outcome"。
- 这是 expected behavior：真实 LLM provider 非确定性，且每次运行的 prompt 规模不同（service diagnostic 是独立 Python 调用，非 CLI 子进程）。
- **影响**：无。两次运行均证明独立 body chapter 执行，且均 fail-closed。

### N-2: Chapter 2/6 writer prompt 极大值得专项调查

- `user_prompt_chars` 分别为 104256 和 116223（~26k/29k tokens by heuristic）。
- 对比 chapter 1 writer 仅 8719 chars（~2202 tokens），差距超 10x。
- 可能原因：chapter 2/6 的 `ChapterFactProjection` 包含大量 structured data（如完整持仓列表、交易明细）。
- **建议**：在 next gate 中调查 prompt 构造逻辑，确认是否存在不必要的全量数据序列化。

### N-3: 60s per-attempt timeout 对 auditor 也偏紧

- Chapter 3 auditor prompt 仅 ~1047 tokens 也在 60s 内 timeout（两次 attempt 均为 ReadTimeout）。
- 说明 timeout 不仅仅是大 prompt 的问题，当前 provider/endpoint 本身响应延迟可能较高。
- **建议**：next gate 可同时考虑 per-chapter timeout 策略（小 prompt 用短 timeout，大 prompt 用长 timeout）或 provider-level 优化。

### N-4: Evidence 文档 CLI section 的 first_failed_chapter_id 与 service diagnostic first_failed 不同

- CLI stderr: `first_failed_chapter_id=3`（因为 CLI run 中 ch1-2 accepted）。
- Service diagnostic `first_failed`: `chapter_id=1`（因为 diagnostic run 中 ch1 failed）。
- Evidence 文档 CLI section 使用 CLI 数据，per-chapter matrix 使用 service diagnostic 数据，各节内部一致。
- **影响**：无。只要读者理解这是两次独立运行。

## Residual Risks

| Risk | Severity | Mitigation |
|---|---|---|
| 真实 provider 响应延迟波动大，未来 smoke rerun 可能再次出现不同 chapter outcome | low | 已有 independent body matrix，单次 rerun 结果不影响管线正确性判断 |
| Chapter 2/6 prompt 大小可能导致即使增加 timeout 也无法在合理时间内完成 | medium | Next gate 应调查 prompt 构造是否有压缩空间 |
| 60s timeout 对所有 chapter 统一配置，未按 prompt 规模适配 | low | Next gate 可引入 per-chapter 或 per-operation timeout 策略 |
| Gate B smoke acceptance 仍 blocked，无完整 0-7 报告 | high (gate-level) | 非 evidence review 问题；next gate 应解决 runtime budget |

## Summary

Evidence 准确、完整、安全。独立 body chapter matrix 已被真实 provider smoke 验证：chapters 1-6 全部独立执行，无 synthetic `dependency_missing`。Blocker 为 `provider_runtime_timeout`，由 `ReadTimeout` diagnostic 直接支撑。Chapter 4 端到端成功证明 write-audit 管线逻辑正确。Final assembly 正确 fail-closed。无 secret/raw payload 泄漏。Next entry `MVP provider runtime budget and prompt-cost calibration gate` 合理，应聚焦 chapter 2/6 极大 prompt 和统一 timeout 策略。
