# Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition

Date: 2026-06-14

Role: disposition worker, not controller

Gate: `Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition Gate`

Release/readiness: `NOT_READY`

## 1. Scope

This artifact classifies the current strongest root-cause category for the Chapter 3 `missing_required_output_marker` / `missing_required_marker` blocker reported by the accepted Chapter 5 post-fix bounded live evidence.

Boundaries observed:

- No source, test, runtime, control-doc, design-doc or README changes.
- No live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR command.
- No raw provider payload, raw prompt body, final report body or chapter body read.
- Safe runtime metadata only from `summary.json` and `chapters/chapter-03.json`.
- EID single-source/no-fallback policy and release/readiness `NOT_READY` preserved.

Worker self-check: current role remains disposition worker; output is this single artifact; next action after writing is stop and report path plus verdict.

## 2. Evidence Reviewed

| Evidence | Classification use |
|---|---|
| `AGENTS.md` | Repo rule truth for source boundary, CHAPTER_CONTRACT intent, EID single-source/no-fallback, role/layer constraints and `NOT_READY` posture. |
| `docs/current-startup-packet.md:22-24`, `docs/current-startup-packet.md:49-55`, `docs/current-startup-packet.md:66-73` | Current gate, accepted checkpoint lineage, no implementation/live/readiness boundary and active control truth. |
| `docs/implementation-control.md:24-38`, `docs/implementation-control.md:44-49`, `docs/implementation-control.md:84-89` | Current guardrails, active gate objective and accepted Chapter 5 live checkpoint. |
| `docs/design.md:154-180`, `docs/design.md:512-522`, `docs/design.md:529-536` | CHAPTER_CONTRACT, typed template, EvidenceAvailability, Route C, Host/Agent and writer/auditor boundary truth. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Accepted live judgment for Chapter 5 accepted and Chapter 3 first failed. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-post-fix-bounded-live-re-evidence-20260614.md` | Live evidence artifact, used only for safe scalar metadata claims already accepted by controller. |
| `reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/summary.json` | Safe metadata: first failed chapter, failure category/subcategory, prompt diagnostics, runtime diagnostics, chapter matrix and final assembly issues. |
| `reports/llm-runs/004393-2025-20260614T031221Z-host_run_68d54160dc204eb/chapters/chapter-03.json` | Safe Chapter 3 metadata: issue ids, terminal status and prompt/runtime diagnostic fields. |
| `fund_agent/fund/chapter_writer.py:664-736`, `fund_agent/fund/chapter_writer.py:916-1045`, `fund_agent/fund/chapter_writer.py:1101-1124`, `fund_agent/fund/chapter_writer.py:1560-1625`, `fund_agent/fund/chapter_writer.py:1759-1878` | No-live repo facts for writer prompt marker contract, typed required-output plan, preflight block behavior, parser marker items and marker/degrade issue generation. |
| `fund_agent/agent/runner.py:1172-1193` | No-live repo fact that Agent runner reads typed required-output items when typed contract is active. |
| `tests/services/test_chapter_orchestrator.py:689-704`, `tests/services/test_fund_analysis_service_llm.py:1288-1306`, `tests/fund/template/test_typed_contracts.py:158-170` | No-live test facts around diagnostic classification, Chapter 3 missing marker behavior and item 01 missing-evidence policy. |

## 3. Accepted Current Facts

### Repo Facts

- `chapter_writer.py` tells the writer to copy an exact marker before each `required_output_items` entry and, on typed path, use `<!-- required_output:<typed item id> -->`.
- `chapter_writer.py` renders typed required-output prompt payload as `plan.marker`, item id/text, availability/action and instruction.
- The parser/audit side checks marker presence for every non-deleted required-output item and emits `missing_required_output_marker` when an exact marker is absent.
- For typed `render_evidence_gap` items, the writer output must contain the required-output marker segment and approved gap phrasing; otherwise `writer:required_output_gap_missing:<item_id>` is emitted with reason `missing_required_output_marker`.
- The Agent runner supplies typed required-output items from the active typed contract when typed contract path is enabled.
- Tests cover writer prompt-contract classification as `prompt_contract` / `missing_required_marker`, Chapter 3 item 01 gap behavior, and final assembly incomplete status when Chapter 3 blocks on missing required output marker.

### Truth-doc Facts

- `docs/design.md` defines canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` as the authored template contract truth source.
- Route C `analyze --use-llm` is explicit opt-in, provider-backed and fail-closed; incomplete LLM result does not fall back to deterministic Markdown.
- Typed path wiring passes typed required-output items, same-source `EvidenceAvailability` and typed audit focus into Fund primitives.
- Chapter writer/auditor primitives are Fund-layer facts; Host remains business-opaque and Service owns provider construction/runtime plan.
- Current repair budget is one regenerate attempt per body chapter and is not product-calibrated.

### Accepted Live Facts

- The accepted post-fix bounded live sample is exact `004393 / 2025` and failed closed with exit `1`.
- `summary.json` records `orchestration_status=partial`, `final_assembly_status=incomplete`, first failed chapter `3`, `status=blocked`, `stop_reason=missing_required_output_marker`, `failure_category=prompt_contract`, `failure_subcategory=missing_required_marker`, `attempt_count=1`.
- Chapter 3 prompt diagnostics are at `phase=writer_parse`, `attempt_index=0`, `finish_reason=stop`, `max_output_chars=12000`, `response_chars=1906`, `required_output_missing_count=2`, `issue_reason_counts.missing_required_output_marker=2`, and issue prefix `writer:required_output_gap_missing=2`.
- Chapter 3 safe issue ids are `writer:required_output_gap_missing:ch3.required_output.item_01` and `writer:required_output_gap_missing:ch3.required_output.item_05`.
- Chapter 3 metadata records `accepted=false`, `accepted_conclusion_present=false`, `accepted_draft_file=null`, `diagnostic_consistency_status=consistent`.
- Runtime diagnostics for the first failed blocker classify operation as writer, provider attempt count as `0`, provider runtime categories as empty, and many provider/runtime scalar fields as null.
- Final assembly is blocked because Chapter 3 is not accepted and lacks accepted draft/conclusion.
- The previous Chapter 5 forbidden-phrase blocker is accepted in this sample; full Route C completion and release/readiness remain unproven.

