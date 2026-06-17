# Docling Dedicated Extractor Candidate-field No-live Evidence Controller Judgment - 2026-06-17

Gate: `Docling Dedicated Extractor Candidate-field No-live Evidence Gate`
Role: controller
Accepted plan commit: `1d9350b`
Status: `EVIDENCE_ACCEPTED_NOT_READY`
Verdict: `ACCEPT_NEGATIVE_EVIDENCE_ROUTE_TO_REAL_ENVELOPE_MISMATCH_DIAGNOSTIC_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Plan: `docs/reviews/docling-dedicated-extractor-candidate-field-no-live-evidence-plan-20260617.md`
- Plan review: `docs/reviews/plan-review-20260617-171534.md`
- Evidence: `docs/reviews/docling-dedicated-extractor-candidate-field-no-live-evidence-20260617.md`
- Matrix: `reports/docling-dedicated-extractor-candidate-field-no-live-evidence/20260617/template_field_coverage_matrix.json`

## Decision

Accept this evidence gate as negative no-live evidence.

The result does not support entering field contract stabilization or production integration planning yet. The next gate must diagnose why the accepted extractor yields zero direct field matches on accepted current-schema Docling candidate envelopes.

## Accepted Facts

- Four current-schema Docling candidate envelopes were runnable:
  - S1 / 004393 / 2025
  - S4 / 006597 / 2024
  - S5 / 017641 / 2024
  - S6 / 110020 / 2024
- One old S1 full JSON remains blocked by `ValueError: unsupported candidate representation schema_version`.
- Runnable sample count: 4.
- Target field slots: 92.
- Direct slots: 0.
- Missing slots: 92.
- Candidate anchors: 0.
- Direct coverage ratio: 0.0.
- Missing ratio: 1.0.
- All outputs remain candidate-only and `source_truth_status="not_proven"`.
- Production parser replacement remains `not_authorized`.

## Boundary

This judgment does not authorize:

- extractor rule changes;
- candidate schema compatibility bypass;
- source-truth acceptance;
- field-correctness claims;
- Docling baseline promotion;
- parser replacement;
- production integration;
- `FundDataExtractor` changes;
- report-generation usage;
- release/readiness/PR claims.

## Interpretation

The evidence proves a real-envelope mismatch, not source absence.

The zero direct coverage can be caused by one or more of:

- extractor label expectations not matching projected Docling text/table labels;
- table family or section context not matching extractor filters;
- row/column label paths not carrying the expected semantic labels;
- S1 current envelope being narrower than full-document representation;
- representation projection losing fields the synthetic tests assumed.

This gate does not isolate which cause dominates.

## Residual Owner

Next gate:

`Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Planning Gate`

Purpose:

- inspect actual projected text/table shapes for the four runnable samples;
- map extractor matcher expectations to observed candidate envelope structures;
- identify a minimal remediation plan;
- keep all outputs candidate-only and `NOT_READY`.

## Stop Condition

Do not proceed to:

- field contract stabilization;
- comparative correctness;
- production integration;
- baseline promotion.

Those gates remain blocked until a diagnostic/remediation gate shows non-zero, reviewable candidate-field coverage or provides a controller-accepted alternative route.

VERDICT: `ACCEPT_NEGATIVE_EVIDENCE_ROUTE_TO_REAL_ENVELOPE_MISMATCH_DIAGNOSTIC_NOT_READY`
