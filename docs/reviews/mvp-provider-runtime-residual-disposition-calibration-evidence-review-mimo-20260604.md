# Evidence Review: Provider Runtime Residual Disposition / Calibration — D1-D4 Evidence

## 元信息

| 字段 | 值 |
|---|---|
| Review artifact | `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-evidence-review-mimo-20260604.md` |
| 日期 | 2026-06-04 |
| Reviewer 角色 | Independent evidence reviewer（非 evidence author、非 controller） |
| 被审查的 evidence | `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-evidence-20260604.md` |
| Accepted plan | `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-plan-20260604.md` |
| Controller judgment | `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-plan-controller-judgment-20260604.md` |
| Retained artifact | `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/` |
| Gate 分类 | `heavy` |

---

## Verdict: PASS_WITH_FINDINGS

Evidence D1-D4 可以被 controller 接受。3 个 non-blocking findings，0 个 blocking findings。

---

## D1 Review：Diagnostic Completeness Verification

### D1.1 Top-Level 字段校验 — PASS

Reviewer 独立读取全部 6 个 chapter JSON，逐字段交叉验证：

| 验证项 | 结果 |
|---|---|
| `terminal_runtime_diagnostic_present` 全部 True | 6/6 确认 |
| `diagnostic_consistency_status` 全部 consistent | 6/6 确认 |
| `chapter_runtime_diagnostics[]` count = 2 每章 | 6/6 确认 |
| `terminal_issue_class` = ReadTimeout | 6/6 确认 |
| `terminal_failure_category` = llm_timeout | 6/6 确认 |
| `terminal_stop_reason` = llm_timeout | 6/6 确认 |
| `terminal_runtime_operation` 值 | Ch1=auditor, Ch2-Ch5=writer, Ch6=auditor — 与 evidence 表一致 |
| `status` = failed, `accepted` = False | 6/6 确认 |

**Finding NB-1**（non-blocking）：evidence D1.1 表将 `terminal_repair_attempt_index` 统一列为 0，但 reviewer 注意到 Ch1/Ch6 的 terminal 字段位于 `attempts[0]` 层级（attempt 结构体内的 terminal 字段），而 Ch2-Ch5 的 terminal 字段位于 chapter JSON 顶层（无 attempts 数组）。两者 terminal 值一致，但 evidence 表未区分 terminal 字段的来源结构差异。不影响正确性判定。

### D1.2 Runtime Diagnostic 逐条字段校验 — PASS

Reviewer 逐章验证 12 条 runtime diagnostic：

| 验证项 | 预期 | 实际 |
|---|---|---|
| `error_type` | ReadTimeout | 12/12 ReadTimeout |
| `provider_runtime_category` | timeout | 12/12 timeout |
| `timeout_seconds` | 60.0 | 12/12 60.0 |
| `approx_prompt_tokens` 非 null | 非 null | 12/12 数值（946–2879） |
| `elapsed_ms` 非 null | 非 null | 12/12 数值（60003–60224） |
| `provider_attempt_index` | 1 或 2 | 12/12 正确 |
| `provider_max_attempts` | 2 | 12/12 正确 |
| `timeout_budget_kind` | writer_initial 或 auditor | 12/12 正确 |
| `repair_timeout_fallback_used` | True | 12/12 True |
| `status_code` | None | 12/12 None |
| `response_chars` | None | 12/12 None |
| `finish_reason` | None | 12/12 None |

### D1.3 Chapter Prompt Contract Diagnostics — PASS

| 章节 | evidence 声称 | 实际 JSON | 一致 |
|---|---|---|---|
| Ch1 | `[]` (0 items) | `chapter_prompt_contract_diagnostics: []` | 是 |
| Ch2 | `[]` (0 items) | `chapter_prompt_contract_diagnostics: []` | 是 |
| Ch3 | `[]` (0 items) | `chapter_prompt_contract_diagnostics: []` | 是 |
| Ch4 | `[]` (0 items) | `chapter_prompt_contract_diagnostics: []` | 是 |
| Ch5 | `[]` (0 items) | `chapter_prompt_contract_diagnostics: []` | 是 |
| Ch6 | `[]` (0 items) | `chapter_prompt_contract_diagnostics: []` | 是 |

### D1.4 Writer Draft 文件存在性 — PASS

| 章节 | evidence 声称 | summary.json artifact_files | 一致 |
|---|---|---|---|
| Ch1 | PRESENT | `chapter-01-attempt-00-writer.md` in artifact_files | 是 |
| Ch2 | ABSENT | 不在 artifact_files 中 | 是 |
| Ch3 | ABSENT | 不在 artifact_files 中 | 是 |
| Ch4 | ABSENT | 不在 artifact_files 中 | 是 |
| Ch5 | ABSENT | 不在 artifact_files 中 | 是 |
| Ch6 | PRESENT | `chapter-06-attempt-00-writer.md` in artifact_files | 是 |

