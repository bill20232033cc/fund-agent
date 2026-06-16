# Docling Multi-sample Field-family Correctness Expansion Evidence Controller Judgment - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Evidence Gate`
Controller role: evidence disposition and closeout
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the resumed evidence gate after the controlled
same-source reference acquisition checkpoint `5b5f8d5`.

This gate reviewed selected Docling candidate facts for expansion samples S4
`006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024` against same-source
annual-report references loaded through `FundDocumentRepository(...,
force_refresh=False)`.

This gate did not run Docling conversion, pdfplumber export, live/source
acquisition, provider/LLM routes, analyze/checklist/golden/readiness/release/PR
commands, source/test/runtime changes, parser replacement, source policy change,
`EvidenceAnchor` schema change, or Service/Host/UI/renderer/quality gate
integration.

The evidence and JSON paths intentionally supersede the earlier blocked evidence
content at the same paths. The prior blocked state remains recoverable through
the earlier accepted checkpoint history and is not treated as if it never
existed.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule truth source |
| `docs/current-startup-packet.md` | Current active gate and NOT_READY guardrails |
| `docs/implementation-control.md` | Control truth and current gate scope |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` | Accepted evidence plan |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-controller-judgment-20260616.md` | Plan controller judgment |
| `docs/reviews/docling-controlled-same-source-reference-acquisition-evidence-controller-judgment-20260616.md` | Accepted S4/S5/S6 reference metadata prerequisite |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md` | Evidence summary |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | Machine-readable reviewed facts |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-review-local-20260616.md` | Local fallback review |

Independent subagent review was attempted, but the subagent spawn channel
returned `agent thread limit reached`. No MiMo, DS or ProCodex review is claimed
for this resumed evidence closeout.

## 3. Accepted Evidence Facts

| Fact | Classification | Controller disposition |
| --- | --- | --- |
| S1 `004393 / 2025` remains accepted by hash from the prior bounded pilot: 21 selected Docling facts, 19 exact + 2 normalized. | accepted bounded evidence fact | `ACCEPT` |
| S4/S5/S6 reference metadata is accepted as EID single-source, fallback disabled and fallback unused by `5b5f8d5`. | accepted prerequisite fact | `ACCEPT` |
| This gate loaded S4/S5/S6 annual reports through `FundDocumentRepository.load_annual_report(..., force_refresh=False)`. | repository-bound reference fact | `ACCEPT_WITH_BOUNDARY` |
| The expansion evidence reviewed 51 selected Docling facts across S4/S5/S6. | evidence fact | `ACCEPT` |
| All 51 expansion facts matched same-source repository-loaded table-row excerpts by exact or normalized match; mismatch count is 0. | selected-fact correctness fact | `ACCEPT` |
| Each expansion sample reviewed five table-heavy field families: `fund_identity_profile`, `product_contract_profile`, `performance_indicators`, `expense_costs`, `portfolio_structure`. | bounded coverage fact | `ACCEPT` |
| `manager_alignment` remains blocked/deferred for all three expansion samples. | residual fact | `ACCEPT_RESIDUAL` |
| pdfplumber comparator was not re-opened for S4/S5/S6. | comparator boundary fact | `ACCEPT_RESIDUAL` |
| EID HTML render remains `blocked_deferred` for this Docling expansion gate. | route boundary fact | `ACCEPT` |

## 4. Review Finding Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| R1: Evidence overwrites prior blocked content at the same paths. | Local review | `ACCEPT_RESIDUAL` | Controller records this evidence as a superseding resumed evidence pass. Prior blocked content remains in checkpoint history. |
| R2: Reference excerpts are parsed table rows, not visual screenshots or raw PDF crop images. | Local review | `ACCEPT_RESIDUAL` | This is stronger than candidate self-agreement and preserves the repository boundary, but future ambiguous facts may require visual/crop review. |
| R3: `manager_alignment` is blocked for S4/S5/S6. | Local review | `ACCEPT_RESIDUAL` | The residual is visible in JSON and Markdown and is not counted as a passed family. |
| R4: pdfplumber comparator is not re-opened. | Local review | `ACCEPT_RESIDUAL` | This gate answers Docling selected-fact expansion correctness only; pdfplumber comparison remains future work. |
| Reviewer channel unavailable. | Controller observation | `ACCEPTED_REVIEW_CHANNEL_RESIDUAL` | Subagent spawn failed with `agent thread limit reached`; no external review is claimed. |