## 4. Root-cause Classification

Current strongest root-cause class:

```text
LLM_WRITER_OUTPUT_NONCOMPLIANCE_WITH_EXISTING_TYPED_REQUIRED_OUTPUT_GAP_MARKER_CONTRACT
```

Rationale by evidence type:

- Repo fact: the writer prompt and parser already define exact required-output marker behavior for typed items, including required marker segments for `render_evidence_gap` items.
- Repo fact: current code can classify a writer output that omits required marker/gap segments as `missing_required_output_marker` with subcategory `missing_required_marker`.
- Truth-doc fact: typed required-output items and `EvidenceAvailability` are current Route C typed path facts; this is not a future-only contract.
- Accepted live fact: Chapter 3 failed at writer parse with two `writer:required_output_gap_missing` issues for typed item ids `ch3.required_output.item_01` and `ch3.required_output.item_05`.
- Inference: because the failing issue ids are gap-missing typed required-output ids, and because the prompt contract and parser already exist, the strongest current classification is writer output not satisfying existing typed required-output gap marker/phrasing contract.
- Residual: this disposition did not read the raw prompt or draft body, so it does not prove whether the live prompt payload was ergonomically sufficient, whether repair context would have corrected the issue, or whether item 05 has a separate policy/config gap. Those require no-live diagnostic evidence.

This is not currently classified as a source/EID issue, provider availability issue, runtime truncation issue, final assembly bug, or missing template truth-source issue.

## 5. Rejected Overreads

- Do not treat the live runtime artifact as EID/source proof. Manifest/source policy fields from this run are not accepted as source identity evidence.
- Do not infer provider quality or provider availability from this blocker. Safe runtime metadata shows provider attempt count `0` and no provider runtime categories for the first failed Chapter 3 blocker.
- Do not claim full LLM path readiness. Final assembly is incomplete and Chapter 3 is blocked.
- Do not claim Chapter 3 content quality, correctness, factual sufficiency or source-body validity from safe metadata.
- Do not infer raw prompt adequacy or raw LLM response quality without a no-live prompt/draft diagnostic reproduction.
- Do not treat the accepted Chapter 5 live pass as a general Route C pass.
- Do not use this disposition to change repair budget, provider defaults, annual-period LLM route, fallback/source expansion, Docling, score-loop, release/readiness or PR state.

## 6. Disposition Decision

Decision: proceed to a no-live diagnostic evidence gate before any fix planning.

Reason:

- The current strongest category is specific enough to reject source/provider/final-assembly overreads: writer output failed an existing typed required-output gap marker contract.
- It is not yet specific enough for fix planning because the current evidence does not prove which no-live mechanism should be adjusted: prompt wording, repair-context propagation, writer retry trigger, item 05 typed policy, diagnostic mapping, or no code change with accepted residual.
- A no-live diagnostic gate can prove the exact current prompt payload/check list for Chapter 3 typed items, reproduce `writer:required_output_gap_missing` without provider/network/live access, and determine whether repair receives enough context under the existing one-regenerate budget.

## 7. Next Gate Recommendation

Recommended next entry:

```text
Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Gate
```

Minimum diagnostic questions:

- Does the current no-live typed Chapter 3 prompt include exact required-output marker entries for `ch3.required_output.item_01` and `ch3.required_output.item_05`, including availability/action/instruction?
- Does a no-live fake writer response that omits only those gap marker segments reproduce the exact `writer:required_output_gap_missing` ids and `prompt_contract` / `missing_required_marker` classification?
- Does the current repair path receive missing-marker issue ids and required-output item ids clearly enough to make a second attempt possible within existing repair budget?
- Is item 05 configured with the intended missing-evidence behavior, or does it need a separate policy classification before fix planning?

No-live diagnostic gate must not run provider/live/network/PDF/FDR/source/analyze/checklist commands and must preserve `NOT_READY`.

## 8. Residuals

| Residual | Classification | Owner / next handling |
|---|---|---|
| Raw prompt/body not read in this gate. | Evidence limitation | No-live diagnostic evidence may inspect generated prompt fixtures/fake-writer requests if explicitly authorized; live/raw provider payload remains out of scope. |
| Provider behavior for this blocker remains unclassified. | Accepted residual | Keep out of root-cause class unless a future authorized provider diagnostic proves otherwise. |
| `chapter-03.json` runtime scalar fields are sparse/null while prompt diagnostics are populated. | Diagnostic residual | No-live diagnostic gate should distinguish prompt-contract diagnostics from provider runtime diagnostics. |
| Item 05 policy status is not classified here. | Residual | Next no-live gate should identify item 05 missing-evidence behavior and whether it is policy, prompt or output noncompliance. |
| Full Route C completion is unproven. | Readiness blocker | Separate bounded live evidence and readiness gates only after blockers are dispositioned/fixed. |
| Release/readiness remains `NOT_READY`. | Required posture | No release/readiness/PR claim in this gate. |

## 9. Final Verdict

VERDICT: PROCEED_TO_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE
