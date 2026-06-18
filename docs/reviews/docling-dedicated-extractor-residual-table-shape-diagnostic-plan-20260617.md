# Docling Dedicated Extractor Residual Table-shape Diagnostic Plan - 2026-06-17

Gate: `Docling Dedicated Extractor Residual Table-shape Diagnostic Planning Gate`
Role: planning worker
Status: `PLAN_READY_FOR_REVIEW_NOT_READY`
Release/readiness: `NOT_READY`

## Goal

Produce a no-live diagnostic matrix for the remaining Docling dedicated extractor residuals after row/column label derivation.

The goal is to explain why `43 / 92` target field slots still remain missing, especially:

- `product_profile.investment_scope`;
- `nav_benchmark_performance.nav_growth_rate`;
- `nav_benchmark_performance.benchmark_return_rate`;
- `tracking_error.value_text`;
- `turnover_rate`;
- remaining `holdings_snapshot.*` misses;
- explicitly deferred narrative/share/risk fields.

Success signal:

- same four accepted current-schema candidate envelopes are inspected;
- every missing field slot is assigned a deterministic diagnostic reason code;
- reason codes distinguish source absence from extractor predicate mismatch;
- the evidence identifies the next narrow implementation route;
- all findings remain candidate-only and `NOT_READY`.

## Non-goals / Boundaries

This gate does not authorize:

- extractor rule changes;
- representation projection changes;
- parser replacement;
- `FundDataExtractor` integration;
- production `EvidenceAnchor` exposure;
- source-truth acceptance;
- field correctness claims;
- baseline promotion;
- live Docling, PDF, cache, source-helper, network, provider, LLM, golden, release, PR, or readiness commands.

This is a diagnostic-only gate. It must not convert missing fields into direct hits.

## Design / Control Alignment

Direct accepted inputs:

- `docs/reviews/docling-dedicated-extractor-row-column-label-derivation-reevidence-20260617.md`
- `reports/docling-dedicated-extractor-row-column-label-derivation-reevidence/20260617/template_field_coverage_after_row_column_labels.json`
- `fund_agent/fund/documents/candidates/template_field_extraction.py`

Accepted facts:

- Row/column label derivation increased direct slots only from `48 / 92` to `49 / 92`.
- Candidate anchors increased from `52` to `57`.
- Only `holdings_snapshot.target_fund_holdings` improved from `0` to `1`.
- The main remaining residual is not solved by generic row/column label derivation.
- Release/readiness remains `NOT_READY`.

## First-principles Judgment

The next useful unit is not another extractor rule change. The current evidence cannot distinguish:

- whether a target field is genuinely absent from the candidate representation;
- whether the relevant text/table exists in the wrong section;
- whether the section is correct but the matcher predicate is too narrow;
- whether the field is deferred by current plan;
- whether the next fix should be table-family recognition, text-pattern extraction, or field-specific matching.

Therefore the shortest safe path is an evidence-only diagnostic over the same local candidate JSON artifacts and current extractor result matrix.

This is not over-designed because it avoids reusable diagnostic infrastructure, public schema changes, and production path changes. It writes one matrix and one evidence artifact for one residual set.

## Affected Files

Allowed code files:

- None.

Allowed evidence artifacts:

- `docs/reviews/docling-dedicated-extractor-residual-table-shape-diagnostic-evidence-20260617.md`
- `docs/reviews/docling-dedicated-extractor-residual-table-shape-diagnostic-controller-judgment-20260617.md`
- `reports/docling-dedicated-extractor-residual-table-shape-diagnostic/20260617/residual_table_shape_matrix.json`

Allowed planning/review artifacts:

- `docs/reviews/docling-dedicated-extractor-residual-table-shape-diagnostic-plan-20260617.md`
- `docs/reviews/plan-review-*.md`

## Contract / Schema / State Changes

No production contract, schema, state-machine, public interface, or README changes.

Diagnostic matrix contract:

- `candidate_only=true`;
- `release_readiness="NOT_READY"`;
- one row per missing field slot from the accepted row/column label re-evidence matrix;
- include sample identity, field path, target section family, relevant candidate blocks, candidate text snippets or table-row snippets, and reason code;
- include aggregate counts by reason code and field path;
- include interpretation flags:
  - `missing_fields_prove_source_absence=false`;
  - `direct_fields_are_correctness_proof=false`;
  - `baseline_promotion_supported=false`;
  - `production_integration_supported=false`.

Required reason-code taxonomy:

