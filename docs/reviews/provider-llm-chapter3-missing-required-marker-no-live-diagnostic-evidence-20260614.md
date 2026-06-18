# Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence

Date: 2026-06-14

Role: no-live diagnostic evidence worker, not controller

Gate: `Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Gate`

Release/readiness: `NOT_READY`

## 1. Scope

This artifact answers the assigned no-live diagnostic questions for the Chapter 3 `missing_required_output_marker` / `prompt_contract` / `missing_required_marker` blocker.

Boundaries observed:

- No source, test, runtime behavior, control-doc, design-doc, README, provider default, repair-budget, annual-period LLM route, Docling, fallback, readiness, release, PR, stage, commit or push change.
- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command.
- No raw provider payload, final report body or chapter draft body read.
- Runtime artifact use was limited to safe scalar metadata from `summary.json` and `chapters/chapter-03.json`.
- EID single-source/no-fallback and release/readiness `NOT_READY` preserved.

Worker self-check:

- Current role remained no-live diagnostic evidence worker; not controller.
- Only this artifact was written.
- Existing dirty/untracked workspace state was not modified.
- Evidence is sufficient for a no-live fix planning gate, not for implementation or readiness.

## 2. Evidence Commands

Read/control commands:

- `sed -n '1,260p' AGENTS.md`
- `sed -n '261,520p' AGENTS.md`
- `sed -n '1,260p' docs/current-startup-packet.md`
- `sed -n '1,320p' docs/implementation-control.md`
- `sed -n '1,320p' docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-controller-judgment-20260614.md`
- `sed -n '1,360p' docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-20260614.md`

Safe metadata commands:

- `jq 'keys' reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/summary.json`
- `jq 'keys' reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/chapters/chapter-03.json`
- `jq '{schema_version, fund_code, report_year, orchestration_status, final_assembly_status, first_failed, prompt_contract_diagnostics, runtime_diagnostics, chapter3_matrix: (.chapter_matrix[] | select(.chapter_id==3))}' reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/summary.json`
- `jq '{chapter_id,status,accepted,accepted_conclusion_present,accepted_draft_file,stop_reason,failure_category,failure_subcategory,terminal_stop_reason,terminal_failure_category,terminal_issue_class,terminal_repair_attempt_index,terminal_runtime_diagnostic_present,terminal_runtime_operation,issues_type:(.issues|type), issues, prompt: .chapter_prompt_contract_diagnostics, runtime: .chapter_runtime_diagnostics, attempt_count: (.attempts|length), attempt_summaries: [.attempts[] | {attempt_index, status, stop_reason, failure_category, failure_subcategory, writer_status, audit_status, repair_decision}]}' reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/chapters/chapter-03.json`

Code/test evidence commands:

- `rg -n "ch3\\.required_output\\.item_01|ch3\\.required_output\\.item_05|required_output_gap_missing|missing_required_marker|prompt_contract|render_evidence_gap|missing_required_output_marker" fund_agent tests docs/fund-analysis-template-draft.md`
- `sed -n '650,700p' docs/fund-analysis-template-draft.md`
- `sed -n '1,120p' fund_agent/fund/evidence_availability.py`
- `sed -n '232,292p' fund_agent/fund/evidence_availability.py`
- `sed -n '916,1075p' fund_agent/fund/chapter_writer.py`
- `sed -n '1540,1640p' fund_agent/fund/chapter_writer.py`
- `sed -n '1750,1888p' fund_agent/fund/chapter_writer.py`
- `sed -n '300,420p' fund_agent/agent/runner.py`
- `sed -n '658,705p' fund_agent/agent/runner.py`
- `sed -n '1492,1520p' fund_agent/fund/chapter_writer.py`
- `sed -n '151,210p' fund_agent/agent/repair.py`
- `sed -n '1840,1960p' fund_agent/services/chapter_orchestrator.py`
- `sed -n '480,560p' tests/fund/test_chapter_writer.py`
- `sed -n '330,390p' tests/agent/test_runner.py`
- `sed -n '910,940p' tests/agent/test_runner.py`
- `sed -n '1820,1865p' tests/services/test_chapter_orchestrator.py`
- `sed -n '1288,1306p' tests/services/test_fund_analysis_service_llm.py`
- `sed -n '100,145p' tests/fund/test_evidence_availability.py`
- `rg -n "ch3\\.required_output\\.item_01|ch3\\.required_output\\.item_05|when_evidence_missing|missing_evidence_reason|风格稳定性判断|基金经理基本信息" docs/fund-analysis-template-draft.md tests/fund/template/test_typed_contracts.py tests/fund/test_chapter_writer.py tests/fund/test_evidence_availability.py tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py`
- `rg -n "def _prompt_required_output_payload|def _prompt_required_output_plan_item|def _prompt_required_output_marker_items|availability=|action=|instruction=|def _required_output_degrade_issues|writer:required_output_gap_missing|def _required_output_segment_contains|def _repair_context_prompt" fund_agent/fund/chapter_writer.py`
- `rg -n "def _should_retry_writer_invalid_marker|chapter_id != 6|writer_result.stop_reason !=|writer:invalid_anchor_marker|def repair_context_from_writer_invalid_marker|previous_issue_ids|required_corrections|missing_required_output_marker|missing_required_marker|prompt_contract" fund_agent/agent/runner.py fund_agent/agent/repair.py fund_agent/services/chapter_orchestrator.py tests/agent/test_runner.py tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py`

Validation commands:

- `uv run pytest tests/fund/test_chapter_writer.py::test_writer_prompt_contains_typed_required_output_ids_not_freeform_fallbacks tests/agent/test_runner.py::test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer tests/agent/test_runner.py::test_chapter_6_invalid_anchor_marker_retries_once_and_accepts tests/services/test_chapter_orchestrator.py::test_regenerate_request_contains_previous_failure_context tests/fund/template/test_typed_contracts.py::test_chapter_3_basic_manager_info_missing_behavior_renders_evidence_gap tests/fund/test_evidence_availability.py::test_ch3_actual_behavior_requirement_is_unreviewed_when_turnover_or_style_evidence_absent tests/fund/test_evidence_availability.py::test_ch3_basic_manager_info_required_output_uses_basic_identity_availability`
  - Result: `7 passed in 0.48s`.
- `git diff --check`
  - Result: passed with no output before writing this artifact.

## 3. Facts Proven

1. Current typed Chapter 3 prompt construction includes exact marker entries and item fields.
   - Template truth: `docs/fund-analysis-template-draft.md:665-668` defines `ch3.required_output.item_01`, text `基金经理基本信息`, `when_evidence_missing=render_evidence_gap`, and its item-specific missing-evidence reason.
   - Template truth: `docs/fund-analysis-template-draft.md:689-692` defines `ch3.required_output.item_05`, text `风格稳定性判断`, `when_evidence_missing=render_evidence_gap`, and its separate style/behavior missing-evidence reason.
   - Writer prompt construction: `fund_agent/fund/chapter_writer.py:1560-1600` renders each typed plan item as exact marker, `item_id | text`, `availability=...; action=...`, and `instruction=...`.
   - Writer marker list: `fund_agent/fund/chapter_writer.py:1605-1618` uses stable item ids for parser-required marker items when typed plan exists.
   - Existing no-live test: `tests/fund/test_chapter_writer.py:520-530` proves item 05 prompt contains `<!-- required_output:ch3.required_output.item_05 -->`, `ch3.required_output.item_05 | 风格稳定性判断`, `action=render_evidence_gap`, and does not fall back to freeform `<!-- required_output:风格稳定性判断 -->`.

