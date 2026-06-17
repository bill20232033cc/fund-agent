# Docling Dedicated Extractor Template-field Mapping Plan Controller Judgment - 2026-06-17

Gate: `Docling Dedicated Extractor Template-field Mapping Planning Gate`
Role: controller
Status: `PLAN_ACCEPTED_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`
Verdict: `ACCEPT_PLAN_READY_FOR_DOCLING_DEDICATED_EXTRACTOR_IMPLEMENTATION_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Plan: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-20260617.md`
- DS plan review: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-review-ds-20260617.md`
- MiMo plan review: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-review-mimo-20260617.md`
- DS targeted re-review: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-rereview-ds-20260617.md`
- MiMo targeted re-review: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-rereview-mimo-20260617.md`
- Prior blocked evidence checkpoint: `edf1c68`

## Decision

Accept the plan for the next no-live implementation gate.

Controller basis:

- User explicitly redirected away from the Docling baseline-judgment / residual-closure optimization route toward direct Docling + dedicated extractor development.
- The accepted evidence checkpoint `edf1c68` proves the previous residual-closure route remains blocked by missing comparable producer diagnostics and cannot interpret `13 / 4` vs `10 / 7`.
- DS review verdict: `PLAN_REVIEW_PASS_NOT_READY`.
- MiMo review verdict: `PLAN_REVIEW_PASS_NOT_READY`.
- The plan was amended to fix non-blocking implementation ambiguities:
  - exact `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS` dot-notation strings;
  - explicit missing-field emission for paths not implemented in the first pass;
  - explicit relationship to `evidence_anchor_mapping.py` and candidate-only anchor boundary.
- DS targeted re-review verdict: `REREVIEW_PASS_NOT_READY`.
- MiMo targeted re-review verdict: `REREVIEW_PASS_NOT_READY`.
- `git diff --check` passed for plan and review artifacts.

## Accepted Transition

Suspend the old mainline question:

`Can Docling be judged/promoted as a baseline through residual closure?`

Enter the new mainline question:

`Can a Docling-specialized extractor map candidate annual-report representation into analysis-report template target fields with anchors, explicit missing values, and fail-closed semantics?`

This transition does not claim that Docling is source truth, a production parser replacement, or release-ready. It only changes the next development target.

## Accepted Next Implementation Scope

Next gate:

`Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`

Allowed implementation files:

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md`

Optional only if required by tests:

- `fund_agent/fund/documents/candidates/__init__.py`

Accepted implementation constraints:

- consume `CandidateRepresentationDocument` directly;
- do not consume `CandidateEvidenceAnchorMappingResult`;
- do not return production `EvidenceAnchor`;
- emit candidate-only `CandidateTemplateField` records;
- emit exactly one result for every default target field path;
- emit explicit `extraction_mode="missing"` for unimplemented or unmatched paths;
- preserve `candidate_only=true`, `source_truth_status="not_proven"`, and `NOT_READY`.

## Boundary Decision

Not authorized in the next implementation gate:

- modifying `FundDataExtractor`;
- integrating with production report generation;
- changing Service/UI/Host/renderer/quality-gate behavior;
- running live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- direct PDF/cache/source-helper access;
- fresh Docling conversion or repository reload;
- source truth acceptance;
- Docling baseline promotion;
- parser replacement;
- full field correctness;
- golden readiness, release readiness, or PR readiness.

## Validation

Controller validation:

```text
git diff --check -- docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-review-ds-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-review-mimo-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-rereview-ds-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-rereview-mimo-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-controller-judgment-20260617.md
```

Result: pass.

## Residual Risks

- The accepted implementation gate will produce a candidate extractor with no production consumption path. That is intentional for this step; integration requires a later gate.
- `docs/implementation-control.md` still names an older active gate. This judgment records the transition, but control-doc sync remains a later controller/documentation gate.
- Field correctness, source truth, baseline promotion, and report-generation quality remain unproven.

## Controller Self-check

- Current role: controller acceptance after plan review, targeted amendment, and re-review.
- Source of truth: user redirect, accepted blocked evidence checkpoint `edf1c68`, current plan, DS/MiMo reviews and re-reviews, code facts from `StructuredFundDataBundle`, `SNAPSHOT_FIELD_ORDER`, and candidate representation models.
- Scope boundary: controller judgment artifact only; no implementation, no control-doc sync, no production integration, no readiness/release/PR action.
- Validation: diff check passed.
- Stop conditions: no material blocking findings remain.
- Next action: create local accepted plan checkpoint.

VERDICT: `ACCEPT_PLAN_READY_FOR_DOCLING_DEDICATED_EXTRACTOR_IMPLEMENTATION_NOT_READY`
