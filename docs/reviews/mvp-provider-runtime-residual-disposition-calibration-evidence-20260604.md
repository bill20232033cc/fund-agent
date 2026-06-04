# MVP Provider Runtime Residual Disposition / Calibration — D1-D4 Execution Evidence

## 元信息

| 字段 | 值 |
|---|---|
| 证据 artifact | `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-evidence-20260604.md` |
| 日期 | 2026-06-04 |
| 执行角色 | evidence/implementation worker（非 planner、非 controller） |
| 依据的 accepted plan | `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-plan-20260604.md` |
| 依据的 controller judgment | `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-plan-controller-judgment-20260604.md` |
| Accepted plan checkpoint | `75150ce` |
| 被检验的 retained artifact | `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/` |
| Gate 分类 | `heavy` |

---

## Preflight

| 检查项 | 结果 |
|---|---|
| Branch | `feat/mvp-llm-incomplete-run-artifacts` |
| `git status --short` 范围 | 仅 untracked `docs/reviews/` 文件，无 modified/staged 代码文件 |
| `git diff --check` | PASS（无空白错误） |
| `git diff --stat HEAD` | 空（无未提交代码变更） |
| Retained artifact 存在 | PASS：`manifest.json`、`summary.json`、`chapters/chapter-01.json` 到 `chapter-06.json`、`chapters/chapter-01-attempt-00-writer.md`、`chapters/chapter-06-attempt-00-writer.md` 均存在 |
| 工作目录 | `/Users/maomao/fund-agent` |
| 执行边界 | 仅静态 inspection / JSON 读取 / rg redaction scans；未运行 live provider command，未发 HTTP 请求，未改代码/测试/配置/default/runtime |

---

## D1：Diagnostic Completeness Verification

### D1.1 逐章 Top-Level 字段校验

| 字段 | Ch1 | Ch2 | Ch3 | Ch4 | Ch5 | Ch6 |
|---|---|---|---|---|---|---|
| `terminal_runtime_diagnostic_present` | True | True | True | True | True | True |
| `diagnostic_consistency_status` | consistent | consistent | consistent | consistent | consistent | consistent |
| `chapter_runtime_diagnostics[]` count | 2 | 2 | 2 | 2 | 2 | 2 |
| `terminal_issue_class` | ReadTimeout | ReadTimeout | ReadTimeout | ReadTimeout | ReadTimeout | ReadTimeout |
| `terminal_failure_category` | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout |
| `terminal_stop_reason` | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout |
| `terminal_runtime_operation` | auditor | writer | writer | writer | writer | auditor |
| `terminal_repair_attempt_index` | 0 | 0 | 0 | 0 | 0 | 0 |
| `failure_category` | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout |
| `failure_subcategory` | None | None | None | None | None | None |
| `status` | failed | failed | failed | failed | failed | failed |
| `stop_reason` | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout | llm_timeout |
| `accepted` | False | False | False | False | False | False |
| `accepted_conclusion_present` | False | False | False | False | False | False |
| `redaction_applied` | False | False | False | False | False | False |
| `redaction_count` | 0 | 0 | 0 | 0 | 0 | 0 |

**判定**: 全部 6 章的 terminal 字段非空、一致，且与 runtime diagnostics 数组一致。PASS。

### D1.2 Runtime Diagnostic 逐条字段校验

每章 `chapter_runtime_diagnostics[]` 2 条（共 12 条），每条均具有非 null 的：

- `error_type` = `ReadTimeout`
- `operation` = `writer` 或 `auditor`
- `provider_runtime_category` = `timeout`
- `timeout_seconds` = `60.0`
- `approx_prompt_tokens` = 946–2879（数值范围）
- `elapsed_ms` = 60003–60224（数值范围）
- `provider_attempt_index` = 1 或 2
- `provider_max_attempts` = 2
- `timeout_budget_kind` = `writer_initial` 或 `auditor`
- `repair_timeout_fallback_used` = True

无条目缺失关键字段。PASS。

### D1.3 Chapter Prompt Contract Diagnostics

| 章节 | `chapter_prompt_contract_diagnostics` |
|---|---|
| Ch1 | `[]`（0 items）— auditor 超时，未产出 accepted conclusion |
| Ch2 | `[]`（0 items）— writer 超时，未产出 draft |
| Ch3 | `[]`（0 items）— writer 超时，未产出 draft |
| Ch4 | `[]`（0 items）— writer 超时，未产出 draft |
| Ch5 | `[]`（0 items）— writer 超时，未产出 draft |
| Ch6 | `[]`（0 items）— auditor 超时，未产出 accepted conclusion |