2. Existing no-live fake writer reproduction proves the current class for missing approved gap wording.
   - Parser/degrade code: `fund_agent/fund/chapter_writer.py:1787-1820` emits `writer:required_output_gap_missing:<item_id>` with reason `missing_required_output_marker` when a `render_evidence_gap` item segment lacks approved gap wording.
   - Segment check: `fund_agent/fund/chapter_writer.py:1837-1858` requires the phrase to appear after the exact typed marker and before the next required-output marker.
   - Existing Agent fake writer test: `tests/agent/test_runner.py:348-379` builds a Chapter 3 fake writer output that keeps the item 01 marker but replaces the gap wording with unsafe positive wording; the run blocks with terminal state `blocked_prompt_contract`, stop reason `missing_required_output_marker`, failure category `prompt_contract`, subcategory `missing_required_marker`, and issue `writer:required_output_gap_missing:ch3.required_output.item_01`.
   - Existing Service final-assembly test: `tests/services/test_fund_analysis_service_llm.py:1295-1303` independently confirms Chapter 3 blocks as `missing_required_output_marker` / `prompt_contract` / `missing_required_marker`, includes `writer:required_output_gap_missing:ch3.required_output.item_01`, and does not emit `required_output_block`.
   - Limitation: the existing fake writer reproduction directly covers item 01. It does not contain a paired fake-writer assertion for item 05, but the parser/degrade loop is item-id generic and item 05 prompt/policy is directly tested.

3. Current repair path does not receive `required_output_gap_missing` issue ids for correction because writer parse failure stops before repair for this class.
   - Agent runner writer-block branch returns a blocked `ChapterTask` after appending the writer attempt unless `_should_retry_writer_invalid_marker(...)` is true: `fund_agent/agent/runner.py:360-415`.
   - `_should_retry_writer_invalid_marker()` is explicitly limited to Chapter 6, writer status `blocked`, stop reason `llm_contract_violation`, positive remaining budget, and `writer:invalid_anchor_marker` issue ids: `fund_agent/agent/runner.py:658-688`.
   - Therefore Chapter 3 `writer:required_output_gap_missing:*` / `missing_required_output_marker` does not enter the writer-block retry path under current no-live code.
   - Repair context rendering itself is clear when supplied: `fund_agent/fund/chapter_writer.py:1492-1514` renders attempt index, previous issue ids, previous messages and required corrections into the prompt.
   - Audit repair context is clear when an audit failure reaches repair: `fund_agent/agent/repair.py:151-176` and `fund_agent/services/chapter_orchestrator.py:1928-1952` carry issue ids, sanitized messages and deterministic corrections.
   - Existing no-live test proves audit regenerate request contains previous required-output failure context: `tests/services/test_chapter_orchestrator.py:1834-1859`.
   - Existing no-live test proves writer-block retry exists for Chapter 6 invalid anchor only: `tests/agent/test_runner.py:541-574`.

4. Prompt-contract diagnostics must be separated from provider runtime diagnostics.
   - Accepted disposition already records Chapter 3 prompt diagnostic facts: `phase=writer_parse`, `finish_reason=stop`, `response_chars=1906`, `max_output_chars=12000`, `required_output_missing_count=2`: `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-controller-judgment-20260614.md:40-44`.
   - Safe `summary.json` metadata confirms first failed Chapter 3 has `attempt_count=1`, `failure_category=prompt_contract`, `failure_subcategory=missing_required_marker`, and prompt diagnostics with `writer:required_output_gap_missing=2`, `required_output_missing_count=2`, `response_chars=1906`, `max_output_chars=12000`.
   - Safe `chapter-03.json` metadata confirms issues are exactly:
     - `3:missing_required_output_marker:writer:required_output_gap_missing:ch3.required_output.item_01`
     - `3:missing_required_output_marker:writer:required_output_gap_missing:ch3.required_output.item_05`
   - Safe `chapter-03.json` metadata also confirms `attempt_count=1`, writer attempt `writer_status=blocked`, `audit_status=null`, `repair_decision=null`, `terminal_runtime_diagnostic_present=false`, `terminal_runtime_operation=null`.
   - Runtime diagnostic layer for the same blocker is sparse/null: operation is `writer`, `provider_attempt_index=null`, `provider_max_attempts=null`, `provider_runtime_category=null`, `finish_reason=null`, `max_output_chars=null`, `response_chars=null`, prompt-size fields null, and summary-level `provider_attempt_count=0`.
   - Diagnostic rule: use prompt-contract diagnostics for marker/gap contract classification; use provider runtime diagnostics only to state that provider-runtime evidence is absent/sparse for this blocker. Do not infer provider quality, availability or truncation from null runtime fields.
   - Attempt-count mismatch handling: summary/chapter matrix show Chapter 3 `attempt_count=1`; prompt diagnostic has attempt index `0`; runtime first-failed has `repair_attempt_index=0`; chapter metadata has `terminal_repair_attempt_index=null` and no repair decision. This is not evidence of an executed repair attempt. It means initial writer attempt index 0 failed and no repair was scheduled for this writer-parse class.