## 5. Accepted / Rejected / Residual Table

| Claim | Decision | Reason |
| --- | --- | --- |
| Accept selected Docling expansion facts for S4/S5/S6 as matching same-source repository-loaded references. | `ACCEPT` | 51/51 exact or normalized matches; zero mismatches. |
| Treat this as Docling source truth. | `REJECT` | Candidate JSON and repository-loaded parsed excerpts are evidence, not source-truth promotion. |
| Treat this as full field correctness. | `REJECT` | Selected facts and field families are bounded; `manager_alignment` is blocked. |
| Treat this as production parser replacement or baseline promotion. | `REJECT` | Production integration and baseline disposition require later gates. |
| Treat this as readiness/release/PR proof. | `REJECT` | Release/readiness remains `NOT_READY`; no release/PR commands were run. |
| Carry reference-excerpt strength as residual. | `ACCEPT_RESIDUAL` | Parsed table-row excerpts are not visual/crop proof. |
| Carry reviewer-channel residual. | `ACCEPT_RESIDUAL` | Subagent spawn failed; local fallback review was used transparently. |

## 6. Validation

Commands run:

```text
git diff --check
jq '.schema_version, (.samples | length), (.facts | length), (.sample_results | length), .overall_result' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json
jq -e '.not_source_truth == true and .not_production_parser_replacement == true and .not_full_field_correctness == true and .not_readiness_proof == true' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json
jq -e 'all(.facts[]; has("sample_id") and has("family") and has("candidate_route") and has("reference_source") and has("match_status") and has("mismatch_type"))' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json
jq -e 'all(.samples[]; .eid_html_status == "blocked_deferred")' reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json
```

Observed results:

```text
git diff --check: pass
schema_version: docling_multi_sample_field_family_correctness.v1
samples: 3
facts: 51
sample_results: 3
overall_result: candidate_expansion_pass_not_ready
guard checks: true
fact schema check: true
eid_html_status check: true
```

## 7. Residuals

| Residual | Owner | Next handling |
| --- | --- | --- |
| `manager_alignment` not reviewed in S4/S5/S6 expansion evidence. | Future evidence worker | Review manager tenure/holding rows in a focused manager-alignment evidence gate or as part of full-document coverage evidence. |
| Reference excerpts are parsed table rows, not visual/crop screenshots. | Controller / future evidence worker | Add visual/crop review for ambiguous fields before baseline disposition if needed. |
| pdfplumber comparator not re-opened for expansion samples. | Comparison evidence owner | Defer to comparative evidence gate if the product decision needs parser-vs-parser tradeoff evidence. |
| Local fallback review only. | Controller | Obtain MiMo/DS review in a future acceptance gate if agent channels are available. |

## 8. Final Verdict

```text
VERDICT: ACCEPT_CANDIDATE_EXPANSION_PASS_READY_FOR_RUNTIME_CONTAINMENT_EVIDENCE_GATE_NOT_READY
```

Accepted conclusion:

```text
S1 remains accepted by the prior bounded pilot. S4/S5/S6 now have accepted
same-source EID reference prerequisites and 51 selected Docling facts matched
repository-loaded same-source table-row excerpts with zero mismatches. This
supports continuing Docling baseline qualification, but does not prove source
truth, full field correctness, production parser replacement, readiness,
release or PR readiness.
```

Next recommended gate:

```text
Docling Baseline Runtime Containment Evidence Gate
```

Do not proceed to production integration or baseline disposition until runtime
containment, full-document coverage, EvidenceAnchor mapping, comparative
correctness and performance/cache/cost evidence have been accepted or explicitly
deferred by controller judgment.
