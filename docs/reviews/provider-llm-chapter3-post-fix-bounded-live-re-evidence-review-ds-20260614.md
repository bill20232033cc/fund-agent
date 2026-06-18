# AgentDS 证据审查：Provider/LLM Chapter 3 Post-fix Bounded Live Re-evidence

## Scope

- **Mode**: role-scoped evidence review（AgentDS）
- **审查输入**: `docs/reviews/provider-llm-chapter3-post-fix-bounded-live-re-evidence-20260614.md`
- **验证来源**:
  - `AGENTS.md`
  - `docs/current-startup-packet.md`
  - `docs/implementation-control.md`
  - `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/manifest.json`
  - `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/summary.json`
  - `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/chapters/chapter-03.json`
- **排除范围**: 代码、设计文档、控制文档、writer markdown、auditor feedback、raw prompts、provider payloads、source/cache/PDF bodies、live/provider/LLM/network 命令
- **边界**: 仅审查证据工件是否正确且完整；不做实现修复

## Findings

### 核心声明交叉验证

以下逐条对照证据工件声明与运行时 JSON 工件：

---

**声明 1**: 修复后受限 live 命令仍然 fail-closed

- **证据工件（第52行）**: `Exit code: 1`
- **manifest.json**: `orchestration_status: "partial"`, `final_assembly_status: "incomplete"`
- **summary.json**: `orchestration_status: "partial"`, `final_assembly_status: "incomplete"`
- **chapter-03.json**: `status: "failed"`, `stop_reason: "llm_exception"`
- **结论**: 一致。命令以非零退出码失败，编排状态为 partial，最终组装 incomplete。

---

**声明 2**: Chapter 3 仍为第一个失败章节

- **证据工件（第64行）**: `first_failed_chapter_id=3`
- **summary.json**: `first_failed.chapter_id: 3`
- **chapter-03.json**: `chapter_id: 3`, `status: "failed"`
- **结论**: 一致。

---

**声明 3**: Chapter 3 仍在 writer 操作处失败，未到达 provider 执行

- **证据工件（第67行）**: `first_failed_runtime_operation=writer`
- **chapter-03.json**: `terminal_runtime_operation: "writer"`, `operation: "writer"`（在 `chapter_runtime_diagnostics[0]` 中）
- **summary.json**: `first_failed.runtime_operation: "writer"`
- **结论**: 一致。失败发生在 writer 阶段，早于任何 provider 调用。

---

**声明 4**: Provider 调用次数仍为 `0`

- **证据工件（第68行）**: `first_failed_provider_attempts=0/unknown`
- **summary.json**: `first_failed.provider_attempt_count: 0`
- **chapter-03.json**: `attempts: []`（空数组），`provider_attempt_index: null`
- **结论**: 一致。provider_attempt_count 为零，chapter-03 无任何 attempt 记录。

---

**声明 5**: 运行时诊断记录 `error_type=ValueError`, `failure_category=code_bug`, `stop_reason=llm_exception`

- **证据工件（第65-66行）**: `first_failed_status=failed`, `first_failed_stop_reason=llm_exception`, `first_failed_category=code_bug`
- **chapter-03.json**: `error_type: "ValueError"`, `failure_category: "code_bug"`, `stop_reason: "llm_exception"`, `terminal_issue_class: "ValueError"`, `terminal_failure_category: "code_bug"`
- **summary.json**: `first_failed.failure_category: "code_bug"`, `first_failed.stop_reason: "llm_exception"`, `runtime_diagnostics.first_failed.terminal_issue_class: "ValueError"`
- **证据工件（第95行）**: 提到 `error_type=ValueError`
- **结论**: 一致。全部四个诊断字段在所有三个 JSON 工件中吻合。

---

**声明 6**: `max_output_chars=12000` 存在于 Chapter 3 运行时诊断中，非先前 null-cap 元数据残留

- **证据工件（第70行）**: `first_failed_max_output_chars=12000`
- **证据工件（第96行）**: `max_output_chars=12000 is present in the Chapter 3 runtime diagnostic`
- **chapter-03.json**: `chapter_runtime_diagnostics[0].max_output_chars: 12000`
- **summary.json**: `runtime_diagnostics.first_failed.max_output_chars: 12000`
- **结论**: 一致。`max_output_chars` 在两个 JSON 源中均存在且值为 12000。排除了之前运行中观察到的 null-cap 问题。

---

