# Provider/LLM Chapter 3 Required-output Policy No-live Implementation Review — MiMo

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Required-output Policy No-live Implementation Gate`.

Role: AgentMiMo independent implementation review worker.

Review target:
- Current scoped diff for implementation files
- `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-evidence-20260614.md`

Truth/control consulted:
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/provider-llm-chapter3-required-output-policy-plan-controller-judgment-20260614.md`

No forbidden body/payload/live/source/PDF/FDR/analyze/checklist/readiness/release/PR reads were used.

Release/readiness remains `NOT_READY`. EID single-source/no-fallback unchanged.

## Evidence Reviewed

- `docs/fund-analysis-template-draft.md` — canonical template JSON, ch3.required_output.item_01 policy change
- `tests/fund/template/test_typed_contracts.py` — typed projection test for item 01 render_evidence_gap
- `tests/agent/test_runner.py` — Agent runner positive/negative gap tests, missing-envelope fail-closed
- `tests/services/test_fund_analysis_service_llm.py` — Service positive/negative final assembly tests
- `tests/README.md` — test-surface documentation sync
- `tests/fund/test_evidence_availability.py` — verified unchanged (mapping preserved)
- `docs/reviews/provider-llm-chapter3-required-output-policy-no-live-implementation-evidence-20260614.md` — implementation evidence
- Controller judgment `docs/reviews/provider-llm-chapter3-required-output-policy-plan-controller-judgment-20260614.md`

Validation re-confirmed:
- `uv run pytest tests/agent/test_runner.py tests/services/test_fund_analysis_service_llm.py tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q` → 74 passed
- `uv run ruff check` on touched files → passed
- `git diff --check` → passed

## Findings

No findings. All controller amendments are correctly applied.

## Accepted Points

| Point | Evidence | Status |
|---|---|---|
| Template item 01 changed from `block` to `render_evidence_gap` | `docs/fund-analysis-template-draft.md` diff: `when_evidence_missing` and `missing_evidence_reason` updated | ACCEPT |
| Item 01 `missing_evidence_reason` updated to align with gap rendering | Template diff shows new wording: "只能输出证据缺口，不得进入未经证据支持的基金经理画像判断" | ACCEPT |
| Item id, ordering, other Ch3 policies, chapter ids, must_answer, must_not_cover, preferred_lens preserved | Template diff shows only item 01 fields changed; `test_current_typed_projection_matches_template_json_exact_fields` passes | ACCEPT |
| Typed projection test renamed from `blocks` to `renders_evidence_gap` | `test_typed_contracts.py` diff: old `test_chapter_3_basic_manager_info_missing_behavior_blocks` replaced with `test_chapter_3_basic_manager_info_missing_behavior_renders_evidence_gap`; assertions check `render_evidence_gap` and reason contains `缺少已复核证据` / `只能输出证据缺口` | ACCEPT |
| Missing EvidenceAvailability envelope remains fail-closed as ValueError | `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` unchanged; verified in focused suite | ACCEPT |
| EvidenceAvailability mapping unchanged | `tests/fund/test_evidence_availability.py` — `git diff` shows no changes | ACCEPT |
| Agent runner positive: missing basic manager info with approved gap wording → writer called, Chapter 3 accepted | `test_chapter_3_missing_basic_manager_info_renders_evidence_gap_and_accepts`: writer requests `[3]`, status `accepted`, `final_assembly_readiness.ready=True`, item 01 `action=="render_evidence_gap"` | ACCEPT |
| Agent runner negative: missing basic manager info without approved gap wording → blocked after writer-output validation | `test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer`: status `blocked`, `terminal_state=="blocked_prompt_contract"`, `failure_category=="prompt_contract"`, issue `writer:required_output_gap_missing:ch3.required_output.item_01`, no `required_output_block:ch3.required_output.item_01` | ACCEPT |
| Negative degradation issue classification uses writer-output validation, not old `required_output_block` | Agent runner negative test asserts `writer:required_output_gap_missing:ch3.required_output.item_01` in blocked_reasons and explicitly asserts absence of `required_output_block:ch3.required_output.item_01` | ACCEPT |
| Controller amendment 1: full fake Route C body run shape chosen for Service positive test | `test_analyze_with_llm_accepts_final_assembly_when_ch3_item01_degrades_to_gap`: all 6 body chapters accepted, `assembled_chapter_ids==(0,1,2,3,4,5,6,7)`, `report_markdown is not None` | ACCEPT |
| Controller amendment 2: direct negative Service-level assertion for unsafe Ch3 output | `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`: Chapter 3 `blocked`, final assembly `incomplete`, `report_markdown is None`, `chapter7_readiness_blocked` in issues, `result.report_markdown` raises ValueError | ACCEPT |
| Controller amendment 3: docs search discovery-only | Only `tests/README.md` test-surface lines updated (two lines changing `block` to `render_evidence_gap` and `zero-provider fact-gap 阻断` to `evidence-gap 降级与 unsafe gap wording 阻断`); control docs, root README, design doc, historical review artifacts untouched | ACCEPT |
| Controller amendment 4: missing EvidenceAvailability envelope remains fail-closed | `test_chapter_3_missing_evidence_availability_envelope_remains_value_error` preserved; only reviewed missing manager basic info degrades to visible evidence gap | ACCEPT |
| No overbroad docs/source changes | Template change is exactly item 01 fields; test README is two test-surface description lines; no control docs/design/root README/source policy changed | ACCEPT |
| No readiness overclaim | Evidence doc and implementation explicitly state `NOT_READY`; no release/readiness/PR action | ACCEPT |
| Old hard-block test name removed | `test_chapter_3_missing_basic_manager_info_blocks_before_provider` renamed to `test_chapter_3_missing_basic_manager_info_renders_evidence_gap_and_accepts`; no duplicate near-identical test | ACCEPT |
| Focused regression bundle passes | 74 passed in 0.56s (evidence) / 0.90s (re-confirmed) | ACCEPT |

## Residuals

- No live/provider completion, provider-response classification, content quality, bounded live re-evidence, additional samples, cleanup, PR, release, or readiness proof is provided by this no-live implementation.
- Historical review artifacts still describe prior item 01 hard-block facts as historical evidence-chain records; they were not updated by this implementation gate.
- Release/readiness remains `NOT_READY`.

## Verdict

PASS

The implementation correctly applies the accepted plan and all four controller amendments. The template item 01 policy change is narrow and exact, the typed projection test confirms the new behavior, the Agent runner positive/negative tests cover both approved-gap-acceptance and unsafe-gap-blocking, the missing-envelope fail-closed is preserved, the Service positive test uses the full fake Route C body run shape with chapters `0..7`, and the Service negative test directly asserts unsafe Chapter 3 output keeps final assembly incomplete. No overbroad changes, no readiness overclaim, no forbidden scope violations.