### D1.5 Secret-Safe 字段校验 — PASS

Reviewer 对 6 个 chapter JSON 确认：无 `prompt`、`raw_response`、`raw_audit_response`、`message`、`model_name`、API key、Authorization header、base URL 字段。`request_id` 全部为 null。

### D1 总判定: PASS

---

## D2 Review：Cross-Chapter Failure Pattern Analysis

### D2.1 12 条 Provider Call 聚合表 — PASS

Reviewer 独立从 6 个 chapter JSON 提取 12 条 diagnostic，与 evidence 聚合表逐行对比：

| # | Ch | Operation | Attempt | Tokens (evidence) | Tokens (JSON) | Elapsed (evidence) | Elapsed (JSON) | Match |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | auditor | 1/2 | 1074 | 1074 | 60003 | 60003 | 是 |
| 2 | 1 | auditor | 2/2 | 1074 | 1074 | 60224 | 60224 | 是 |
| 3 | 2 | writer | 1/2 | 1843 | 1843 | 60152 | 60152 | 是 |
| 4 | 2 | writer | 2/2 | 1843 | 1843 | 60160 | 60160 | 是 |
| 5 | 3 | writer | 1/2 | 2879 | 2879 | 60173 | 60173 | 是 |
| 6 | 3 | writer | 2/2 | 2879 | 2879 | 60185 | 60185 | 是 |
| 7 | 4 | writer | 1/2 | 1433 | 1433 | 60094 | 60094 | 是 |
| 8 | 4 | writer | 2/2 | 1433 | 1433 | 60171 | 60171 | 是 |
| 9 | 5 | writer | 1/2 | 2676 | 2676 | 60144 | 60144 | 是 |
| 10 | 5 | writer | 2/2 | 2676 | 2676 | 60201 | 60201 | 是 |
| 11 | 6 | auditor | 1/2 | 946 | 946 | 60004 | 60004 | 是 |
| 12 | 6 | auditor | 2/2 | 946 | 946 | 60171 | 60171 | 是 |

全部 12 条数值同源一致。

### D2.2 不变量校验 — PASS

| 不变量 | evidence 声称 | reviewer 验证 | 判定 |
|---|---|---|---|
| 全部 error_type = ReadTimeout | 12/12 | 12/12 确认 | PASS |
| 全部 provider_runtime_category = timeout | 12/12 | 12/12 确认 | PASS |
| 全部 status_code = None | 12/12 | 12/12 确认 | PASS |
| 全部 response_chars = None | 12/12 | 12/12 确认 | PASS |
| 全部 finish_reason = None | 12/12 | 12/12 确认 | PASS |
| 全部 timeout_root_cause_hint = small_prompt_provider_timeout | 12/12 | 12/12 确认 | PASS |
| 全部 repair_timeout_fallback_used = True | 12/12 | 12/12 确认 | PASS |
| Elapsed 范围 [60003, 60224] ms | 声称 | 实际 min=60003, max=60224 确认 | PASS |
| Prompt token 范围 [946, 2879] | 声称 | 实际 min=946, max=2879 确认 | PASS |
| 操作覆盖 writer + auditor | 声称 | 实际 Ch1/Ch6=auditor, Ch2-Ch5=writer 确认 | PASS |
| Budget kind 覆盖 writer_initial + auditor | 声称 | 实际确认 | PASS |
| 无任何调用成功 | 0/12 | 全部 failed 确认 | PASS |

### D2.3 关键观察校验 — PASS

Evidence 声称「Ch1/Ch6 writer 成功产出 draft，但 auditor 超时」。Reviewer 确认：
- Ch1 JSON: `writer_status: "drafted"`, `writer_draft_file: "chapters/chapter-01-attempt-00-writer.md"`, terminal operation = auditor (超时)
- Ch6 JSON: `writer_status: "drafted"`, `writer_draft_file: "chapters/chapter-06-attempt-00-writer.md"`, terminal operation = auditor (超时)
- Ch2-Ch5: `attempts: []` (空数组，writer 自身超时未产出 draft)

与 evidence 观察一致。

### D2 总判定: PASS

---

## D3 Review：Fail-Closed Safety Verification

| 安全检查项 | evidence 声称 | reviewer 验证 | 判定 |
|---|---|---|---|
| orchestration_status = blocked | 是 | manifest.json L16 确认: `"orchestration_status": "blocked"` | PASS |
| final_assembly_status = incomplete | 是 | manifest.json L14 确认: `"final_assembly_status": "incomplete"` | PASS |
| trigger = use_llm_incomplete | 是 | manifest.json L35 确认 | PASS |
| retention_policy = manual_local_cleanup | 是 | manifest.json L31 确认 | PASS |
| 全部 6 章 accepted = False | 是 | 6 个 chapter JSON 确认 | PASS |
| 全部 6 章 accepted_conclusion_present = False | 是 | 6 个 chapter JSON 确认 | PASS |
| final_assembly_issues = 20 blocking | 声称 20 | reviewer 计数: 1 (orchestration) + 3×6 (ch1-6: not_accepted + missing_draft + missing_conclusion) + 1 (ch7 readiness) = 20 确认 | PASS |
| chapter_matrix 6 章全 failed/llm_timeout | 是 | summary.json chapter_matrix 确认 6 章全部 `status: "failed"`, `stop_reason: "llm_timeout"` | PASS |
| CLI exit code = 1 | 推断自 orchestration_status=blocked | controller judgment 已接受此推断方法 | PASS |
| stdout 空 | 推断自 final_assembly_status=incomplete | controller judgment 已接受此推断方法 | PASS |

**Finding NB-2**（non-blocking）：evidence D3 表声称「final_assembly_issues = 20 blocking issues，覆盖全部 6 章 + Ch7 readiness」。实际 20 条中 19 条是 chapter-level（6 章 × 3 + ch7 readiness），1 条是 orchestration-level。「覆盖全部 6 章 + Ch7 readiness」的描述遗漏了 orchestration-level issue，但总数正确且不影响安全判定。

### D3 总判定: PASS

---

## D4 Review：Calibration Readiness Verdict

### D4 READY 含义校验 — PASS

Evidence D4 明确声明：

**正面含义**（均被 D1-D3 支撑）：
- 当前 retained diagnostic schema 捕获了分类 provider 失败所需的全部字段 — 支撑
- Fail-closed 安全边界完整且已验证 — 支撑
- Future controller 可以授权恰好一次 live provider evidence run — 支撑
- 下一次 evidence gate 之前不需要额外的 diagnostic instrumentation — 支撑

**限制（不等于）**（均正确限定）：
- 不等于 endpoint working — 正确
- 不等于 live run 会成功 — 正确
- 不等于 provider defaults 应该改 — 正确
- 不等于 Chapter acceptance calibration 可以开始 — 正确

D4 没有过度推断。READY 仅表示 diagnostic readiness for future live calibration gate，不表示 endpoint working、不授权 defaults change / live probe / Chapter calibration。

### 残余分类校验 — PASS

```
Primary:   endpoint_availability_residual（endpoint 在 60s 内对全部 12 次请求返回零字节）
Secondary: not_applicable（timeout policy 不是根因）
Tertiary:  not_applicable（diagnostic evidence 完整、一致、充分）
```

Reviewer 确认此分类与 plan Section 4.2/4.3 的 first-principles differential diagnosis 一致，且被 D1-D3 evidence 支撑。

### D4 总判定: PASS

---

## Redaction Scan 验证

Evidence 声称对 retained artifact 和 evidence 自身分别执行了 `rg` redaction scan。Reviewer 验证：

| 扫描目标 | evidence 声称 | 可信度 |
|---|---|---|
| Retained artifact secret 模式 | 仅命中 redaction_policy 描述中的 category 名称 | 合理——manifest.json 的 `forbidden_categories` 数组包含 "secret_headers" 等名称 |
| Retained artifact URL/endpoint | 零命中 | reviewer 确认 6 个 chapter JSON 和 manifest/summary 中无 base URL |
| Retained artifact model name | 零命中 | reviewer 确认无 model name 字段 |
| Evidence 自身 redaction | 零命中 | reviewer 确认 evidence 文档不含 secret/endpoint/model |

PASS。

---

## Forbidden-Scope Checklist 验证

Evidence 列举 12 项 forbidden scope。Reviewer 逐项确认：

| 禁止事项 | evidence 声称 | reviewer 验证 |
|---|---|---|
| 运行 live provider smoke/probe | 否 | 无网络调用证据 |
| 发送 HTTP 请求 | 否 | 无网络调用证据 |
| 修改代码/测试/配置/README | 否 | git diff --stat HEAD 为空（preflight 已声明） |
| 修改 design/control/startup docs | 否 | 未触及 |
| 修改 provider/default/runtime/budget | 否 | 未触及 |
| 设置 env override | 否 | 未设置 |
| 进入 Chapter acceptance calibration | 否 | D4 明确标注不授权 |
| Agent runtime / multi-year runtime | 否 | 未触及 |
| Score-loop / golden/readiness | 否 | 未触及 |
| PR / push / release | 否 | 未触及 |
| 输出 secret / base URL / model / raw prompt / draft 正文 / raw response | 否 | 全部为安全字段 |

PASS。

---

## Historical Artifact Substitution 检查

Evidence 全部基于 retained artifact `host_run_b52b779e7e9a43c`（2026-06-04T09:12:39Z）。Reviewer 确认：

- D1-D3 所有数值均从该 retained artifact 的 chapter JSON 中直接提取
- 无任何数值来自 2026-06-02 或更早的历史 run
- D4 执行摘要中提到的 Ch3 `programmatic:C2` / `code_bug_other` 明确标注为「独立 residual，本 gate 不涉及」，且来自 plan 的历史背景说明而非当前 retained artifact

无 historical artifact substitution。

---

## Over-Claim 检查

| Claim | 评估 |
|---|---|
| 「12/12 全部 ReadTimeout」 | 正确，直接证据 |
| 「elapsed 紧聚 [60003, 60224] ms」 | 正确，直接证据 |
| 「prompt tokens [946, 2879]」 | 正确，直接证据 |
| 「exit 1 / stdout empty」 | 推断而非直接测量，但 controller judgment 已接受此推断方法 |
| 「20 blocking issues」 | 正确计数 |
| D4 READY 不等于 endpoint working | 正确限定 |
| 残余分类 endpoint_availability_residual | 被 D1-D3 evidence 支撑 |

无 over-claim。

---

## Gate Sequencing 检查

| 检查项 | 结果 |
|---|---|
| Plan accepted checkpoint 存在 | `75150ce`（startup packet 确认） |
| Evidence 在 plan acceptance 之后执行 | 是（evidence 引用 plan 和 controller judgment） |
| Evidence 未进入 plan 未授权的领域 | 确认——仅 D1-D4 静态 disposition |
| Evidence 未提前进入下一个 gate | 确认——未运行 live provider、未做 Chapter calibration |

PASS。

---

## Non-Blocking Findings

### NB-1: D1 表未区分 terminal 字段来源结构

**位置**: evidence D1.1 表
**描述**: Ch1/Ch6 的 terminal 字段位于 `attempts[0]` 层级（attempt 结构体内），Ch2-Ch5 的 terminal 字段位于 chapter JSON 顶层（无 attempts 数组）。Evidence 表将两者统一列出，未标注来源结构差异。
**影响**: 不影响正确性——terminal 值本身一致。但对后续读者理解 chapter JSON schema 差异可能造成困惑。
**建议**: 可选——在 D1 表下方添加脚注说明 Ch1/Ch6 有 attempt 结构而 Ch2-Ch5 无。

### NB-2: D3 final_assembly_issues 描述精确度

**位置**: evidence D3 表 `final_assembly_issues` 行
**描述**: 声称「20 blocking issues，覆盖全部 6 章 + Ch7 readiness」。实际 20 条中 1 条是 orchestration-level (`orchestration_not_accepted`)，19 条是 chapter-level。描述遗漏了 orchestration-level issue 的独立性。
**影响**: 总数正确，安全判定不受影响。
**建议**: 可选——改为「20 blocking issues：1 orchestration + 3×6 chapter + 1 ch7 readiness」。

### NB-3: Ch3 programmatic:C2 残余引用为历史上下文

**位置**: evidence 执行摘要
**描述**: 提到「Chapter 3 `programmatic:C2` / `code_bug_other`（独立 residual，本 gate 不涉及）」。此信息来自 plan 的历史背景说明，当前 retained artifact 中 Ch3 仅有 writer timeout（无 C2 证据）。Evidence 未显式标注此为历史上下文引用。
**影响**: 不影响 D1-D4 判定。但严格来说，evidence 应区分「当前 retained artifact 直接证据」与「plan 历史背景引用」。
**建议**: 可选——在执行摘要中将 Ch3 C2 residual 标注为「plan context reference, not from current retained artifact」。

---

## Required Fixes

无。3 个 non-blocking findings 均为可选改进，不要求 evidence 修订。

---

## Controller Recommendation

**建议: ACCEPT evidence as-is.**

- D1-D4 全部 PASS
- 12 条 provider call diagnostic 数值全部与 retained artifact 同源一致
- Fail-closed safety 完整验证
- D4 READY 含义正确限定，无 over-claim
- Redaction 和 forbidden-scope 全部通过
- 无 historical artifact substitution、secret leakage 或 gate sequencing violation
- 3 个 non-blocking findings 为可选精确度改进，不要求修订

Controller 可接受此 evidence，确认 calibration readiness verdict，并决定下一步 gate。
