# RR-09 A2 Value-match / Bond-risk Missing-evidence Diagnostic Plan

Verdict: `RR_09_A2_DIAGNOSTIC_PLAN_READY_FOR_REVIEW_NOT_READY`

## 1. Goal Confirmation

Work unit:

`RR-09 A2 R1-R4 Value-match / Bond-risk Missing-evidence Diagnostic`

Current user goal remains the broader Evidence Confirm productionization goal: key fund-report claims, numbers and conclusions must be traceable, consistent with evidence, quality-gate actionable, default-product usable, and ultimately release-ready.

This A2 work unit is narrower and evidence-driven:

- A1 live/PDF re-evidence proved all four R1-R4 samples still fail strict deterministic V2 after A1-C.
- A1-C closed the previous zero-reference materializer defect for current evidence.
- Current unresolved failure shape is `value_match` for `fee_schedule`, `nav_benchmark_performance`, `manager_alignment`, `manager_strategy_text`; R3 additionally has `bond_risk_evidence` `missing_evidence`.

Goal:

- Build and run a bounded diagnostic path that explains whether current `value_match` failures are caused by fact value shape, tokenization/matching rules, coarse reference degradation, wrong anchor/reference attachment, or extractor/projection mismatch.
- Classify the R3 `bond_risk_evidence` `missing_evidence` failure separately from value-match failures.
- Produce safe, durable evidence sufficient to choose the next fix route without changing V2 thresholds or quality-gate semantics.

Success signal:

- A2 evidence can assign each failing source field to a stable next-fix class:
  - `value_shape_overbroad`
  - `matcher_normalization_gap`
  - `coarse_reference_insufficient`
  - `anchor_attachment_mismatch`
  - `extractor_value_or_anchor_defect`
  - `bond_risk_group_anchor_projection_gap`
  - `undetermined_requires_live_excerpt_review`
- The diagnostic output contains no raw annual-report excerpts, PDF/cache paths, URLs, provider payloads, API keys, or report-body text.
- The next implementation gate can be planned from direct evidence rather than guessing.

## 2. Non-goals / Boundary

Out of scope for A2 planning and its immediate diagnostic implementation:

- No fix to `value_match`, extractor outputs, bond-risk projection, quality gate, CLI, Service, renderer, checklist, provider, LLM, tag, release, or readiness.
- No direct PDF/cache/source-helper access outside `FundDocumentRepository`.
- No semantic provider fallback and no replacement of deterministic V2 as the main truth path.
- No weakening of V2 hard-gate, `value_match`, `missing_evidence`, or `anchor_precision` semantics.
- No raw excerpt or full structured fact value dump into artifacts.
- No B1 `017641 / 2024` runtime product CLI re-evidence unless separately authorized.

## 3. Accepted Input

Accepted A1-C implementation and aggregate:

- `docs/reviews/evidence-confirm-productionization-rr-09-a1c-code-review-controller-judgment-20260624.md`
- `docs/reviews/evidence-confirm-productionization-rr-09-a1c-aggregate-deepreview-controller-judgment-20260624.md`
- Accepted slice commit: `0671fff`

Accepted A1 live/PDF re-evidence:

- Evidence artifact: `docs/reviews/evidence-confirm-productionization-rr-09-a1-live-pdf-reevidence-20260624.md`
- Controller judgment: `docs/reviews/evidence-confirm-productionization-rr-09-a1-live-pdf-reevidence-controller-judgment-20260624.md`
- Verdict: `ACCEPT_RR_09_A1_LIVE_PDF_REEVIDENCE_ROUTE_A2_NOT_READY`

A1 live/PDF accepted facts:

| Residual | Sample | Reference status | Reference count | Strict V2 status | Current failure shape |
|---|---|---|---:|---|---|
| R1 | `004393 / 2025` | pass | 144 | fail | `value_match=8`, `anchor_precision_warn=34` |
| R2 | `004194 / 2024` | pass | 144 | fail | `value_match=15`, `anchor_precision_warn=35` |
| R3 | `006597 / 2024` | pass | 132 | fail | `value_match=15`, `missing_evidence=3`, `anchor_precision_warn=29` |
| R4 | `110020 / 2024` | pass | 158 | fail | `value_match=15`, `anchor_precision_warn=39` |

