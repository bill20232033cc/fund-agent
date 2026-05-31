# MVP provider runtime timeout hardening code review

日期：2026-05-31

Gate：`MVP provider runtime timeout hardening gate`

角色：review worker，不是 implementation worker。

Review scope：当前 implementation diff + plan + controller judgment + implementation evidence。

## Verification commands run

| Command | Result |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q` | PASS, 157 passed |
| `git diff --name-only HEAD` | 见下方 scope 分析 |

## Findings

### B-1 [BLOCKING] Forbidden files modified: fund_agent/fund/chapter_writer.py, fund_agent/fund/chapter_auditor.py

**文件**: `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py`

Plan 明确禁止本 gate 修改这两个文件：

> 显式禁止修改：
> - `fund_agent/fund/chapter_writer.py` 和 `fund_agent/fund/chapter_auditor.py`，本 gate 不扩展 Fund-layer Protocol request/response，不把 provider diagnostics 放入 Fund primitive。

Controller judgment 再次确认：

> Implementation must not modify:
> - `fund_agent/fund/chapter_writer.py`
> - `fund_agent/fund/chapter_auditor.py`
> - Fund-layer LLM request/response dataclasses or Protocol signatures

实际 diff 显示大量变更：

**chapter_writer.py**:
- 新增 `REQUIRED_BODY_SECTION_HEADINGS`, `REQUIRED_OUTPUT_MARKER_PREFIX`, `INCOMPLETE_FINISH_REASONS` 常量
- 新增 `ChapterRepairContext` dataclass
- `ChapterLLMRequest` 新增 `repair_context` 字段
- `ChapterWriterInput` 新增 `repair_context` 字段
- `build_chapter_writer_input()` 新增 `repair_context` 参数
- 新增 `_repair_context_prompt()`, `_prompt_required_output_payload()`, `_required_structure_issues()`, `_required_output_marker_issues()`, `_required_output_marker()` 函数
- `_draft_from_llm_response()` 新增 `response_incomplete` stop reason 检测
- `response_too_long` stop reason 从 `llm_contract_violation` 改为独立值
- `unknown_anchor` stop reason 从 `llm_contract_violation` 改为独立值
- 大量 prompt 文本变更（结构段落要求、required_output marker 要求、candidate facet 写法要求）

**chapter_auditor.py**:
- 新增 `_ASSERTED_FACET_RE_TEMPLATE` 常量
- 新增 `_required_output_marker()`, `_facet_asserted()` 函数
- `_audit_contract_markers()` 从裸 item 文案匹配改为 exact marker 匹配
- `_audit_non_asserted_facets()` 从窗口扫描改为正则匹配
- `_llm_request()` system_prompt 和 user_prompt 大幅重写（更严格的行协议要求）
- `_llm_parse_failure()` 消息更新

这些变更属于 Gate A（writer/auditor contract hardening）scope，不是本 gate（provider runtime timeout hardening）scope。即使这些变更是从上一个 gate 的未提交工作遗留下来的，当前 diff 中包含 forbidden 文件仍构成 scope violation。

### B-2 [BLOCKING] Forbidden files modified: docs/current-startup-packet.md, docs/implementation-control.md

**文件**: `docs/current-startup-packet.md`, `docs/implementation-control.md`

Plan 明确禁止：

> `docs/implementation-control.md`、`docs/current-startup-packet.md`、`docs/design.md`，除非 controller 在后续 gate 单独授权 docs/control sync。

`git diff --name-only HEAD` 显示这两个文件被修改。`docs/current-startup-packet.md` 的变更包括 gate status 和 next entry point 更新。`docs/implementation-control.md` 未在 allowed files 列表中。

### B-3 [BLOCKING] Non-allowed files modified: fund_agent/fund/README.md, tests/fund/test_chapter_auditor.py, tests/fund/test_chapter_writer.py

**文件**: `fund_agent/fund/README.md`, `tests/fund/test_chapter_auditor.py`, `tests/fund/test_chapter_writer.py`

这三个文件不在 plan allowed files 列表中。`fund_agent/fund/README.md` 的变更同步了 chapter_writer/chapter_auditor 的新 contract 语义。测试文件新增了 Gate A contract 的测试覆盖。

### F-1 [HIGH] Timeout-only retry correctly scoped, but combined with non-gate scope changes

本 gate 核心实现（Slice A-D）本身正确：

- `fund_agent/config/llm.py`: 新增 `timeout_max_attempts` / `timeout_backoff_seconds` typed config，边界 `[1,3]` / `[0,30]`，默认 `2` / `1.0`。✅
- `fund_agent/services/llm_provider.py`: timeout-only bounded retry，`_complete()` 内循环 `timeout_max_attempts` 次，backoff 可注入 sleep，429/network/malformed 不 retry。✅
- `fund_agent/services/chapter_orchestrator.py`: `ChapterLLMRuntimeDiagnostic` 定义在 Service 层，provider 层只填 provider-safe 字段，orchestrator enrich 章节 identity。✅
- `fund_agent/ui/cli.py`: `_llm_incomplete_message()` 输出 `first_failed_chapter_id/status/stop_reason`，stdout 为空。✅
- 测试覆盖了 bounded retry、non-timeout no retry、diagnostic propagation、missing config fail-closed。✅

但这些正确实现被 B-1/B-2/B-3 的 scope violation 包裹，无法独立 accept。

### F-2 [MEDIUM] Provider exception type matching uses string comparison instead of isinstance

`chapter_orchestrator.py:960-968` 和 `1180-1190` 中 `_provider_runtime_stop_reason()` 和 `_provider_runtime_category_from_exception()` 使用 `type(exc).__name__` 字符串比较而非 `isinstance`。这在当前单文件导入场景下可行，但如果异常类被重命名或子类化，匹配会静默失败。当前 gate scope 内这不构成 blocking，但值得注意。

### F-3 [LOW] _sanitize_text 两个实例有微妙差异

`llm_provider.py:585-594` 和 `chapter_orchestrator.py:1526` 各有 `_sanitize_text()` 实现。两者 redaction 列表不同：provider 版包含 `"writer user"` 和 `"draft markdown"`，orchestrator 版不包含。plan 要求 diagnostic message 使用 `_sanitize_text()` 或等价 helper，两个实现都满足最低要求，但不一致可能导致 future drift。

### F-4 [LOW] CLI _llm_incomplete_message 使用 untyped result parameter

`cli.py:807` 的 `_llm_incomplete_message(result)` 使用 `# type: ignore[no-untyped-def]`。这是 pre-existing pattern，本 gate 未引入，不 blocking。

