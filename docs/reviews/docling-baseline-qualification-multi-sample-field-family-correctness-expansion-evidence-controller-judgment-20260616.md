# Docling Multi-sample Field-family Correctness Expansion Evidence Controller Judgment - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Expansion Evidence Gate`
Controller role: evidence disposition and closeout
Release/readiness: `NOT_READY`

## 1. Scope

This controller judgment closes the evidence gate that followed accepted plan checkpoint
`bc82125`.

This gate did not run live/network/EID acquisition, `FundDocumentRepository`, PDF parsing,
Docling conversion, provider/LLM routes, analyze/checklist/golden/readiness/release/PR/push/merge
commands, or source/test/runtime changes.

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` | Accepted evidence plan |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-controller-judgment-20260616.md` | Plan controller judgment |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md` | Evidence summary |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | Machine-readable evidence |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-review-ds-tmux-20260616.md` | DS evidence review |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-rereview-ds-tmux-20260616.md` | DS targeted fix re-review |

MiMo evidence review was not used. Its pane retained unrelated prior prompt content after the allowed clear/retry path, so it was classified as temporarily unavailable for this assigned review rather than treated as current evidence.

## 3. Accepted Evidence Facts

| Fact | Classification | Controller disposition |
| --- | --- | --- |
| S1 `004393 / 2025` has an accepted same-source reviewed-facts artifact with 21 Docling selected facts: 19 exact + 2 normalized. | accepted bounded evidence fact | `ACCEPT` |
| S1 source pilot contains 4 pdfplumber comparator mismatches. | diagnostic comparator fact | `ACCEPT_AS_DIAGNOSTIC_ONLY` |
| S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024` have local Docling/pdfplumber candidate JSON artifacts present and hashed. | candidate input availability fact | `ACCEPT` |
| For S4/S5/S6, no accepted no-live same-source reference artifact or no-live repository metadata proof was established in this gate. | blocker fact | `ACCEPT` |
| Existing candidate JSONs are not source truth and are not field-correctness proof. | boundary fact | `ACCEPT` |
| EID HTML remains blocked/deferred for this Docling expansion gate. | boundary fact | `ACCEPT` |

## 4. Review Finding Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Fix 1: S1 fact `candidate_artifact` paths initially referenced `_current_envelope.json` instead of manifest-verified `_full.json`. | DS review | `ACCEPT_FIXED` | Evidence JSON now points all 21 S1 facts to `reports/representation-json/004393_2025_docling_full.json`; DS targeted re-review verified closure. |
| Fix 2: Evidence needed to explain why `FundDocumentRepository(force_refresh=False)` was not attempted for S4/S5/S6. | DS review | `ACCEPT_FIXED` | Evidence Markdown now records that this pass was no-live/no-PDF/no-FDR and therefore records `no_no_live_reference_proof` instead of probing repository behavior; DS targeted re-review verified closure. |
| MiMo review unavailable for this evidence gate. | Controller observation | `ACCEPTED_REVIEWER_AVAILABILITY_RESIDUAL` | DS review plus targeted re-review were completed through real tmux artifacts. MiMo was not counted because the pane failed clear verification. |

## 5. Blocked Claims

The following claims remain blocked:

- multi-sample Docling field-family correctness;
- S4/S5/S6 field correctness;
- source truth;
- full field correctness;
- production parser replacement;
- `FundDocumentRepository` behavior change;
- `EvidenceAnchor` schema change;
- Service/Host/UI/renderer/quality gate integration;
- readiness/release/PR readiness.

## 6. Residuals

| Residual | Owner | Next handling |
| --- | --- | --- |
| No-live same-source reference proof for S4/S5/S6 is absent. | Controller / future evidence worker | Requires a dedicated reference availability proof gate. |
| FDR `force_refresh=False` was not attempted in this evidence pass. | Controller | Decide in the next gate whether to design a no-live repository metadata proof or explicitly authorize a bounded repository attempt. |
| Multi-sample correctness remains unproven beyond S1. | Controller | Do not promote Docling baseline or production route until expansion samples are reviewable. |
| MiMo review was unavailable for this evidence gate. | Controller | Reuse MiMo only after pane clear verification succeeds. |

## 7. Final Verdict

```text
VERDICT: ACCEPT_EVIDENCE_BLOCKED_NOT_READY
```

Accepted conclusion:

```text
S1 remains a bounded accepted pilot. S4/S5/S6 candidate artifacts exist, but multi-sample Docling correctness expansion is blocked because no no-live same-source reference proof was established for the expansion samples.
```

Next recommended gate:

```text
Docling Multi-sample Same-source Reference Availability Proof Gate
```

The next gate should answer only whether S4/S5/S6 can obtain no-live same-source reference proof through accepted reference artifacts or an explicitly bounded `FundDocumentRepository(force_refresh=False)` path. It must not promote Docling baseline, replace the production parser, or claim readiness.
