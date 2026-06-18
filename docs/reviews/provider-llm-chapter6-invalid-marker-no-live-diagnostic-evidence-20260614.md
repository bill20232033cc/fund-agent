# Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence

## 1. Scope

Role: AgentCodex no-live diagnostic evidence worker, not controller.

Gate: `Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Gate`

Target: D1-D5 only. This artifact does not implement a fix, modify source/tests/runtime/prompts/README/design/control docs, run live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands, or change EID source policy.

Release/readiness remains: `NOT_READY`

## 2. Evidence Reviewed

Allowed rule/control inputs:

- `AGENTS.md` instructions provided in the task prompt; applied as execution boundary truth.
- `docs/current-startup-packet.md`: current active gate is this no-live diagnostic evidence gate; checkpoint `6afe67e`; release/readiness remains `NOT_READY`.
- `docs/implementation-control.md`: active gate, standard classification, D1-D5 evidence objective, no implementation/live/provider/source/fallback/readiness/release/PR boundary.
- `docs/design.md`: Route C current facts, exact writer marker contract, explicit opt-in fail-closed LLM route, current Agent body runner boundaries.
- Accepted Chapter 6 disposition plan/judgment/reviews:
  - `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-controller-judgment-20260614.md`
  - `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-20260614.md`
  - `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-review-ds-20260614.md`
  - `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-review-mimo-20260614.md`

Relevant no-live code/tests read:

- `fund_agent/fund/chapter_writer.py`: prompt rendering, exact marker parser, invalid/unknown anchor taxonomy, Chapter 6 bond-risk internal-anchor warning, writer repair-context prompt rendering.
- `fund_agent/services/chapter_orchestrator.py`: writer prompt-contract diagnostic mapping, raw suffix stripping, audit-derived repair context, repair decision flow.
- `fund_agent/agent/runner.py`: Agent writer-block behavior and audit-derived repair retry behavior.
- `fund_agent/agent/tools.py`: writer stop reason to terminal state mapping.
- `fund_agent/agent/repair.py`: Agent repair-context correction mapping.
- `tests/fund/test_chapter_writer.py`: fake writer tests for exact marker syntax, invalid marker, unknown anchor, Chapter 6 bond-risk internal/组级 anchor warning.
- `tests/services/test_chapter_orchestrator.py`: fake orchestration tests for prompt-contract subcategory mapping, sanitized diagnostics, repair context mechanics.
- `tests/agent/test_repair_policy.py`: repair context sanitization mechanics.

Not read:

- Writer/auditor/repair markdown bodies.
- Provider payloads or raw LLM responses.
- PDF/source/cache bodies, source bodies, FDR-loaded documents, final report body.
- `reports/llm-runs/...` safe metadata files were not needed for D1-D5 no-live proof and were not read.

## 3. Commands Run

Read/search/status:

- `sed -n '1,260p' /Users/maomao/.codex/skills/phaseflow/SKILL.md`
- `git status --branch --short`
- `rg -n "Provider/LLM Chapter 6|Invalid-marker|NOT_READY|no-live|current gate|Startup Packet|Route C|Agent runner|marker|anchor" docs/implementation-control.md`
- `rg -n "Provider/LLM Chapter 6|Invalid-marker|NOT_READY|no-live|current gate|Startup Packet|Route C|Agent runner|marker|anchor" docs/current-startup-packet.md docs/design.md`
- `rg -n "Provider/LLM Chapter 6|Invalid-marker|D1|D2|D3|D4|D5|invalid_marker|unknown_anchor|writer:invalid_anchor_marker|repair|marker|anchor|NOT_READY|no-live" docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-controller-judgment-20260614.md docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-20260614.md docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-review-ds-20260614.md docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-review-mimo-20260614.md`
- `rg -n "invalid_anchor_marker|invalid_marker|unknown_anchor|anchor:<anchor_id>|allowed anchor|allowed_anchor|anchor_ids|repair_context|Repair|prompt_contract|invalid marker|marker" fund_agent tests`
- `rg -n "chapter_id.?6|Chapter 6|第 6 章|bond|债券|组级|internal|anchor" fund_agent tests`
- `rg -n "invalid_marker_count|unknown_anchor_count|issue_id_prefix_counts|safe diagnostics|diagnostics|writer:invalid_anchor_marker|raw" fund_agent tests`
- Multiple focused `sed -n` reads over the files listed in Section 2.

No-live deterministic tests/snippets:

- `uv run pytest -q tests/fund/test_chapter_writer.py::test_ch6_prompt_forbids_synthesized_bond_risk_anchor_ids tests/fund/test_chapter_writer.py::test_writer_rejects_invalid_anchor_marker_spacing_or_case tests/fund/test_chapter_writer.py::test_writer_rejects_unknown_anchor_reference tests/fund/test_chapter_writer.py::test_writer_reports_bond_risk_internal_anchor_message tests/services/test_chapter_orchestrator.py::test_writer_prompt_contract_subcategory_mapping tests/services/test_chapter_orchestrator.py::test_writer_diagnostic_prefix_counts_strip_raw_suffixes tests/services/test_chapter_orchestrator.py::test_writer_missing_marker_issues_count_as_invalid_marker_without_raw_suffix`
  - Result: `12 passed in 0.84s`.
- First snippet attempt with wrong import path:
  - Result: failed with `ModuleNotFoundError: No module named 'fund_agent.fund.chapter_fact_provider'`.
  - Evidence value: none; corrected immediately using the actual module.
- Corrected no-live snippet using fake bundle/fake writer:
  - D1 booleans all `True`: exact `<!-- anchor:<anchor_id> -->`, allowed-anchor boundary, no synthesized anchor, Chapter 6 bond internal/组级 prohibition, `允许 anchors`; `allowed_anchor_count=8`.
  - D2 invalid syntax: `stop_reason='llm_contract_violation'`, issue prefix includes `writer:invalid_anchor_marker`.
  - D2 valid unauthorized id: `stop_reason='unknown_anchor'`, issue prefix includes `writer:unknown_anchor`.
  - D3: `failure_subcategory='invalid_marker'`, `invalid_marker_count=1`, prefix counts include `writer:invalid_anchor_marker`.
  - D3 raw suffix leak check: `False` for raw `bad` / `<!-- ANCHOR:bad -->` in serialized prompt-contract diagnostics.
  - D4: `attempt_count=1`, `repair_decision=None`, `second_writer_request_exists=False`.

No live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR command was run.

## 4. D1-D5 Evidence Table

| ID | Question | Evidence | Finding |
| --- | --- | --- | --- |
| D1 | Chapter 6 prompt contract rendering: exact anchor marker syntax, allowed-anchor boundary language, and Chapter 6 bond-risk internal/组级 anchor prohibition. | `chapter_writer.py` renders protocol text: evidence assertions may only use `<!-- anchor:<anchor_id> -->`; `required_anchor_ids` is an allowed set, not a required full-use list; synthesized ids from `fact_id`, `source_field_id`, `source_field_name` or fact value are forbidden. `_bond_risk_anchor_contract_prompt()` adds: `bond_risk_evidence 内部/组级 anchors 不是 ChapterEvidenceAnchor`, not to be written as `<!-- anchor:... -->`, only ids in `允许 anchors` may be cited. Focused test `test_ch6_prompt_forbids_synthesized_bond_risk_anchor_ids` passed. Corrected snippet confirmed all D1 booleans `True` with `allowed_anchor_count=8`. | Proven no-live. Current Chapter 6 rendered prompt already exposes exact syntax, allowed-anchor boundary, no synthesized ids, and bond-risk internal/组级 anchor prohibition. |
| D2 | Validator taxonomy: malformed anchor comments route to `invalid_marker`; valid syntax with unauthorized ids routes to `unknown_anchor`. | `_invalid_marker_issues()` scans HTML comments and emits `writer:invalid_anchor_marker:<offset>` with reason `llm_contract_violation` when payload contains anchor but does not fullmatch exact `_ANCHOR_MARKER_RE`. `_parse_anchor_markers()` separately processes valid `<!-- anchor:<id> -->` markers and emits `_unknown_anchor_issue()` when id is not in the allowed set. Focused tests passed: invalid anchor marker syntax, unknown anchor reference, bond-risk internal anchor message, and orchestrator subcategory mapping. Corrected snippet showed malformed `<!-- ANCHOR:... -->` produced `stop_reason='llm_contract_violation'` with `writer:invalid_anchor_marker`; valid unauthorized `<!-- anchor:unknown-anchor -->` produced `stop_reason='unknown_anchor'` with `writer:unknown_anchor`. | Proven no-live. Parser taxonomy distinguishes malformed marker syntax from syntactically valid but unauthorized anchor ids. |
| D3 | Diagnostic payload mapping: `writer:invalid_anchor_marker` contributes to `invalid_marker_count`; raw malformed suffixes are not leaked in safe diagnostics. | `_writer_prompt_contract_diagnostic()` computes `invalid_marker_count` from `_INVALID_MARKER_PREFIXES`; `_writer_issue_id_prefix_counts()` strips writer issue ids to the first two components, removing raw offsets/ids/suffixes. Focused tests passed: prompt-contract subcategory mapping, prefix stripping, missing marker invalid-marker no raw suffix, sanitized payload excludes raw prompt/draft/provider fields. Corrected snippet showed `failure_subcategory='invalid_marker'`, `invalid_marker_count=1`, `issue_id_prefix_counts` includes `writer:invalid_anchor_marker`, and serialized diagnostics did not contain raw `bad` or `<!-- ANCHOR:bad -->`. | Proven no-live. Diagnostics count invalid anchor markers and retain only safe prefixes/counts, not malformed raw marker suffixes. |
| D4 | Repair-context specificity for `invalid_marker`: whether no-live repair context instructs exact marker syntax clearly enough. | Current flow shows writer parser block is terminal before audit/repair. `agent/runner.py` returns immediately when `writer_result.status == "blocked"`; Service orchestrator builds repair context only from `ChapterAuditResult` via `_repair_context_from_audit()`, after a draft reaches audit and `decision.action == "regenerate"`. Corrected snippet for `llm_contract_violation` showed `attempt_count=1`, `repair_decision=None`, `second_writer_request_exists=False`. Existing repair context renderer has a generic line: do not bypass required_output/anchor/missing markers; known audit correction mapping for anchor issues says only "只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor", without exact `<!-- anchor:<anchor_id> -->` syntax except in Chapter 2 L1-special guidance. | Proven no-live as a gap. For `invalid_marker`, current runner does not generate a repair attempt/context at all. If a later fix wants repair-context correction for invalid marker recurrence, it must add a narrow no-live plan; current exact syntax clarity lives in the initial prompt, not an invalid-marker repair context. |
| D5 | Boundary preservation. | Commands were limited to `rg`, `sed`, `git status --branch --short`, focused `uv run pytest`, and fake-input `uv run python -c` snippets. No source/test/runtime/prompt/README/design/control files were modified. No reports safe metadata was read. No body reads or live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands were run. | Preserved. EID remains single-source/no-fallback; Eastmoney/fund-company/CNINFO/fallback routes remain out of scope; release/readiness remains `NOT_READY`. |

