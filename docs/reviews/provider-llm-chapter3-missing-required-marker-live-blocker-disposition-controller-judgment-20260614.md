# Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition Controller Judgment

Date: 2026-06-14

Role: AgentController

Gate: `Provider/LLM Chapter 3 Missing-required-marker Live-blocker Disposition Gate`

Final verdict: `ACCEPT_DISPOSITION_READY_FOR_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY`

Release/readiness: `NOT_READY`

## 1. Scope

This judgment accepts or rejects the disposition artifact for the Chapter 3 blocker discovered by the accepted Chapter 5 post-fix bounded live evidence checkpoint `49129b2`.

This gate was disposition-only. It did not authorize source/test/runtime changes, control/design/README changes, live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands, source policy changes, provider default changes, repair-budget changes, annual-period LLM route work, Docling work, or fallback expansion.

## 2. Evidence Reviewed

| Evidence | Role |
|---|---|
| `AGENTS.md` | Repo rule truth, source boundary, gate classification and `NOT_READY` posture. |
| `docs/current-startup-packet.md` | Current active gate, accepted checkpoint lineage and startup truth. |
| `docs/implementation-control.md` | Control truth and active gate objective. |
| `docs/design.md` | Route C, typed template, EvidenceAvailability and Host/Agent boundary truth. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md` | Accepted upstream live judgment. |
| `docs/reviews/provider-llm-chapter5-forbidden-phrase-post-fix-bounded-live-re-evidence-20260614.md` | Accepted live evidence input, safe scalar metadata only. |
| `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-20260614.md` | Disposition artifact under review. |
| `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-review-ds-20260614.md` | DS independent review, verdict `PASS`. |
| `docs/reviews/provider-llm-chapter3-missing-required-marker-live-blocker-disposition-review-mimo-20260614.md` | MiMo independent review, verdict `PASS`. |

No raw provider payload, raw prompt body, final report body, chapter draft body, source/PDF/cache body or additional live command was used for this judgment.

## 3. Accepted Current Facts

| Fact | Controller judgment |
|---|---|
| Chapter 5 is accepted in the latest bounded live evidence, and Chapter 3 is the first failed chapter. | Accepted from upstream controller judgment. |
| Chapter 3 fails as `missing_required_output_marker` / `prompt_contract` / `missing_required_marker`. | Accepted from safe runtime metadata and upstream judgment. |
| Chapter 3 safe issues are `writer:required_output_gap_missing:ch3.required_output.item_01` and `writer:required_output_gap_missing:ch3.required_output.item_05`. | Accepted. |
| Chapter 3 prompt diagnostics show `phase=writer_parse`, `finish_reason=stop`, `response_chars=1906`, `max_output_chars=12000`, `required_output_missing_count=2`. | Accepted. |
| Chapter 3 provider/runtime diagnostics remain sparse/null and must not be used as provider quality or provider availability proof. | Accepted residual. |
| Current code already has typed required-output marker/gap validation paths that produce `writer:required_output_gap_missing` for unsafe `render_evidence_gap` output. | Accepted repo fact. |
| This runtime artifact is not EID/source proof. | Accepted evidence limitation. |
| Full Route C completion and release/readiness remain unproven. | Accepted residual; `NOT_READY` preserved. |

## 4. Root-cause Classification

Accepted strongest current classification:

```text
LLM_WRITER_OUTPUT_NONCOMPLIANCE_WITH_EXISTING_TYPED_REQUIRED_OUTPUT_GAP_MARKER_CONTRACT
```

This is accepted as a disposition-level classification, not as a final fix diagnosis. The direct basis is:

- repo fact: typed required-output items are rendered as exact marker requirements;
- repo fact: `render_evidence_gap` output must include the item marker segment and approved gap wording;
- accepted live fact: Chapter 3 failed in `writer_parse` with two `writer:required_output_gap_missing` issues;
- accepted live fact: output was not empty, not truncated by the configured `max_output_chars`, and not classified as provider runtime failure.

Rejected classifications for this gate:

| Candidate | Decision | Rationale |
|---|---|---|
| Source/EID source failure | REJECT | The failure is writer output validation; this runtime artifact is not source identity proof. |
| Provider availability or provider quality failure | REJECT | Safe metadata does not support provider classification for the blocker. |
| Runtime truncation | REJECT | Prompt diagnostic records `finish_reason=stop`, `response_chars=1906`, `max_output_chars=12000`. |
| Final assembly bug | REJECT | Final assembly is incomplete because Chapter 3 is not accepted. |
| Immediate code fix plan | DEFER | The evidence has not yet classified prompt ergonomics, repair propagation, parser sensitivity or item 05 policy details. |

## 5. Reviewer Findings Disposition

| Finding | Source | Disposition | Controller rationale |
|---|---|---|---|
| Disposition separates repo fact, truth-doc fact, accepted live fact, inference and residual. | DS, MiMo | ACCEPT | Both reviews verified the separation and found no blocking overclaim. |
| Root-cause classification is supported by safe metadata and no-live code evidence. | DS, MiMo | ACCEPT | Direct evidence supports writer output noncompliance with existing typed gap-marker contract. |
| Next gate should be no-live diagnostic evidence before fix planning. | DS, MiMo | ACCEPT | Current evidence is specific enough to reject source/provider/readiness overreads, but not enough to choose a fix. |
| Summary/chapter attempt-count mismatch is not recorded strongly enough in the disposition artifact. | DS F1, MiMo 01 | ACCEPT_AS_NONBLOCKING_DIAGNOSTIC_RESIDUAL | Next diagnostic evidence gate must carry this residual. It does not change disposition verdict. |
| Provider-attempt/runtime-null fields versus `writer_response_chars=1906` diagnostic layering should be clearer. | DS F2, MiMo 02 | ACCEPT_AS_NONBLOCKING_DIAGNOSTIC_RESIDUAL | Next diagnostic evidence gate must explicitly distinguish prompt-contract diagnostics from provider runtime diagnostics. |
| Parser sensitivity and item 05 policy status need further proof. | MiMo adversarial pass, DS open questions | ACCEPT_AS_NEXT_GATE_INPUT | These are exactly no-live diagnostic questions, not disposition blockers. |

## 6. Accepted / Rejected / Residual Table

| Item | Decision | Basis | Next handling |
|---|---|---|---|
| Disposition artifact | ACCEPT | DS PASS, MiMo PASS, controller review | Local accepted checkpoint |
| Current root-cause class | ACCEPT_WITH_RESIDUALS | Safe metadata plus code path support writer-output contract noncompliance | No-live diagnostic evidence |
| Direct no-live fix planning | REJECT_FOR_NOW | Missing no-live evidence on prompt payload, fake response reproduction, repair context and item 05 details | Defer until diagnostic evidence accepted |
| Additional live evidence | REJECT_FOR_CURRENT_NEXT_GATE | No-live evidence can answer the immediate classification questions without provider/network | Separate bounded live gate only after reviewed authorization |
| Provider/source/EID/readiness claims | REJECT | Not proven by this artifact | Preserve current policy and `NOT_READY` |
| Repair budget/default/provider route changes | REJECT | Out of scope | Future reviewed gates only |

## 7. Next Gate Recommendation

Proceed to:

```text
Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Gate
```

Minimum required questions:

1. Does current no-live typed Chapter 3 prompt construction include exact marker entries, availability/action and instructions for `ch3.required_output.item_01` and `ch3.required_output.item_05`?
2. Does a fake writer response that omits or malforms only those gap marker segments reproduce the exact `writer:required_output_gap_missing` issue ids and `prompt_contract` / `missing_required_marker` classification?
3. Does the current repair path receive missing-marker issue ids and item ids clearly enough to attempt correction within the existing one-regenerate budget?
4. Does the diagnostic evidence explicitly separate prompt-contract diagnostics from provider runtime diagnostics, including the summary/chapter attempt-count mismatch and sparse/null runtime fields?

The next gate must remain no-live and must not change source/test/runtime behavior unless a later implementation gate is accepted.

## 8. Control-doc Update Recommendation

After checkpointing this judgment, update:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Record:

- accepted disposition checkpoint;
- next entry point as `Provider/LLM Chapter 3 Missing-required-marker No-live Diagnostic Evidence Gate`;
- release/readiness remains `NOT_READY`;
- EID single-source/no-fallback remains unchanged;
- additional live/provider evidence, repair-budget calibration, annual-period LLM route, Docling and PR/release remain deferred.

## 9. Final Verdict

```text
ACCEPT_DISPOSITION_READY_FOR_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY
```
