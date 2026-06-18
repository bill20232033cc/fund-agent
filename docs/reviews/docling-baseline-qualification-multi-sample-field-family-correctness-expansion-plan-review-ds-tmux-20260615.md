# Docling Multi-sample Field-family Correctness Expansion Plan Review (DS) - 2026-06-15

Gate: `Docling Multi-sample Field-family Correctness Expansion Plan Review Gate`
Role: AgentDS review worker
Release/readiness: `NOT_READY`

## 1. Scope

Review the expansion plan artifact `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` against DS review focus items specified in the plan's §12:

- same-source correctness principle enforceability
- schema distinction between candidate facts, repository-loaded references, accepted same-source reference artifacts, and comparator diagnostics
- sample matrix sufficiency for bounded multi-fund/multi-year expansion
- per-family and per-sample threshold determinism
- `not_applicable` guard against hiding missing locator/reference failures
- `NOT_READY` preservation and absence of source truth / full correctness / production parser replacement claims

## 2. Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | Execution rules truth source |
| `docs/design.md` (Docling/FundDisclosureDocument/PDF parser boundary sections via grep) | Design truth for current parser boundary, Docling candidate status, FundDisclosureDocument candidate design |
| `docs/current-startup-packet.md` | Current control packet: accepted facts, next entry, current mainline |
| `docs/implementation-control.md` (first 120 lines) | Current gate state, truth guardrails, next entry point |
| `docs/reviews/docling-baseline-qualification-review-provenance-remediation-controller-judgment-20260615.md` | Provenance remediation: `afebc92` accepted after real tmux review, prior non-tmux artifacts contaminated |
| `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-controller-judgment-20260615.md` | 004393 pilot controller judgment: 21/21 pass, bounded pilot only, `not_proven` |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` | Plan under review |

## 3. Findings

### F1: Same-source Correctness Principle — PASS

Plan §5 explicitly enumerates what correctness must come from (repository-loaded annual report or accepted same-source reference artifact) and what it must NOT be inferred from (parser-vs-parser agreement, candidate JSON existence alone, external values, untracked PDFs, etc.). The six prohibited inference sources are specific and testable. The requirement that each fact identify both candidate cell and same-source reference span (§5 final paragraph) makes the principle enforceable at evidence review time.

No amendment required.

### F2: Schema Distinction — PASS

Plan §7 JSON schema cleanly separates:

- `candidate_route` at fact level distinguishes `docling_pdf_candidate` from `pdfplumber_pdf_candidate`
- `reference_source` enum (`repository_loaded_annual_report` | `accepted_same_source_reference_artifact`) distinguishes repository-loaded from artifact-loaded references
- `route_results[]` at top level separates primary Docling route results from comparator diagnostics
- `candidate_*` prefixed fields vs `reference_*` prefixed fields prevent conflation
- `eid_html_status: "blocked_deferred"` on every sample prevents EID HTML from leaking into correctness claims

The `pdfplumber_pdf_candidate` role as "comparator only" (§6) is correctly scoped: comparator results are diagnostic and "do not prove correctness by agreement."

One advisory note: `family_applicability_reason` lives on the `facts[]` item (§7) but semantically belongs to the family level. The `family_results[]` item correctly has `applicability` and `reason`, so this is a minor denormalization, not a correctness issue. No amendment required; evidence worker may place the reason on the first fact of each family or duplicate it.

### F3: Sample Matrix Sufficiency — PASS_WITH_AMENDMENT

Plan §3 defines S1 (004393/2025), S4 (006597/2024), S5 (017641/2024), S6 (110020/2024). All use existing accepted/local candidate artifacts from `full-representation-export-manifest-20260615.json`.

Minimum matrix: S1 plus at least 2 of S4/S5/S6, with at least two report years (2024, 2025). This is a sufficient bounded expansion: it tests cross-fund generalization (three different funds beyond 004393) and cross-year generalization (2024 vs 2025) without requiring live acquisition.

**Required Amendment A1 (§3, §9 step 7, §10 stop condition 2): Clarify reference-load availability check.**

The plan currently says samples are "Required if reference load is available without live" (§3) and the evidence workflow says "If this would require live/network acquisition not already authorized, mark that sample `blocked_reference_unavailable`" (§9 step 7). These statements create ambiguity:

- Does "available without live" mean the repository has a cached PDF on disk?
- Or does it mean the evidence worker should attempt `FundDocumentRepository().load_annual_report()` and see if it triggers a network call?

The 004393 pilot already established the pattern: load through the repository with `force_refresh=False`, which uses cached PDF if available. The plan should make this explicit.

Required fix: Add to §9 step 7 (or a new §9 step 5.5 before the repository load step) a pre-check instruction:

> Before loading each sample through `FundDocumentRepository`, check whether a cached PDF exists at the expected cache path for `(fund_code, document_year)`. If no cached PDF exists, record the sample as `blocked_reference_unavailable` with reason `no_cached_pdf` and do not attempt repository load. If a cached PDF exists, load through `FundDocumentRepository().load_annual_report(fund_code, document_year, force_refresh=False)` and verify the returned metadata matches expected identity. Do not invoke `force_refresh=True` or any operation that would trigger live EID acquisition.

Also add to §10 stop conditions: "a cached PDF does not exist for a required sample and the controller has not separately authorized live acquisition for that sample."

### F4: Per-family and Per-sample Threshold Determinism — PASS

Plan §8 thresholds are numeric and categorical:

Per-family: each family has explicit match requirements (e.g., `fund_identity_profile`: all must be exact/normalized, no partial; `performance_indicators`: all numeric must be exact after named normalizations). Per-family verdicts (`pass`/`partial`/`fail`/`not_applicable`/`blocked`) have clear triggering conditions.

Per-sample: numeric criteria — ≥4 applicable families with all pass/not_applicable for `pass`; ≥3 applicable with ≤1 fail for `partial`; ≥2 fails or identity fail for `fail`.

Overall expansion: four named verdicts with explicit conditions referencing S1 hash verification and per-sample results.

These thresholds are deterministic. An evidence worker applying them to the same fact set would produce the same verdict. The only judgment call is `product_contract_profile` long-text partial match ("same clause without omitted contradicting text"), which is appropriately scoped as the only family where partial is allowed and has a bounded criterion.

No amendment required.

### F5: `not_applicable` Guard — PASS

Plan §4 `not_applicable` rules are explicit and enforceable:

- "must be based on same-source annual-report review, not on candidate JSON absence alone" — prevents hiding missing data behind `not_applicable`
- "recorded `family_applicability_reason`" — requires documented justification
- "If the family is expected for the product type but locators cannot be found, use `blocked_locator_unresolved` or `not_reviewable`, not `not_applicable`" — the key guardrail

The field-family matrix further constrains `not_applicable`: `fund_identity_profile` "normally should not be N/A" and each family has specific conditions for when N/A is acceptable. The per-sample threshold requiring ≥4 applicable families (not counting `not_applicable`) for `pass` means excessive N/A usage automatically fails.

The facts schema (§7) supports this with `field_applicability` enum including `not_applicable | blocked_locator_unresolved | blocked_reference_unavailable` as distinct states, and `mismatch_type` includes `not_applicable` only as a terminal classification.

No amendment required.

### F6: `NOT_READY` Preservation and Boundary Language — PASS

The plan preserves `NOT_READY` throughout:

- §1: "This plan does not claim source truth, production parser replacement, full field correctness, taxonomy compatibility, raw XML availability, release readiness, or PR readiness."
- §7 JSON schema: top-level boolean flags `not_source_truth`, `not_production_parser_replacement`, `not_full_field_correctness`, `not_readiness_proof` all required to be `true`, validated by jq in §11.
- §8: "All verdicts preserve `NOT_READY`."
- §13: "No production implementation, parser replacement, repository behavior change, source policy change, readiness/release/PR state change, or LLM/provider route may follow directly from this plan."
- §2 non-proof boundaries list is comprehensive and specific.

Design truth (`docs/design.md`) confirms Docling is accepted only as "candidate-layer structural locator baseline and 004393/2025 bounded pilot pass," not as production parser. The plan's boundary language aligns with this.

No amendment required.

### F7: Candidate Input Verification — ADVISORY

Plan §9 step 2 says "Load `full-representation-export-manifest-20260615.json`" but does not include a verification step to confirm that S4/S5/S6 candidate JSON files referenced by the manifest actually exist and have stable hashes before proceeding. The `input_artifacts[]` schema requires `sha256`, which implies hash computation, but the workflow doesn't sequence this.

Advisory: Add to §9 a step between 2 and 3: "Verify each candidate JSON path listed in the manifest for S1/S4/S5/S6 exists on disk. If any path is missing, stop and report `blocked_missing_candidate_input`."

### F8: EID HTML Block Consistency — PASS

Plan consistently marks EID HTML as `blocked_deferred`:
- §3 sample matrix: S4/S5/S6 all note "EID HTML blocked JSON"
- §6: "Current expansion gate must keep EID HTML blocked/deferred"
- §7 `samples[]` schema: `eid_html_status: "blocked_deferred"`
- §11 validation: jq asserts all samples have `eid_html_status == "blocked_deferred"`

This is consistent with the pilot controller judgment and the remediation controller judgment.

No amendment required.

## 4. Required Amendments

| ID | Severity | Section | Finding | Required Fix |
|---|---|---|---|---|
| A1 | MEDIUM | §3, §9 step 7, §10 | Reference-load availability check is ambiguous: "available without live" is not defined and could lead the evidence worker to either skip valid cached samples or attempt unauthorized live acquisition. | Add to §9 a pre-check step before repository load: check for cached PDF existence at expected cache path; only proceed with `force_refresh=False` if cached PDF exists; mark as `blocked_reference_unavailable` with reason `no_cached_pdf` otherwise. Add corresponding stop condition to §10. |

## 5. Deferred Risks

| Risk | Classification | Rationale |
|---|---|---|
| S4/S5/S6 cached PDFs may not exist locally | accepted residual | Plan correctly routes this to `blocked_reference_unavailable`; this is a data availability issue, not a plan defect. If all three expansion samples are blocked, the evidence gate produces `blocked_not_ready`, which is the correct outcome. |
| `product_contract_profile` long-text partial match judgment | accepted residual | The "same clause without omitted contradicting text" criterion requires reviewer judgment. The plan limits partial to this single family, which is an acceptable scope. |
| pdfplumber comparator locator may not exist for all selected facts | accepted residual | Plan §6 correctly scopes comparator as "only when a corresponding locator exists." Missing comparator is diagnostic, not a correctness failure. |
| Broader Docling correctness beyond 4 funds / 2 years remains unproven | accepted residual | Plan explicitly states this is bounded expansion, not full correctness proof. Future gates handle broader coverage. |
| EID HTML mapping remains blocked | accepted residual | Consistently marked `blocked_deferred` across all samples; separate gate required. |

## 6. Verdict

`VERDICT: PASS_WITH_REQUIRED_AMENDMENTS_NOT_READY`

Amendment A1 must be applied to the plan before the evidence gate can proceed. All other DS review concerns are satisfied. The plan is structurally sound, the schema is well-distinguished, thresholds are deterministic, `not_applicable` is properly guarded, and `NOT_READY` is preserved throughout.

Next gate after amendment: `Docling Multi-sample Field-family Correctness Expansion Evidence Gate` (after controller accepts amended plan).