**声明 7**: 第1、2、4、5、6章达到 accepted 状态；最终组装因第3章未 accepted 而受阻

- **证据工件（第71行）**: `chapter_matrix=1:accepted;2:accepted;3:failed;4:accepted;5:accepted;6:accepted`
- **证据工件（第97行）**: 第1、2、4、5、6章为 accepted，最终组装被阻断
- **summary.json** `chapter_matrix`: 第1、2、4、5、6章 `status: "accepted"`，第3章 `status: "failed"`
- **summary.json** `final_assembly_issues`: 5个阻断问题均涉及第3章和编排状态
- **结论**: 一致。

---

### 其他验证

**Guardrails 遵守**（证据工件第17-21行）：证据声明未读取 Eastmoney/fallback、PDF/source/cache body、writer markdown、raw prompt、provider payload 或 chapter body。summary.json 中 `artifact_files` 列表显示第3章仅有 `chapter-03.json`，无 writer/auditor markdown 文件——这与第3章 writer 执行前即失败的事实一致。第1、2、4、5、6章存在 writer/auditor markdown 文件，但证据声明未读取它们。此声明为过程性声明，无法仅从 JSON 工件中独立验证，但与可见工件状态兼容。

**Evidence Limits**（证据工件第99-111行）：限制部分正确说明证据范围——证明 writer-before-provider 失败，未证明 provider 可用性、LLM 内容质量、报告/发布就绪状态。这些限制与运行时工件中实际捕获的内容一致。

**Residuals 表**（证据工件第115-121行）：两个 residual 分类正确：
- Chapter 3 仍然 writer-before-provider 失败，为开放阻断项
- Provider 可用性和 LLM 内容质量推迟至 Chapter 3 到达 provider 调用后

**Verdict**（证据工件第125行）：`LIVE_FAIL_CLOSED_STILL_PROVIDER_BEFORE_CODE_BUG_NOT_READY` 准确反映了证据数据。

**推荐下一 gate**（证据工件第127-129行）：`Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence Gate` 是从当前证明的失败模式出发的逻辑下一步。

---

### 未覆盖区域 / 细微差异

1. **run_id 目录命名差异**：证据工件第53行引用目录 `host_run_c1b20382568e4ae`，但 manifest.json 中的 `run_id` 为 `host_run_c1b20382568e4ae0`（多一个尾部 `0`）。证据在第56行正确报告了 manifest 的 `run_id`。目录名与 run_id 不完全一致属于文件系统产物，不影响证据正确性。

2. **修复提交验证**：证据依赖 controller judgment 链来确认提交 `2bced82` 的修复已被接受并是运行时代码。证据未独立验证该提交是否确实为 live 命令执行时的活动代码。在 gateflow 上下文中，作为先决条件引用此前提是可以接受的，但应注意此为信任链依赖，而非独立验证。

3. **CLI 专用字段**：`exit code: 1`（第52行）和 `elapsed_ms: 188648`（第57行）是 CLI 诊断输出，在 JSON 运行时工件中不可用。这些字段无法针对允许的验证源进行交叉检查，但它们是命令输出的标准字段。

4. **内部诊断一致性**：chapter-03.json 中的 `diagnostic_consistency_status: "consistent"` 和 summary.json 第3章运行时诊断中的相同字段确认了系统的内部一致性检查通过——runtime diagnostic 与 prompt contract diagnostic 之间没有不一致。证据工件未提及此内容，但也不要求提及。

## Open Questions

- 无。证据工件中的全部可验证声明均已针对可用运行时 JSON 工件进行交叉检查，且全部吻合。

## Residual Risk

- CLI 专用数值（exit code、elapsed_ms）无法针对允许的 JSON 工件进行独立验证；信任证据编写者的 CLI 观察。
- 此审查未验证修复提交 `2bced82` 是否确实为 live 命令执行时的活动签出代码。在 gateflow 上下文中，此前提由 controller judgment 链建立。
- 未读取第1、2、4、5、6章的章节正文或 auditor feedback；此范围排除由硬边界强制执行，与证据工件自身的 guardrails 一致。

## Verdict

**PASS**

证据工件正确得出结论：修复后 live 命令仍然 fail-closed，Chapter 3 在 writer 操作处失败（早于 provider），`error_type=ValueError`、`failure_category=code_bug`、`provider_attempt_count=0`。全部可交叉验证的声明均与运行时 JSON 工件吻合。未发现实质性问题。
