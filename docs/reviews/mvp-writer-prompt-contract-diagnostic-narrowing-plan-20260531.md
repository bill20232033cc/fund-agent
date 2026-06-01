# MVP writer prompt contract diagnostic narrowing plan

日期：2026-05-31

Gate：`MVP writer prompt contract diagnostic narrowing gate`

角色：Gateflow planning worker，不是 implementation worker。

## Self-check

- Current gate / role：当前只写 plan artifact；不实现、不 review、不 commit/push/PR/merge/release，不运行真实 provider。
- Source of truth：`AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、prompt-contract calibration controller judgment / implementation evidence、`controller-real-provider-006597-2024-diagnostic.json`，以及按需读取的 writer / orchestrator / CLI 相关代码。
- Scope boundary：本 plan 允许后续 implementation worker 只做最小脱敏诊断扩展和测试；不得改模板、golden、score、quality gate、Host/Agent/dayu、provider auth/config、确定性默认链路或 PR 外部状态。
- Stop condition：若需要保存完整 prompt、完整 draft、完整 provider response、API key、Authorization header，或需要放松证据锚点 / ITEM_RULE / candidate facet / 交易建议 / E2 deferred / missing semantics / no-fallback 边界，则停止并回 controller。
- Evidence and validation：完成信号是 full smoke pass，或唯一 `prompt_contract` 子类 + 章节/阶段定位 + 最小修复入口；所有 evidence 必须脱敏、按 chapter/phase 记录，不保存全文。
- Next action：plan review 通过后进入最小 implementation；本 artifact 本身不授权真实 provider rerun。

## Goal

在 provider config/auth 已验证可用、当前 blocker 已收敛为 writer `prompt_contract` / `llm_contract_violation` 的前提下，设计一个最小诊断收窄 gate，把真实 provider 失败唯一定位到可修复子类，并给出下一最小入口。

本 gate 的可接受结果只有两类：

1. `006597 / 2024 --use-llm` real provider smoke 生成完整 0-7 章报告并 exit `0`。
2. real provider 仍 fail-closed，但 evidence 唯一定位为一个 `prompt_contract` 子类，并记录 chapter、phase、attempt、最小修复入口。

## Non-goals

- 不修 writer prompt 或 parser 语义，除非仅为诊断字段暴露所需的最小代码触点。
- 不放松 writer parser、programmatic audit、LLM audit line protocol、证据锚点、ITEM_RULE、candidate facet、交易建议禁区、E2 deferred、missing semantics。
- 不新增 deterministic fallback，不让 `--use-llm` partial result 输出报告。
- 不改变 provider config/auth、timeout budget、provider SDK/HTTP 策略、multi-model split。
- 不改 `docs/fund-analysis-template-draft.md`、score/golden/fixtures/snapshot/quality gate、Host/Agent/dayu。
- 不保存完整 prompt、完整 draft、完整 provider response、API key、Authorization header 或 env dump。

## Direct Evidence

### Current accepted state

- Prompt-contract calibration 已本地接受；writer prompt 更短，auditor line protocol 继续 fail-closed，repair bounded，CLI 暴露 `first_failed_category`。
- Controller CLI smoke：exit `1`，stdout empty，first failed chapter `1`，stop reason `llm_contract_violation`，category `prompt_contract`。
- Controller service diagnostic：orchestration `partial`，chapter 1 accepted，chapter 2 blocked，stop reason `llm_contract_violation`，category `prompt_contract`，chapters 3-6 dependency skipped，final assembly incomplete。
- Provider auth/config 已不是主 blocker；timeout 已不是当前主 blocker。

### Current diagnostic gap

现有 `controller-real-provider-006597-2024-diagnostic.json` 在删除 `accepted_draft` / `accepted_conclusion` 后只包含：

- orchestration / final assembly status；
- chapter status / stop_reason / failure_category；
- attempt runtime categories / failure categories / operations。

它不能区分 `prompt_contract` 的实际子类，因为没有脱敏保存 writer issue id、issue reason count、marker count、finish reason / response length 汇总或 audit issue typed counts。

### Relevant current code facts

- `fund_agent/fund/chapter_writer.py` 已有稳定 writer issue id / reason：
  - `missing_required_structure`
  - `missing_required_output_marker`
  - `unknown_anchor`
  - `response_too_long`
  - `response_incomplete`
  - `writer:invalid_anchor_marker:*` / `writer:invalid_missing_marker:*` currently reason=`llm_contract_violation`
  - `writer:forbidden_phrase:*` currently reason=`llm_contract_violation`
  - `writer:evidence_line_without_anchor_marker` currently reason=`llm_contract_violation`
  - `writer:unknown_missing_reason:*` currently reason=`llm_contract_violation`
- `fund_agent/fund/chapter_auditor.py` programmatic audit can expose candidate facet assertion, forbidden phrase, must_not_cover, missing semantics, ITEM_RULE and evidence issues, but these currently appear after writer drafted and audit ran, not inside writer blocked diagnostics.
- `fund_agent/services/chapter_orchestrator.py` maps writer blocked issues to category `prompt_contract`, but `ChapterRunResult` does not carry a typed subcategory / issue count field.
- CLI currently prints only `first_failed_category`, not subcategory.

## Diagnostic Taxonomy

Implementation must classify each failed writer/auditor phase into exactly one primary diagnostic subcategory, while preserving all secondary counters for review.

| Subcategory | Primary signal | Phase | Minimal next entrance |
|---|---|---|---|
| `missing_structure` | writer issue reason `missing_required_structure` or missing required heading count > 0 | writer_parse | writer prompt structure wording / marker placement gate |
| `missing_required_marker` | writer issue reason `missing_required_output_marker` or required marker missing count > 0 | writer_parse | writer prompt required_output marker simplification gate |
| `unknown_anchor` | writer issue reason `unknown_anchor` or unknown anchor count > 0 | writer_parse | anchor conversion / prompt allowed-anchor copy gate |
| `invalid_marker` | issue id prefix `writer:invalid_anchor_marker:` / `writer:invalid_missing_marker:` / `writer:unknown_missing_reason:` / `writer:evidence_line_without_anchor_marker` | writer_parse | marker syntax prompt/parser diagnostic gate |
| `candidate_facet_assertion` | audit issue message/code source for non-asserted facet boundary or dedicated typed counter > 0 | programmatic_audit | candidate facet wording / repair hint gate |
| `forbidden_phrase` | issue id prefix `writer:forbidden_phrase:` or audit forbidden content counter > 0 | writer_parse or programmatic_audit | forbidden phrase prompt/repair gate |
| `response_length_incomplete` | writer issue reason `response_too_long` / `response_incomplete`, finish_reason in incomplete set, or response_chars > max_output_chars | writer_parse | output length / max token / prompt brevity gate |
| `code_bug_other` | exception not provider runtime, unmapped issue id, inconsistent drafted/blocked state, or no issue counters despite `llm_contract_violation` | service_orchestrator | code bug diagnostic/fix gate |

Primary selection order must be deterministic and safety-first:

1. `response_length_incomplete`
2. `invalid_marker`
3. `unknown_anchor`
4. `missing_required_marker`
5. `missing_structure`
6. `candidate_facet_assertion`
7. `forbidden_phrase`
8. `code_bug_other`

Rationale：length/incomplete and invalid marker explain parser impossibility first; anchor/required marker/structure are writer-output conformance; candidate facet and forbidden phrase may be post-draft audit failures and must not be mislabeled as safe prompt success.

## Minimal Code Touches If Existing Signals Are Insufficient

If plan review accepts that current issue id/message is insufficient, implementation may touch only these files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- evidence artifacts under `docs/reviews/` and `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/`

Do not change public report markdown, deterministic analyze/checklist output, provider config loading, or auditor safety rules.

### Required minimal implementation shape

1. Add a small typed diagnostic summary, not raw text:
   - recommended location: Service layer because orchestration owns chapter/phase/run diagnostics.
   - example contract fields: `schema_version`, `chapter_id`, `phase`, `attempt_index`, `primary_subcategory`, `issue_reason_counts`, `issue_id_prefix_counts`, `required_structure_missing_count`, `required_output_missing_count`, `unknown_anchor_count`, `invalid_marker_count`, `forbidden_phrase_count`, `candidate_facet_assertion_count`, `response_chars`, `max_output_chars`, `finish_reason`, `accepted_draft_present`.
   - all counts must be integers; no prompt/draft/provider response excerpts.
2. Derive writer subcategory from existing `ChapterWriteResult.issues` without changing parser acceptance behavior.
3. For invalid marker and forbidden phrase, use issue id prefix rather than storing offending marker or phrase.
4. If candidate facet assertion is needed, derive a count from typed audit issue metadata or a narrow helper that recognizes the existing programmatic audit issue; do not store facet text.
5. Surface the first failed diagnostic subcategory in CLI stderr as a short scalar, for example `first_failed_subcategory=missing_required_marker`.
6. Extend the controller diagnostic script / evidence extraction to serialize only the typed summary and chapter matrix. If no existing script exists, implementation evidence may include a small one-off command that imports Service result objects and writes a sanitized JSON; no raw LLM request/response capture.

### Explicitly disallowed implementation shortcuts

- Do not save `ChapterWriterPrompt.system_prompt`, `ChapterWriterPrompt.user_prompt`, `ChapterDraft.markdown`, `ChapterAuditLLMRequest.draft_markdown`, raw provider response, or raw audit response in JSON/evidence.
- Do not use string snippets from provider output as evidence.
- Do not turn `llm_contract_violation` into accepted draft.
- Do not reclassify candidate facet or forbidden phrase as non-blocking.
- Do not broaden allowed anchors or allowed missing reasons to make the current run pass.
- Do not add deterministic fallback or partial report output.

## Implementation Slices

### Slice A: typed prompt-contract diagnostic summary

Add the smallest data contract needed to carry prompt-contract subcategory from writer/auditor result into `ChapterRunResult`.

Expected behavior:

- accepted chapters have no primary subcategory.
- writer blocked chapters with existing issue ids produce counters and a primary subcategory.
- audit-blocked chapters can produce candidate facet / forbidden phrase counters when the programmatic audit is the blocker.
- runtime provider failures remain `llm_timeout` / `provider_runtime`, not prompt-contract subcategories.
- code inconsistency returns `code_bug_other`.

### Slice B: CLI first failed subcategory

Extend incomplete-result stderr only with a scalar `first_failed_subcategory=<value>` when available.

Expected behavior:

- stdout remains empty on failed `--use-llm`.
- existing `first_failed_chapter_id/status/stop_reason/category` remain unchanged.
- no raw issue message, prompt, draft or provider response appears in stderr.

### Slice C: sanitized evidence writer / extraction path

Produce a sanitized diagnostic JSON for real provider rerun with only:

- command label, fund code, report year, exit code, stdout byte count;
- orchestration status, final assembly status, final issue reason counts;
- chapter rows for 1-6;
- per chapter / per phase / per attempt diagnostic summary;
- provider runtime category counts and response char counts where available;
- first failed chapter/category/subcategory.

The JSON must not include accepted drafts/conclusions, prompts, request payloads, response text or raw messages.

## Tests

### Targeted unit tests

`tests/fund/test_chapter_writer.py`

- writer invalid anchor marker produces issue id prefix counted as `invalid_marker`.
- writer invalid missing marker / unknown missing reason counted as `invalid_marker`.
- writer forbidden phrase remains blocked and counted as `forbidden_phrase`.
- response length and incomplete finish reason classified as `response_length_incomplete`.
- missing required structure and missing required output marker remain blocked with existing stop reasons.

`tests/services/test_chapter_orchestrator.py`

- writer blocked `missing_required_output_marker` yields `failure_category=prompt_contract` and `primary_subcategory=missing_required_marker`.
- writer blocked `missing_required_structure` yields `missing_structure`.
- writer blocked `unknown_anchor` yields `unknown_anchor`.
- writer blocked invalid marker issue yields `invalid_marker` while stop reason can remain `llm_contract_violation`.
- programmatic candidate facet audit failure yields `candidate_facet_assertion`.
- forbidden phrase from writer or audit yields `forbidden_phrase`.
- provider timeout remains `llm_timeout` and does not produce prompt-contract subcategory.
- unmapped contract issue yields `code_bug_other` and does not silently pass.
- sanitized diagnostic serialization excludes `accepted_draft.markdown`, prompt fields and raw provider/audit text.

`tests/ui/test_cli.py`

- incomplete `--use-llm` stderr includes `first_failed_subcategory=<value>` when available.
- stderr/stdout do not contain `Authorization`, `Bearer`, API key env names with values, `system_prompt`, `user_prompt`, `draft_markdown`, full draft headings beyond existing summary, or provider response body.
- default deterministic analyze/checklist behavior is unchanged.

## Validation Matrix

Implementation worker must run and record:

| Command | Expected |
|---|---|
| `uv run ruff check .` | PASS |
| targeted pytest for writer/orchestrator/CLI/provider path | PASS |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, coverage threshold unchanged |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, deterministic path exit `0` |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, deterministic path exit `0` |
| isolated missing-config `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | FAIL-CLOSED, exit `1`, stdout empty, provider config error only |
| real provider `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | either PASS full 0-7 report, or FAIL-CLOSED with sanitized first failed subcategory |
| secret scan over new reports and docs artifact | PASS; no API key, Authorization header, full prompt, full draft, full provider response |

The real provider command must be run only by an authorized worker/environment with validated config. It must not be run by this planning worker.

## Real Provider Evidence Matrix

Store evidence under:

`reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/`

Recommended files:

- `controller-real-provider-006597-2024.stdout`
- `controller-real-provider-006597-2024.stderr`
- `controller-real-provider-006597-2024.exitcode`
- `controller-real-provider-006597-2024-diagnostic.json`
- optional `secret-scan.txt` containing only PASS/filtered hit summary, not secrets.

The diagnostic JSON must use this shape or a stricter subset:

```json
{
  "command_label": "real-provider-006597-2024-writer-diagnostic",
  "fund_code": "006597",
  "report_year": 2024,
  "exit_code": 1,
  "stdout_bytes": 0,
  "orchestration_status": "partial",
  "final_assembly_status": "incomplete",
  "first_failed": {
    "chapter_id": 2,
    "phase": "writer_parse",
    "attempt_index": 0,
    "category": "prompt_contract",
    "subcategory": "missing_required_marker"
  },
  "chapter_phase_matrix": [
    {
      "chapter_id": 2,
      "status": "blocked",
      "stop_reason": "llm_contract_violation",
      "failure_category": "prompt_contract",
      "attempt_count": 1,
      "phases": [
        {
          "phase": "writer",
          "attempt_index": 0,
          "primary_subcategory": "missing_required_marker",
          "issue_reason_counts": {"missing_required_output_marker": 3},
          "issue_id_prefix_counts": {"writer:missing_required_output_marker": 3},
          "required_structure_missing_count": 0,
          "required_output_missing_count": 3,
          "unknown_anchor_count": 0,
          "invalid_marker_count": 0,
          "candidate_facet_assertion_count": 0,
          "forbidden_phrase_count": 0,
          "response_length_incomplete_count": 0,
          "response_chars": 2842,
          "max_output_chars": 12000,
          "finish_reason": "stop"
        }
      ]
    }
  ]
}
```

The example is schema guidance only; actual values must come from the rerun. `issue_id_prefix_counts` must never include raw anchor ids, missing reason values, facet text, forbidden phrase text, required output item text or message snippets.

## Safety Boundaries

- Evidence anchors remain fail-closed. Unknown anchors, invalid markers and evidence lines without anchor marker must continue blocking.
- ITEM_RULE deletion remains fail-closed. Diagnostic work must not re-enable deleted sections.
- Candidate facets remain non-asserted unless structured evidence exists. Diagnostic counters may count candidate facet assertion but must not accept it.
- Trading advice and forecast phrases remain blocked.
- E2 source-text confirmation remains deferred; this gate must not pretend to implement Evidence Confirm or weaken E1/E3/L1/C1/C2.
- Missing semantics remain strict; missing data must remain explicit and cannot be rewritten as determinate fact.
- Provider runtime failures remain fail-closed; no deterministic fallback, no partial report.
- The default deterministic `analyze` and `checklist` commands remain current production behavior.

## Pass Criteria

Full pass requires all of the following:

- `uv run ruff check .` passes.
- targeted pytest passes.
- full pytest with coverage threshold passes.
- deterministic analyze/checklist pass.
- missing-config `--use-llm` fails closed with empty stdout.
- real provider `006597 / 2024 --use-llm` exits `0`, produces complete chapters 0-7, final assembly accepted, and secret scan passes.

## Blocked Criteria

If full pass is not achieved, the gate is still acceptable as blocked only if all of the following hold:

- real provider failure remains fail-closed with stdout empty or no accepted report output.
- provider config/auth and provider runtime timeout are not the main blocker, unless the rerun evidence explicitly proves otherwise.
- first failed chapter, phase and attempt are recorded.
- exactly one primary `prompt_contract` subcategory is identified:
  - `missing_structure`
  - `missing_required_marker`
  - `unknown_anchor`
  - `invalid_marker`
  - `candidate_facet_assertion`
  - `forbidden_phrase`
  - `response_length_incomplete`
  - `code_bug_other`
- secondary counters are recorded for transparency without storing raw text.
- next minimal entrance is named and limited to the identified subcategory.
- secret scan passes.

If multiple primary subcategories tie after deterministic precedence, record the precedence winner as primary and the rest as secondary counters. If no counters exist while stop reason is `llm_contract_violation`, classify as `code_bug_other` and route to code diagnostic rather than prompt wording changes.

## Next Minimal Entrance Mapping

| Primary subcategory | Next gate |
|---|---|
| `missing_structure` | `MVP writer structure marker prompt repair gate` |
| `missing_required_marker` | `MVP writer required-output marker repair gate` |
| `unknown_anchor` | `MVP writer anchor contract repair gate` |
| `invalid_marker` | `MVP writer marker syntax repair gate` |
| `candidate_facet_assertion` | `MVP candidate facet assertion repair gate` |
| `forbidden_phrase` | `MVP writer forbidden phrase repair gate` |
| `response_length_incomplete` | `MVP writer output length budget repair gate` |
| `code_bug_other` | `MVP writer diagnostic code-bug fix gate` |

## Completion Report Format

Implementation evidence should report only:

- changed files;
- diagnostic schema fields added;
- validation command results;
- sanitized real provider chapter/phase matrix;
- first failed chapter/category/subcategory or full pass;
- secret scan result;
- next minimal entrance.

Do not include prompt body, draft body, provider response body, raw audit response, env dump or secret-bearing logs.