## 5. Root-cause/Fix-surface Implication

The no-live evidence supports the accepted disposition category: strongest current category remains LLM output-format noncompliance with an existing exact anchor marker contract.

The validator/parser is not the strongest fix surface: malformed anchor comments and valid unauthorized ids are separated correctly, and diagnostics are safely mapped.

The prompt already contains the exact marker syntax and Chapter 6 bond-risk internal/组级 anchor prohibition. The remaining fix-surface question is therefore narrow: whether the initial Chapter 6 output-format instruction is salient enough for the writer, or whether writer-block handling should add a no-live retry/repair-context path for `invalid_marker`. Because writer parser blocks terminate before audit/repair today, that decision requires fix planning, not direct implementation from this evidence artifact.

## 6. Residuals and Rejected Alternatives

Residuals:

- This artifact did not read the actual malformed live marker strings or provider output body by design.
- This artifact did not read writer/auditor/repair markdown bodies or final report body.
- This artifact did not prove that a prompt wording change will fix the provider sample; it only proves the no-live mechanics and the current gap.
- D4 leaves an accepted fix-surface residual: current `invalid_marker` blocks before repair context, so exact repair-context instruction for invalid-marker recurrence is absent.

Rejected alternatives:

- Additional bounded live evidence: rejected for this gate. The missing evidence was no-live mechanics/fix-surface isolation, not another provider occurrence.
- Parser relaxation: rejected for this gate. Current contract is exact marker syntax and validator taxonomy is behaving as designed.
- Source/fallback investigation: rejected. The blocker is writer prompt-contract marker syntax, not document/source availability.
- Readiness/release/PR movement: rejected. This artifact is evidence-only and preserves `NOT_READY`.

## 7. Next Gate Recommendation

Recommend: `Provider/LLM Chapter 6 Invalid-marker Narrow No-live Fix Planning Gate`.

Planning constraints:

- No direct implementation from this artifact.
- Keep fix scope to prompt/repair-output-format guardrails for Chapter 6 invalid anchor marker behavior.
- Preserve exact marker contract unless a separate product/contract gate explicitly accepts a syntax relaxation.
- Preserve EID single-source/no-fallback, provider defaults, repair budget, annual-period LLM route, Docling/source policy and release/readiness state.
- Required planning decision: choose whether to strengthen initial Chapter 6 writer prompt salience only, add a writer-block repair/retry path for `invalid_marker`, or both, with fake-input red tests before implementation.

## 8. Final Verdict

VERDICT: PROCEED_TO_NO_LIVE_FIX_PLANNING_GATE_NOT_READY
