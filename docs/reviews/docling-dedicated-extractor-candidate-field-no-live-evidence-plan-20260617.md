# Docling Dedicated Extractor Candidate-field No-live Evidence Plan - 2026-06-17

Gate: `Docling Dedicated Extractor Candidate-field No-live Evidence Gate`
Role: controller / evidence worker
Prior accepted implementation: `533fd63`
Status: `PLAN_READY_FOR_REVIEW_NOT_READY`
Release/readiness: `NOT_READY`

## Goal

Run the accepted Docling dedicated template-field extractor against accepted candidate representation JSON artifacts and produce durable no-live evidence for:

- field coverage;
- missing/deferred field distribution;
- candidate anchor availability;
- blocked input inventory;
- whether an integration planning gate is justified.

## First-principles Judgment

The previous implementation gate proved only that `extract_docling_template_fields()` works on synthetic `CandidateRepresentationDocument` objects. Baseline progress requires evidence on accepted candidate representation artifacts before any production integration.

This gate is valid because it asks a narrower question than baseline promotion:

> Can the accepted candidate-only extractor produce usable candidate template fields from already accepted Docling candidate representation artifacts?

This gate must accept negative evidence. A low or zero hit rate is still a valid outcome and must be recorded as `NOT_READY`, not repaired by widening scope inside this gate.

## Non-goals

This gate will not:

- modify extractor rules;
- modify `FundDataExtractor`;
- generate fresh Docling conversions;
- access PDF/cache/source helpers directly;
- use live/network/provider/LLM/golden/readiness/release/PR commands;
- compare values with source truth;
- promote Docling to baseline;
- replace the production parser;
- claim field correctness, source truth, release readiness, or PR readiness.

## Input Artifacts

Runnable accepted Docling candidate representation envelopes:

| Sample | Fund | Year | Path |
|---|---:|---:|---|
| S1 | 004393 | 2025 | `reports/representation-json/004393_2025_docling_current_envelope.json` |
| S4 | 006597 | 2024 | `reports/representation-json/006597_2024_docling_full.json` |
| S5 | 017641 | 2024 | `reports/representation-json/017641_2024_docling_full.json` |
| S6 | 110020 | 2024 | `reports/representation-json/110020_2024_docling_full.json` |

Blocked / residual input:

| Sample | Path | Reason |
|---|---|---|
| S1 | `reports/representation-json/004393_2025_docling_full.json` | `project_candidate_representation()` rejects this older full JSON with `ValueError: unsupported candidate representation schema_version`; this gate must not add compatibility bypass. |

## Allowed Write Set

- `reports/docling-dedicated-extractor-candidate-field-no-live-evidence/20260617/template_field_coverage_matrix.json`
- `docs/reviews/docling-dedicated-extractor-candidate-field-no-live-evidence-20260617.md`
- `docs/reviews/docling-dedicated-extractor-candidate-field-no-live-evidence-controller-judgment-20260617.md`
- Plan/review artifacts for this gate under `docs/reviews/`.

## Execution Steps

1. Validate each runnable input by loading JSON and calling `project_candidate_representation(payload)`.
2. Reject any payload whose candidate status or parser replacement status crosses the accepted boundary.
3. Call `extract_docling_template_fields(document)` for each runnable Docling document.
4. Record per-sample:
   - source path;
   - sample id;
   - fund code;
   - year;
   - target field count;
   - direct count;
   - missing count;
   - blocked count;
   - anchor count;
   - direct field paths;
   - missing field paths;
   - blocked field paths;
   - diagnostics.
5. Record aggregate:
   - sample count;
   - total requested field slots;
   - total direct slots;
   - total missing slots;
   - total blocked slots;
   - total anchor count;
   - direct coverage ratio;
   - missing ratio;
   - per-field direct hit count.
6. Record blocked input inventory separately.
7. Write JSON matrix and markdown evidence.
8. Run validation:
   - `uv run pytest tests/fund/documents/test_docling_template_field_extraction.py -q`
   - no-live extraction command used to create the matrix;
   - `git diff --check -- <allowed write set>`.

## Success Signal

This gate passes when:

- every runnable accepted Docling candidate envelope is either processed or explicitly blocked with an error reason;
- coverage and anchor availability are quantified;
- evidence remains candidate-only and `NOT_READY`;
- no source-truth, field-correctness, parser-replacement, baseline, release, or PR claim is made;
- residual risks are classified with an owner gate.

The gate may pass with negative evidence. Negative evidence should block integration planning unless the controller explicitly assigns remediation to a later gate.

## Expected Interpretation Rules

- `direct` fields are candidate hits only, not correctness proof.
- `missing` fields are extractor/representation mismatch evidence, not proof that source text lacks the value.
- `blocked` inputs are excluded from coverage denominator but listed in the blocked inventory.
- S1 old full JSON schema residual must remain blocked; do not broaden `project_candidate_representation()` in this gate.

## Residual Risk Owners

Assigned to possible remediation gate:

- zero or low direct coverage caused by representation shape / section IDs / table family / label path mismatch;
- extractor rules requiring adaptation to real candidate envelope shapes.

Assigned to later field contract gate:

- stabilization of field path schema, multi-row values, missing reasons, and blocked reasons.

Assigned to later comparative correctness gate:

- value correctness against production truth or independent source truth.

Assigned to later integration gate:

- production projection to `ExtractedField` / `EvidenceAnchor`;
- quality-gate semantics;
- `FundDataExtractor` or report generation usage.

## Completion Report Format

The evidence artifact must end with one of:

- `CANDIDATE_FIELD_EVIDENCE_POSITIVE_NOT_READY`
- `CANDIDATE_FIELD_EVIDENCE_NEGATIVE_NOT_READY`
- `CANDIDATE_FIELD_EVIDENCE_BLOCKED_NOT_READY`

The controller judgment must decide whether to proceed to:

- remediation planning;
- field contract stabilization;
- integration planning;
- or blocked/no-go.

VERDICT: `PLAN_READY_FOR_REVIEW_NOT_READY`