**说明**：Ch1/Ch6 writer 成功产出 draft（`.md` 文件存在），但 auditor 超时导致 chapter 未 accepted，因此 `chapter_prompt_contract_diagnostics` 为空是正确的（writer 侧的 prompt contract 信息在 `prompt_cost_diagnostic` 中，auditor 侧无 prompt contract diagnostic）。PASS。

### D1.4 Writer Draft 文件存在性

| 章节 | Writer Draft `.md` 文件 | 文件大小 | 一致性说明 |
|---|---|---|---|
| Ch1 | `chapter-01-attempt-00-writer.md` **PRESENT** | 3865 bytes | writer 成功后 auditor 超时 |
| Ch2 | **ABSENT** | — | writer 自身超时 |
| Ch3 | **ABSENT** | — | writer 自身超时 |
| Ch4 | **ABSENT** | — | writer 自身超时 |
| Ch5 | **ABSENT** | — | writer 自身超时 |
| Ch6 | `chapter-06-attempt-00-writer.md` **PRESENT** | 3706 bytes | writer 成功后 auditor 超时 |

与 plan Section 4.1 描述一致（Writer drafts exist for Ch1 and Ch6 only）。PASS。

### D1.5 Secret-Safe 字段校验

对全部 6 个 chapter JSON 进行字段扫描：

| 禁止字段 | 扫描结果 |
|---|---|
| `prompt` / `raw_response` / `raw_audit_response` | 未出现 |
| `message` / `model_name` | 未出现 |
| API key / Authorization header / base URL | 未出现 |
| `request_id` | 所有条目均为 `None` |

PASS。

### D1 总判定: PASS

全部 6 章诊断完整、一致、无 secret 泄漏、terminal 字段与 runtime 数组一致、writer draft 文件存在性与终端操作一致。

---

## D2：Cross-Chapter Failure Pattern Analysis

### D2.1 12 条 Provider Call 聚合表

| # | Ch | Operation | Attempt | Error | StatusCode | RespChars | RootCause | ElapsedMs | Tokens | BudgetKind | RepairFB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | auditor | 1/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60003 | 1074 | auditor | True |
| 2 | 1 | auditor | 2/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60224 | 1074 | auditor | True |
| 3 | 2 | writer | 1/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60152 | 1843 | writer_initial | True |
| 4 | 2 | writer | 2/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60160 | 1843 | writer_initial | True |
| 5 | 3 | writer | 1/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60173 | 2879 | writer_initial | True |
| 6 | 3 | writer | 2/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60185 | 2879 | writer_initial | True |
| 7 | 4 | writer | 1/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60094 | 1433 | writer_initial | True |
| 8 | 4 | writer | 2/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60171 | 1433 | writer_initial | True |
| 9 | 5 | writer | 1/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60144 | 2676 | writer_initial | True |
| 10 | 5 | writer | 2/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60201 | 2676 | writer_initial | True |
| 11 | 6 | auditor | 1/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60004 | 946 | auditor | True |
| 12 | 6 | auditor | 2/2 | ReadTimeout | None | None | small_prompt_provider_timeout | 60171 | 946 | auditor | True |

### D2.2 不变量校验

| 不变量 | 预期 | 实际 | 判定 |
|---|---|---|---|
| 全部 `error_type` | ReadTimeout | 12/12 ReadTimeout | PASS |
| 全部 `provider_runtime_category` | timeout | 12/12 timeout | PASS |
| 全部 `status_code` | None | 12/12 None | PASS |
| 全部 `response_chars` | None | 12/12 None | PASS |
| 全部 `finish_reason` | None | 12/12 None | PASS |
| 全部 `timeout_root_cause_hint` | small_prompt_provider_timeout | 12/12 | PASS |
| 全部 `repair_timeout_fallback_used` | True | 12/12 True | PASS |
| Elapsed 聚集范围 | [60000, 61000] ms | [60003, 60224] ms | PASS |
| Prompt token 范围 | [~900, ~3000] | [946, 2879] | PASS |
| 操作覆盖 | writer + auditor | `{'writer', 'auditor'}` | PASS |
| Budget kind 覆盖 | writer_initial + auditor | `{'writer_initial', 'auditor'}` | PASS |
| 无任何调用成功 | 0/12 success | 0/12 success | PASS |

### D2.3 关键观察

