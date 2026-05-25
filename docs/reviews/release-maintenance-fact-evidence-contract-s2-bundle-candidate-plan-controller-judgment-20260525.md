# Release Maintenance Fact-Evidence Contract S2 Bundle Candidate Plan Controller Judgment

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `fact-evidence-contract S2 bundle candidate planning`
> Controller status: accepted locally; next gate is `typed ReportEvidenceBundle model/projection implementation plan review`

## Step Self-Check

- Current role: controller. This artifact records review disposition, acceptance rationale, residual ownership, and gate bookkeeping only.
- Source of truth: `AGENTS.md`, `docs/design.md` current architecture and §5.4 / §5.4.1 / §5.4.2 / §5.4.3 / §7.2 / §7.3 / §7.4, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, S1 score-schema controller judgment, and S1 dry-run controller judgment.
- Reviewed plan: `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md`.
- Independent reviews: `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-review-mimo-20260525.md`, `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-review-ds-20260525.md`.
- Re-reviews after plan patch: `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-rereview-mimo-20260525.md`, `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-rereview-ds-20260525.md`.
- Scope boundary: no source code, tests, renderer, FQ0-FQ6 quality gate, config, README, design doc, Host/Agent package, Dayu runtime, fixture promotion, push, PR, or external state change.

## Verdict

**ACCEPTED FOR NEXT GATE.**

The patched S2 bundle candidate plan is accepted as a code-generation-ready planning artifact, not as code authorization. It resolves the core S2 question by choosing a projection wrapper: `ReportEvidenceBundle` should wrap and project from `StructuredFundDataBundle`, not replace it and not create a parallel extraction path.

This is the correct first-principles choice because the current system already has a repository-bounded extraction truth source, extraction snapshot / score / FQ0-FQ6 quality gate consumers, and accepted S0/S1 review evidence. A parallel fact path would increase disagreement risk and make report-quality failures harder to localize.

## Accepted Decisions

| Decision | Accepted behavior | Controller rationale |
|---|---|---|
| Bundle relation | `ReportEvidenceBundle` wraps and projects from `StructuredFundDataBundle` | Preserves current extractor investment and avoids parallel extraction. |
| Location / ownership | Future model belongs in Agent-layer `fund_agent/fund` domain capability | It understands fund type, evidence anchors, CHAPTER_CONTRACT, preferred_lens, and scoring semantics. |
| `classified_fund_type` | Domain is current `FundType` values plus `unknown`; illegal or missing values block `scoring_ready` | Fund type precedes preferred lens and cannot be inferred casually in projection. |
| `nav_data` | Excluded from initial facts projection | `NavDataResult` is not an `ExtractedField`; mapping it now would force a new source contract. |
| Review status | Derived through S0-aligned progression with restrictive priority order | Prevents caller-set inconsistent lifecycle state. |
| Anchor ids | `sha256` first 8 hex over normalized locator fields, with deterministic collision suffixes | Gives implementation a stable id recipe without redesign. |
| `data_gap_refs` | Namespaced `gap:{fund}:{year}:{gap_kind}:{field_or_claim}:{reason}` records | Turns missing facts and unsupported claims into first-class constraints. |
| Turnover stability | Active-fund Chapter 3 stability/style-consistency claim must cite reviewed turnover or style-change evidence, or explicitly state insufficiency | Implements S1 dry-run controller decision: `chapter_contract` first, not automatic extraction. |
| `external_official` | Future / metadata only in S2; no ad hoc external API access | Preserves Repository-style source boundary. |
| Future slices | Typed model, projection, review-status validation, score linkage, and chapter-contract wording constraints are future code gates | This plan does not authorize implementation. |

## Finding Disposition