## Scope analysis

`git diff --name-only HEAD` 实际变更文件 vs plan allowed files：

| 文件 | Plan allowed | 实际修改 |
|---|---|---|
| `fund_agent/config/llm.py` | ✅ | ✅ |
| `fund_agent/services/llm_provider.py` | ✅ | ✅ |
| `fund_agent/services/chapter_orchestrator.py` | ✅ | ✅ |
| `fund_agent/ui/cli.py` | ✅ | ✅ |
| `tests/config/test_llm_config.py` | ✅ | ✅ |
| `tests/services/test_llm_provider.py` | ✅ | ✅ |
| `tests/services/test_chapter_orchestrator.py` | ✅ | ✅ |
| `tests/ui/test_cli.py` | ✅ | ✅ |
| `fund_agent/config/README.md` | ✅ | ✅ |
| **`fund_agent/fund/chapter_writer.py`** | **❌ forbidden** | **✅ modified** |
| **`fund_agent/fund/chapter_auditor.py`** | **❌ forbidden** | **✅ modified** |
| **`fund_agent/fund/README.md`** | **❌ not listed** | **✅ modified** |
| **`tests/fund/test_chapter_auditor.py`** | **❌ not listed** | **✅ modified** |
| **`tests/fund/test_chapter_writer.py`** | **❌ not listed** | **✅ modified** |
| **`docs/current-startup-packet.md`** | **❌ forbidden** | **✅ modified** |
| **`docs/implementation-control.md`** | **❌ forbidden** | **✅ modified** |

7 个非允许/禁止文件被修改。

## Secret hygiene

- `Authorization`/`Bearer`/`FUND_AGENT_LLM_API_KEY`/`sk-` 出现在 `_sanitize_text()` redaction 列表和测试 negative assertion 中，均为 safe variable name/test label。✅
- Diagnostic message 通过 `_sanitize_text()` 脱敏。✅
- Provider error 不拼接 response.text、request JSON 或 headers。✅
- Test `test_timeout_retry_exhausted_carries_provider_diagnostics` 包含 `"Authorization" not in diagnostic_text` 等 negative assertion。✅

## Deterministic default unchanged

`cli.py` 中 `analyze` 和 `checklist` 不调用 LLM config 的路径未被修改。`--use-llm` 路径仍通过 `_build_llm_clients_or_fail()` 显式构造。✅

## Conclusion

**FAIL — 3 blocking findings (B-1, B-2, B-3)**

本 gate 的核心 timeout hardening 实现（Slice A-D）在代码正确性上没有问题，但当前 diff 包含了 7 个 plan 明确禁止或未允许的文件修改。这些变更主要来自 Gate A（writer/auditor contract hardening）的未提交遗留工作，与本 gate scope 混合在一起。

建议：implementation worker 需要将本 gate scope 的变更与 Gate A 遗留变更分离。可以通过 `git stash` 或 selective commit 将 forbidden 文件的变更从当前 working tree 中移除，只保留 allowed files 的 diff。