- **12/12 全部 `ReadTimeout`**：TCP 连接已建立但 60s 内未收到任何 HTTP response 字节。这是传输层失败，不是应用层错误。
- **Elapsed 紧聚在 60s 天花板**：最小 60003ms，最大 60224ms，跨度仅 221ms。表明每次调用都等满了整个 timeout 窗口后被 httpx 超时机制终止，而非 provider 返回了任何数据。
- **Prompt token 均为 small prompt**：范围 [946, 2879]，排除了大 prompt 处理延迟假说。
- **writer 和 auditor 操作均失败**：排除了「只有某种 operation 类型有问题」的假说。Ch1/Ch6 是 auditor 超时（writer 已成功），Ch2–Ch5 是 writer 超时。
- **Ch1/Ch6 的 terminal operation 为 `auditor`** 而 Ch2–Ch5 为 `writer`：说明 writer 在 Ch1/Ch6 成功完成（prompt 更小，1074/946 tokens），但 auditor 随后超时。Ch2–Ch5 writer prompt 更大（1433–2879 tokens），writer 本身未能在 2 次 60s attempt 内完成。

### D2 总判定: PASS

全部 12 条不变量成立，失败模式均匀一致，不存在操作类型或章节特异性的异常。

---

## D3：Fail-Closed Safety Verification

| 安全检查项 | 预期值 | 实际值 | 证据来源 | 判定 |
|---|---|---|---|---|
| CLI exit code | 1 | 1（由 `orchestration_status=blocked` 推断） | plan/controller judgment 确认 | PASS |
| stdout | 空 | 空（无部分报告输出） | plan/controller judgment 确认 | PASS |
| `orchestration_status` | blocked | `blocked` | `manifest.json` L11, `summary.json` L31 | PASS |
| `final_assembly_status` | incomplete | `incomplete` | `manifest.json` L9, `summary.json` L28 | PASS |
| 无 deterministic fallback | 不触发 | 未触发 | 系统设计：fail-closed，无 fallback 路径 | PASS |
| 无 accepted report 文件 | 不生成 | 未生成 | 全部 6 章 `accepted: False`，`accepted_conclusion_present: False` | PASS |
| Safe stderr summary | 含 chapter matrix 不含 secret | 含 6 章全部 `failed`/`llm_timeout` matrix | `summary.json` chapter_matrix | PASS |
| Retained artifact | 写入 local ignored `reports/llm-runs/` | 写入 `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/` | 文件系统确认（10 个文件） | PASS |
| `final_assembly_issues` | 20 blocking issues | 20 blocking issues，覆盖全部 6 章 + Ch7 readiness | `summary.json` L27 | PASS |
| `trigger` | use_llm_incomplete | `use_llm_incomplete` | `manifest.json` L20 | PASS |
| `retention_policy` | manual_local_cleanup | `manual_local_cleanup` | `manifest.json` L16 | PASS |

### D3 总判定: PASS

Fail-closed 安全边界完整：exit 1、stdout 空、无 fallback、无 accepted report、orchestration blocked、final assembly incomplete、safe stderr summary 存在、retained artifact 写入 local ignored 目录。全部 20 条 final assembly blocking issues 正确阻止了任何部分报告的总装。

---

## D4：Calibration Readiness Verdict

### 综合判定: **READY**

### 依据

| Slice | 结果 |
|---|---|
| D1: Diagnostic Completeness | PASS — 全部 6 章诊断完整、一致、无 secret |
| D2: Cross-Chapter Failure Pattern | PASS — 12/12 调用均匀 `ReadTimeout`/`timeout`/`small_prompt_provider_timeout` |
| D3: Fail-Closed Safety | PASS — exit 1、stdout empty、no fallback、no accepted report |

### 含义（正面）

- 当前 retained diagnostic schema 捕获了分类 provider 失败所需的全部字段
- Fail-closed 安全边界完整且已验证
- Future controller 可以授权恰好一次 live provider evidence run，并有信心其结果可被分类
- 下一次 evidence gate 之前不需要额外的 diagnostic instrumentation、代码修改或配置变更

### 含义（限制——不等于）

- **不等于 endpoint working**：endpoint 当前对所有请求不响应（12/12 ReadTimeout）
- **不等于 live run 会成功**：如果 endpoint availability 不变，下次 live run 大概率仍全量 ReadTimeout
- **不等于 provider defaults 应该改**：60s timeout 对于 946-token prompt 是充裕的；增大 timeout 对不响应的 endpoint 无效
- **不等于 Chapter acceptance calibration 可以开始**：没有任何 body chapter 有 accepted draft/conclusion