- `deferred_by_current_plan`;
- `candidate_content_absent_in_target_sections`;
- `candidate_content_present_but_section_mismatch`;
- `candidate_content_present_but_table_shape_unclassified`;
- `candidate_content_present_but_matcher_predicate_too_narrow`;
- `candidate_content_present_but_value_pattern_not_isolated`;
- `needs_target_specific_extractor_rule`;
- `diagnostic_inconclusive_candidate_only`.

## Diagnostic Method

Use the same four current-schema candidate JSON artifacts:

- `reports/representation-json/004393_2025_docling_current_envelope.json`
- `reports/representation-json/006597_2024_docling_full.json`
- `reports/representation-json/017641_2024_docling_full.json`
- `reports/representation-json/110020_2024_docling_full.json`

For each missing field slot from the accepted row/column label matrix:

1. Load the candidate JSON payload.
2. Project via `project_candidate_representation(payload)`.
3. Use the current extractor result only to identify missing slots; do not alter extraction result.
4. Resolve relevant candidate sections by existing section context behavior where possible.
5. Search only the projected candidate representation:
   - candidate text blocks;
   - candidate tables;
   - table captions, labels, headings, row text, and cell text.
6. Capture bounded snippets sufficient for diagnosis, not full report text.
7. Assign exactly one primary reason code and optional secondary signals.
8. Produce aggregate reason counts and next-route recommendation.

Field-family target hints:

- `product_profile.investment_scope`: inspect `§2` profile tables and nearby text for `投资范围`.
- `nav_benchmark_performance.*`: inspect `§3` performance tables for period rows, growth columns, benchmark columns, and multi-level table headers.
- `tracking_error.value_text`: inspect `§3` / `§4` text and tables for actual disclosed tracking error, rejecting target/limit language separately.
- `turnover_rate`: inspect `§8` tables/text for `换手率` and trading amount ratio expressions.
- `holdings_snapshot.*`: inspect `§8` tables for asset-type row context, security/fund name columns, fair value, and net asset ratio.
- deferred fields: classify directly as `deferred_by_current_plan` unless evidence shows they were accidentally omitted from the deferred taxonomy.

## Slice

### Slice 1: Residual table/text shape diagnostic evidence

Objective:

- classify all currently missing candidate field slots without changing extraction behavior.

Allowed changes:

- write the diagnostic evidence artifact;
- write the diagnostic matrix JSON;
- no production code changes;
- no tests required because no code changes are allowed.

Expected outcome:

- `43` missing field slots are classified;
- aggregate reason counts are present;
- per-field reason counts are present;
- next route is one of:
  - target-specific table-family recognition planning;
  - target-specific text-pattern extraction planning;
  - field contract/deferred-field decision planning;
  - blocked-not-ready if diagnostics cannot distinguish the residual.

Stop condition:

- stop after evidence artifact, matrix artifact, controller judgment, and accepted local commit;
- do not implement extractor fixes in this gate.

## Validation

Required validation:

```text
uv run python -c '<load matrix JSON; assert candidate_only; assert NOT_READY; assert row count equals accepted missing slot count 43; assert every row has reason_code; assert aggregate counts sum to 43>'
```

Expected:

- validation exits `0`;
- no live/network/PDF/cache/source-helper access occurs.

Optional formatting:

```text
git diff --check -- docs/reviews/docling-dedicated-extractor-residual-table-shape-diagnostic-evidence-20260617.md docs/reviews/docling-dedicated-extractor-residual-table-shape-diagnostic-controller-judgment-20260617.md reports/docling-dedicated-extractor-residual-table-shape-diagnostic/20260617/residual_table_shape_matrix.json
```

Expected:

- no output.

## Docs Decision

No README update.

Reason:

- This gate writes diagnostic evidence only.
- No public API, package behavior, CLI, test convention, or production path changes.

## Risks / Open Questions

Residual risks:

- Candidate text snippets diagnose extractor mismatch but do not prove source truth.
- A reason code can point to the next route but cannot itself authorize field correctness.
- If candidate snippets are too sparse, some rows may remain `diagnostic_inconclusive_candidate_only`.

Open questions:

- None blocking for this diagnostic slice.

## Completion Report Format

Closeout must report:

- evidence artifact path;
- matrix artifact path;
- reason-code aggregate counts;
- field families with strongest next-route signal;
- explicit `NOT_READY` / candidate-only boundary;
- next recommended gate.

VERDICT: `PLAN_READY_FOR_REVIEW_RESIDUAL_TABLE_SHAPE_DIAGNOSTIC_NOT_READY`