| Finding set | Source | Disposition | Owner / gate |
|---|---|---|---|
| Review status conversion / priority was underspecified | MiMo F-01; DS F-2 | Fixed. Re-reviews confirmed legal progression, transition table, terminal states, priority order, conflict examples, and invalid combinations. | Closed for planning; implementation tests in next plan review. |
| `classified_fund_type` domain was not directly implementable | DS F-1 | Fixed. Re-review confirmed full domain and projection behavior from `StructuredFundDataBundle.basic_identity.value`. | Closed for planning. |
| `nav_data` projection was structurally unclear | DS F-3 | Fixed by conservative exclusion from initial facts projection. | Later `nav_data` mapping slice if needed. |
| `locator_hash` was underspecified | MiMo F-02; DS F-4 | Fixed. Re-reviews confirmed `sha256` / normalization / collision handling. | Closed for planning. |
| Turnover wording constraint was still marked candidate | MiMo F-03 | Fixed. Re-review confirmed accepted narrow constraint tied to S1 judgment. | Closed for planning. |
| Multi-anchor `ExtractedField` mapping was unclear | MiMo F-04 | Fixed. Re-review confirmed no-drop multi-anchor rule and tests. | Closed for planning. |
| `external_official`, `preferred_lens`, `corpus_id`, and negative tests were under-specified | DS F-5 / F-6 / F-7 / F-8 | Fixed. Re-review confirmed boundary, formats, and concrete negative tests. | Closed for planning. |

## Residuals Accepted Into Next Gate

| Residual | Owner / next gate | Required handling |
|---|---|---|
| Exact model file placement | typed model/projection implementation plan review | Choose concrete Agent-layer Fund files after reading package layout; do not scatter models into Service or renderer. |
| Bundle immutability | typed model/projection implementation plan review | Decide whether `ReportEvidenceBundle` and child records should be frozen dataclasses or equivalent immutable models. |
| `type_slot_membership_status` value domain | typed model/projection implementation plan review | Define executable enum/domain and derivation, including `matches_slot` and type-gap outcomes. |
| `EvidenceAnchor.source_kind` narrowness | typed model/projection implementation plan review | Wrap current anchors first; do not widen extractor enums unless needed and tested. |
| `nav_data` mapping | future `nav_data` source-contract slice | Keep excluded from initial facts until a safe mapping contract exists. |
| Fallback source categories | source reliability gate | Recover category for `110020`, `017641`, and `017970`, or keep excluded. |
| Pure FOF coverage | fund-type taxonomy or corpus second pass | Find pure `fof_fund` or explicitly decide QDII-FOF precedence. |
| Curated fixture / durable baseline | later curated-fixture gate | Do not promote ignored scoring-run outputs or baseline fixtures in the next gate. |

## Boundary Confirmation

- No current renderer behavior or v0 8-chapter output changed.
- No FQ0-FQ6 quality-gate behavior changed.
- No LLM writing, LLM audit, Evidence Confirm, repair loop, patch/regenerate, or report assembly pipeline was claimed as implemented.
- No `fund_agent/host` or `fund_agent/agent` package was created.
- No `dayu.host` or `dayu.engine` dependency was introduced.
- No tracked fixture or durable baseline was promoted.
- Future annual-report facts remain behind `FundDocumentRepository` or public Fund APIs that themselves use it.
- All future business parameters must remain explicitly typed; no `extra_payload` / `extra_payloads`.

## Next Gate

`typed ReportEvidenceBundle model/projection implementation plan review`

The next gate should produce an implementation plan, not code. It must choose concrete files, tests, validation commands, and a minimal implementation slice. The default recommended slice is typed model skeleton plus projection from `StructuredFundDataBundle`, with review-status derivation and invalid-combination validation included only if the plan can keep scope tight.

Stop before implementation if the next plan requires renderer/FQ0-FQ6 behavior changes, Host/Agent runtime, direct PDF/cache/source access, fixture promotion, or a parallel extraction path.

## Validation

```text
rg -n "ReportEvidenceBundle|StructuredFundDataBundle|FundDocumentRepository|extra_payload|dayu\\.host|dayu\\.engine|chapter_contract|turnover|data_gap_refs|no code implementation" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md
rg -n "Conclusion: \\*\\*PASS|RESOLVED|已解决|classified_fund_type|nav_data|review_status priority|sha256|external_official|preferred_lens|corpus_id|Negative tests" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-rereview-mimo-20260525.md docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-rereview-ds-20260525.md
git diff --check
```

Result: passed.