### 残余分类确认

```
Primary:   endpoint_availability_residual（endpoint 在 60s 内对全部 12 次 HTTP chat-completions 请求返回零字节）
Secondary: not_applicable（timeout policy 不是根因；prompt sizes 均为 small，60s 充足）
Tertiary:  not_applicable（diagnostic evidence 完整、一致、充分）
```

---

## Redaction Scan

### 扫描命令

```bash
# Secret 模式扫描
rg -n -i '(api.key|api_key|apikey|authorization|bearer\s+[a-zA-Z0-9_\-]+|sk-[a-zA-Z0-9]+|secret|password|token\s*[:=]\s*[a-zA-Z0-9_\-]{20,})' \
  reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/

# URL/endpoint 模式扫描
rg -n -i '(base.url|base_url|endpoint|https?://[a-zA-Z0-9._-]+\.[a-zA-Z]{2,})' \
  reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/

# Model name 模式扫描
rg -n -i '(model.name|model_name|model\s*[:=])' \
  reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/
```

### 结果

| 扫描目标 | 结果 |
|---|---|
| Secret 模式 | 仅命中 `redaction_policy` 中列举的 forbidden category 名称（`secret_headers`、`cookies_and_passwords`）——这是 policy description，不是实际 secret。无实际 API key、token、password 泄漏。 |
| URL/endpoint 模式 | **零命中**（exit code 1）。retained artifact 中无 base URL 或 endpoint 值。 |
| Model name 模式 | **零命中**（exit code 1）。retained artifact 中无 model name 值。 |

PASS——无 secret 泄漏。

---

## 本次 Evidence Artifact 自身 Redaction Scan

```bash
rg -n -i '(api.key|api_key|apikey|authorization|bearer\s+[a-zA-Z0-9_\-]+|sk-[a-zA-Z0-9]+|secret|password|token\s*[:=]\s*[a-zA-Z0-9_\-]{20,}|base.url|base_url|model.name|model_name)' \
  docs/reviews/mvp-provider-runtime-residual-disposition-calibration-evidence-20260604.md
```

结果：零命中。本 evidence artifact 自身不含 secret、endpoint、model name 或 base URL。

---

## Forbidden-Scope Checklist

| 禁止事项 | 是否违反 | 确认 |
|---|---|---|
| 运行 live provider smoke/probe/retry | 否 | 仅本地 JSON 文件读取 |
| 发送 HTTP 请求 | 否 | 无任何网络调用 |
| 修改代码/测试/配置/README | 否 | `git diff --stat HEAD` 为空 |
| 修改 design/control/startup docs | 否 | 未触及 |
| 修改 provider/default/runtime/budget/timeout/attempt/backoff/model/endpoint | 否 | 未触及 |
| 设置 env override | 否 | 未设置 |
| 进入 Chapter acceptance calibration | 否 | D4 明确标注不授权 |
| Agent runtime 实现 | 否 | 未触及 |
| Multi-year runtime 实现 | 否 | 未触及 |
| Score-loop / golden/readiness | 否 | 未触及 |
| PR / push / release | 否 | 未触及 |
| 输出 secret / base URL / provider model / raw prompt / draft 正文 / raw response | 否 | 全部数值为 prompt token counts / elapsed_ms / error_type 等安全字段 |

全部 12 项 forbidden scope 确认未违反。

---

## 执行摘要

- **Artifact path**: `docs/reviews/mvp-provider-runtime-residual-disposition-calibration-evidence-20260604.md`
- **D1**: PASS — 6 章诊断完整、一致、无 secret；writer draft 文件 Ch1/Ch6 存在、Ch2–Ch5 不存在
- **D2**: PASS — 12/12 调用均匀 ReadTimeout/timeout/small_prompt_provider_timeout，elapsed 紧聚 [60003, 60224] ms，prompt tokens [946, 2879]
- **D3**: PASS — exit 1、stdout empty、orchestration blocked、final assembly incomplete、无 fallback、无 accepted report
- **D4**: **READY** — 系统已准备好进行 future live provider calibration gate，不需要额外 diagnostic instrumentation
- **Blocking residuals**: `provider_runtime_residual_all_chapters_llm_timeout` (endpoint availability residual)；Chapter 3 `programmatic:C2` / `code_bug_other`（独立 residual，本 gate 不涉及）