Failing buckets:

- R1: `structured.nav_benchmark_performance`, `structured.manager_alignment`, `structured.manager_strategy_text`
- R2/R4: `structured.fee_schedule`, `structured.nav_benchmark_performance`, `structured.manager_alignment`, `structured.manager_strategy_text`
- R3: same as R2/R4 plus `structured.bond_risk_evidence` `missing_evidence`

## 4. Direct Code Evidence

V2 value-match behavior in `fund_agent/fund/evidence_confirm.py`:

- `_dimension_value_match()` skips derived / not-applicable facts.
- If proof references are absent, `value_match` is `not_applicable`; after A1-C proof references exist, value-match becomes decisive.
- `_material_tokens(fact.value)` recursively flattens scalar values from the structured fact value.
- `_matched_anchor_ids(tokens, proof_references)` passes if any material token appears in any proof reference excerpt for that fact.
- `_token_matches_excerpt()` uses numeric decimal equivalence for numeric tokens and normalized substring matching for text tokens.
- Current A1 failures therefore mean no flattened material token matched the same-anchor proof excerpts for the failing facts.

Projection evidence in `fund_agent/fund/chapter_facts.py`:

- The failing source fields are projected into multiple template chapters through `_CHAPTER_FIELD_SPECS`, so one extractor/value defect can surface as repeated chapter fact failures.
- `_project_bond_risk_evidence_fact()` currently returns `evidence_anchor_ids=()` for available bond-risk evidence and records: `bond_risk_evidence 组级锚点引用保留在 value.anchors 内，未展开为 ChapterEvidenceAnchor`.
- That direct code fact is a likely explanation for R3 `bond_risk_evidence` `missing_evidence`, but A2 must still verify whether the specific R3 failure is exactly this projection gap.

Bond-risk model evidence in `fund_agent/fund/extractors/models.py`:

- `BondRiskEvidenceValue` contains group-level anchors.
- `validate_bond_risk_evidence_value()` requires accepted / weak groups to reference existing group anchors.
- The bond-risk extractor can therefore produce internal anchors even though current chapter projection does not expose them as `ChapterEvidenceAnchor`.

## 5. First-principles Judgment

The current failure should not be fixed by relaxing V2.

Reason:

- The user goal requires evidence/claim consistency before user-visible output.
- A1-C proved references can now be materialized.
- The new failure shape is exactly the step that checks whether structured fact values are present in same-anchor references.
- Relaxing `value_match` would make the final state less true, because it would let unmatched values pass without explaining why.

The shortest correct path is diagnostic-first:

1. Add a no-live safe diagnostic helper that can explain value-match failures from in-memory projection + references + V2 result without exposing raw excerpts.
2. Run that helper on no-live fixtures to prove classification semantics.
3. Only after explicit live/PDF authorization, run it on R1-R4 repository-bounded samples and write safe evidence.
4. Use that evidence to plan a targeted fix.

## 6. Planned Diagnostic Design

Add a Fund-layer diagnostic helper, not a product behavior change.

Proposed module:

`fund_agent/fund/evidence_confirm_value_diagnostics.py`

Proposed schema version:

`evidence_confirm_value_diagnostic.v1`

Inputs:

- `ChapterFactProjection`
- tuple of `EvidenceConfirmReference`
- `EvidenceConfirmResultV2`

Mandatory V2 same-source constraint:

- The diagnostic helper must derive token and match information from the same primitives used by deterministic V2 `value_match`.
- It must not implement a parallel approximate matcher.
- Acceptable implementation options:
  - keep the helper in `evidence_confirm.py` behind package-private diagnostic functions that call current `_material_tokens()`, `_matched_anchor_ids()`, `_token_matches_excerpt()` and proof-reference selection; or
  - extract package-private primitives from `evidence_confirm.py` into an internal module used by both V2 and diagnostics, with no behavior change and no public API expansion.
- If a separate `evidence_confirm_value_diagnostics.py` module is used, it must call those package-private primitives rather than duplicating flatten / normalize / numeric matching logic.

No repository, PDF, cache, source helper, Service, Host, provider, LLM, renderer, quality gate, CLI, or file-system input.

Safe output should include:

- `fund_code`
- `report_year`
- `fact_id`
- `source_field_id`
- `chapter_id`
- `fact_status`
- failing dimensions
- `reference_count`
- `anchor_count`
- `proof_reference_count`
- `token_count`
- token categories only:
  - `numeric_percent`
  - `numeric_plain`
  - `boolean`
  - `short_text`
  - `long_text`
  - `empty`
- structural value paths, not raw values, for unmatched tokens:
  - examples: `value.rows[].fee_rate`, `value.period_return`, `value.groups[].summary`
- matched-token category counts, not matched raw token values
- reference granularity:
  - section-level
  - table-level
  - row-level
  - derived/reviewed note
- locator downgrade indicator
- classification candidate
- explicit flag that token/match metadata was produced by V2 same-source primitives

Forbidden output:

- raw `excerpt_text`
- raw token values
- full structured fact values
- PDF/cache paths
- URLs
- source-helper internals
- provider payloads
- report body text
- tracebacks or secrets

Classification rules:

| Condition | Classification |
|---|---|
| Fact has value-match fail; token count is high and unmatched token paths include metadata-like or label-like scalar paths | `value_shape_overbroad` |
| Fact has value-match fail; token categories are primarily numeric but reference granularity is coarse and no numeric category matched | `coarse_reference_insufficient` |
| Fact has value-match fail; references exist but none are proof references after predicate filtering | `anchor_attachment_mismatch` |
| Fact has value-match fail; tokens are reasonable, references are row/table precise, but no category matched | `extractor_value_or_anchor_defect` |
| Fact has value-match fail; normalized text categories dominate and no numeric issue exists | `matcher_normalization_gap` or `extractor_value_or_anchor_defect`, depending on token/reference granularity |
| Fact has missing-evidence fail for `structured.bond_risk_evidence` and `value.anchors` exists but chapter `evidence_anchor_ids` is empty | `bond_risk_group_anchor_projection_gap` |
| Evidence is insufficient without raw excerpt review | `undetermined_requires_live_excerpt_review` |

## 7. Implementation Slices

### Slice A2-S1: No-live Diagnostic Helper

Objective:

- Implement `evidence_confirm_value_diagnostic.v1` as an in-memory Fund helper with focused synthetic tests.

Allowed files:

- `fund_agent/fund/evidence_confirm_value_diagnostics.py`
- `tests/fund/test_evidence_confirm_value_diagnostics.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

Allowed changes:

- Add dataclasses / type aliases for safe diagnostic records.
- Add a public helper such as `summarize_value_match_diagnostics(...)`.
- Reuse V2 token/matcher primitives exactly. Do not duplicate approximate flatten / normalize / numeric matching logic in the diagnostic module.
- If the current private functions in `evidence_confirm.py` are not directly importable without widening the public API, add package-private wrappers or move the exact primitives to an internal helper module consumed by both V2 and diagnostics.
- Add classification for `bond_risk_group_anchor_projection_gap` based on `BondRiskEvidenceValue` structure and chapter fact anchor exposure.
- Add tests proving:
  - no raw token values or excerpt text appear in `to_safe_dict()`;
  - diagnostic match/miss metadata is consistent with `confirm_projection_evidence_v2()` on synthetic cases;
  - text substring match, numeric decimal equivalence, percent-unit mismatch, ignored keys, dataclass flatten, dict key order, nested list values and empty values follow current V2 behavior;
  - value-shape overbroad classification for nested values with many unmatched scalar paths;
  - coarse-reference classification when references are table/section level and categories do not match;
  - anchor-attachment classification when references exist but proof-reference count is zero;
  - bond-risk group-anchor projection gap when value-level anchors exist but chapter anchors are not exposed;
  - helper does not import/instantiate repository, source helper, PDF/cache, Service, Host, provider, LLM, CLI, or renderer.

Non-goals:

- Do not change `evidence_confirm.py` pass/fail semantics.
- Do not change `chapter_facts.py` projection behavior.
- Do not change extractor outputs.
- Do not run live/PDF.

Validation:

```bash
uv run pytest tests/fund/test_evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_diagnostics.py tests/fund/test_evidence_confirm.py -q --tb=short
uv run ruff check fund_agent/fund/evidence_confirm_value_diagnostics.py tests/fund/test_evidence_confirm_value_diagnostics.py
git diff --check
```

Completion signal:

- Implementation evidence artifact records the helper behavior and validation.
- Code review finds no material boundary or leakage issue.

### Slice A2-S2: Authorized R1-R4 Diagnostic Evidence

Objective:

- Under separate explicit live/PDF authorization, run the A2 helper on the four R1-R4 repository-bounded samples and write safe evidence.

Allowed files:

- `docs/reviews/evidence-confirm-productionization-rr-09-a2-value-match-diagnostic-evidence-<date>.md`
- `docs/reviews/evidence-confirm-productionization-rr-09-a2-controller-judgment-<date>.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`

Allowed commands:

```bash
uv run python - <<'PY'
...
bundle = await FundDataExtractor().extract(fund_code, report_year, force_refresh=True)
projection = project_chapter_facts(bundle)
runner_result = await run_repository_bounded_evidence_confirm(
    EvidenceConfirmRepositoryRunRequest(
        fund_code=fund_code,
        report_year=report_year,
        projection=projection,
        force_refresh=False,
    )
)
diagnostic = summarize_value_match_diagnostics(
    projection=projection,
    references=runner_result.reference_build_result.references,
    result=runner_result.evidence_confirm_result,
)
...
PY
```

Safety constraints:

- Output safe JSON / Markdown only with schema version, sample id, source field ids, counts, token categories, value paths, reference granularity and classification.
- State that diagnostic token/match metadata is derived from V2 same-source primitives, not a parallel matcher.
- Do not output raw excerpt text or raw scalar token values.
- Keep source/PDF access through `FundDocumentRepository` only.

Completion signal:

- Controller judgment accepts a stable classification for each failing bucket and routes to a targeted fix plan.
- Release/readiness remains `NOT_READY`.

## 8. Expected Next Fix Routes After A2 Evidence

A2 evidence should route to one or more later gates:

| A2 classification | Likely next route |
|---|---|
| `value_shape_overbroad` | Narrow value-token extraction for V2 diagnostics or field-specific comparable material token policy. |
| `matcher_normalization_gap` | Conservative V2 matcher normalization patch with red tests. |
| `coarse_reference_insufficient` | Field-specific row/table anchor precision improvement or materializer narrowing. |
| `anchor_attachment_mismatch` | Projection anchor/reference attachment fix. |
| `extractor_value_or_anchor_defect` | Field extractor/source-truth correction gate for the affected family. |
| `bond_risk_group_anchor_projection_gap` | Bond-risk group anchor expansion from `BondRiskEvidenceValue.anchors` into `ChapterEvidenceAnchor`. |
| `undetermined_requires_live_excerpt_review` | Separate reviewed evidence gate with stricter redaction policy or manual bounded excerpt review. |

## 9. Docs Decision

Slice A2-S1 changes developer-facing diagnostic capability, so update:

- `fund_agent/fund/README.md`: describe `evidence_confirm_value_diagnostic.v1` as a safe no-live diagnostic helper, not product behavior.
- `tests/README.md`: add the focused diagnostic test file and clarify no repository/PDF/provider behavior.

No root `README.md` update unless CLI/user-facing behavior changes; A2 does not plan such a change.

## 10. Risks / Open Questions

No blocking open question for the no-live helper.

Known risks:

- A2-S1 can classify structural causes only from in-memory projection/reference/result; it cannot prove exact raw excerpt correctness.
- A2-S2 requires explicit live/PDF authorization before running R1-R4 again.
- If safe categories remain insufficient, the next route must record `undetermined_requires_live_excerpt_review` instead of guessing.
- The helper must avoid becoming a second V2 implementation with divergent pass/fail semantics; it is diagnostic-only.

## 11. Completion Report Format

Final report for A2 planning/review should include:

- plan artifact path;
- review artifact path;
- accepted / rejected / deferred findings;
- exact next gate;
- validation commands and results;
- explicit `NOT_READY` release/readiness status;
- explicit statement that no live/PDF/provider/LLM, quality-gate change, checklist support, report-body rendering, tag or release was performed.

## 12. Completion Token

`RR_09_A2_DIAGNOSTIC_PLAN_READY_FOR_REVIEW_NOT_READY`