5. Item 05 is configured as `render_evidence_gap`, and its policy is separate from item 01.
   - Item 01 template text/reason is manager basic info specific: `docs/fund-analysis-template-draft.md:665-668`.
   - Item 05 template text/reason is style-stability/actual-behavior specific: `docs/fund-analysis-template-draft.md:689-692`.
   - Evidence availability type surface includes both ids as distinct `EvidenceRequirementId` members: `fund_agent/fund/evidence_availability.py:53-58`.
   - Item 01 maps to `structured.basic_identity` and `structured.portfolio_managers`: `fund_agent/fund/evidence_availability.py:247-252`; no-live test confirms those source field ids and fact ids: `tests/fund/test_evidence_availability.py:121-143`.
   - Item 05 belongs to `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` with item 03/04 and depends on turnover, holdings snapshot and synthetic cross-period style evidence: `fund_agent/fund/evidence_availability.py:279-287`; no-live test confirms item 05 is `unreviewed` when actual-behavior/style evidence is absent and that source fields include turnover, holdings and synthetic cross-period comparison: `tests/fund/test_evidence_availability.py:92-114`.

## 4. Diagnostic Question Matrix

| Question | Answer | Direct evidence |
|---|---|---|
| 1. Does no-live typed Chapter 3 prompt construction include exact marker entries, availability/action and instructions for item 01 and item 05? | Yes. The generic typed prompt renderer emits marker, item id/text, availability/action and instruction for every typed required-output plan item. Item 05 is directly tested in the prompt. Item 01 has template/policy and availability tests, and uses the same renderer. | `chapter_writer.py:1560-1600`; `chapter_writer.py:1605-1618`; `tests/fund/test_chapter_writer.py:520-530`; `tests/fund/template/test_typed_contracts.py:163-169`; `tests/fund/test_evidence_availability.py:121-143`. |
| 2. Does an existing no-live fake writer response reproduce `writer:required_output_gap_missing` and `prompt_contract` / `missing_required_marker`? | Yes for item 01. A fake writer keeping the marker but omitting approved evidence-gap wording blocks after writer parse with the expected category/subcategory and issue id. Existing tests do not directly reproduce item 05, but parser/degrade logic is generic and item 05 prompt/policy is tested. | `tests/agent/test_runner.py:348-379`; `tests/services/test_fund_analysis_service_llm.py:1295-1303`; `chapter_writer.py:1787-1820`. |
| 3. Does current repair path receive missing-marker issue ids and item ids clearly enough to attempt correction, or does writer-parse failure stop before repair? | Writer-parse failure stops before repair for this class. Repair context is clear when invoked, but current writer-block retry is limited to Chapter 6 invalid anchor markers, not Chapter 3 required-output gap/missing marker issues. | `fund_agent/agent/runner.py:360-415`; `fund_agent/agent/runner.py:658-688`; `fund_agent/fund/chapter_writer.py:1492-1514`; `tests/services/test_chapter_orchestrator.py:1834-1859`; `tests/agent/test_runner.py:541-574`. |
| 4. How should prompt-contract diagnostics be separated from provider runtime diagnostics? | Prompt-contract diagnostics are authoritative for this blocker; provider runtime diagnostics are sparse/null and support only a non-provider classification. Summary/chapter attempt fields should be read as one initial writer attempt and no scheduled repair, not as provider attempt evidence. | Safe `summary.json` and `chapter-03.json` jq outputs; disposition controller judgment lines 40-44 and 81. |
| 5. Is item 05 configured as `render_evidence_gap`, and is its policy separate from item 01? | Yes. Both are `render_evidence_gap`, but item 01 is manager basic info with basic identity/portfolio manager availability; item 05 is style stability with actual-behavior/cross-period evidence availability. | `docs/fund-analysis-template-draft.md:665-668`, `689-692`; `fund_agent/fund/evidence_availability.py:247-252`, `279-287`; `tests/fund/test_evidence_availability.py:92-114`, `121-143`. |

## 5. Root-cause Refinement

Refined current root cause:

```text
WRITER_PARSE_REQUIRED_OUTPUT_GAP_MARKER_NONCOMPLIANCE_STOPS_BEFORE_REPAIR
```

Direct basis:

- Prompt and typed policy for both affected items exist in current no-live code.
- The parser/degrade path can produce `writer:required_output_gap_missing:<item_id>` for unsafe `render_evidence_gap` output.
- Existing fake writer reproduction proves the classification for item 01.
- Live safe scalar metadata identifies both item 01 and item 05 as the Chapter 3 issues.
- Current writer-block retry path is not wired for `missing_required_output_marker` / `writer:required_output_gap_missing` and therefore does not pass the item ids into repair context.

Rejected refinements:

- Not a source/EID/FDR/fallback root cause. No source command or body evidence was used or needed.
- Not a provider availability/quality root cause. Provider attempt count is `0` and runtime provider fields are null/sparse for this blocker.
- Not a runtime truncation root cause. Prompt-contract layer records `finish_reason=stop`, `response_chars=1906`, `max_output_chars=12000`.
- Not a final assembly root cause. Final assembly is incomplete because Chapter 3 was not accepted.
- Not an item 05 missing policy configuration root cause. Item 05 is already `render_evidence_gap` and separately mapped.

## 6. Residuals

| Residual | Classification | Owner / next handling |
|---|---|---|
| Existing fake writer reproduction directly covers item 01, not item 05. | Nonblocking diagnostic residual | Fix planning may require adding a narrow no-live red test that reproduces item 05 or both item ids before implementation. |
| Current repair context is proven clear only when audit repair or Ch6 invalid-anchor writer retry is invoked. | Root-cause input | Next no-live fix planning should decide whether to add a Chapter 3 required-output writer-block retry using existing budget and repair context shape. |
| Runtime diagnostics are sparse/null for this blocker. | Diagnostic limitation | Keep provider runtime classification out of root cause unless a future authorized provider diagnostic proves otherwise. |
| Full Route C completion remains unproven. | Readiness blocker | Separate bounded live evidence and readiness gates only after reviewed no-live fix planning/implementation and authorized live re-evidence. |
| Release/readiness remains `NOT_READY`. | Required posture | No release/readiness/PR claim in this gate. |

## 7. Next Gate Recommendation

Proceed to:

```text
Provider/LLM Chapter 3 Missing-required-marker No-live Fix Planning Gate
```

Planning constraints for the next gate:

- No direct implementation from this evidence artifact.
- Preserve current repair budget; any retry must consume the existing content repair budget like the Chapter 6 writer-block retry.
- Keep the fix narrow to Chapter 3 required-output gap/missing marker writer-block handling unless planning evidence proves a smaller or safer target.
- Include red-test-first no-live validation for item 05 or for both `ch3.required_output.item_01` and `ch3.required_output.item_05`.
- Preserve prompt-contract/provider-runtime diagnostic separation.
- Preserve EID single-source/no-fallback and `NOT_READY`.

## 8. Final Verdict

VERDICT: READY_FOR_NO_LIVE_FIX_PLANNING_GATE
