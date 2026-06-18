# Docling Dedicated Extractor Template-field Mapping Implementation Controller Judgment - 2026-06-17

Gate: `Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`
Role: controller
Accepted plan commit: `d48aa9f`
Status: `IMPLEMENTATION_ACCEPTED_NOT_READY`
Verdict: `ACCEPT_IMPLEMENTATION_READY_FOR_CANDIDATE_FIELD_EVIDENCE_GATE_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Accepted plan: `docs/reviews/docling-dedicated-extractor-template-field-mapping-plan-20260617.md`
- Implementation evidence: `docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md`
- Code review, AgentDS: `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-ds-20260617.md`
- Code review, AgentMiMo: `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-mimo-20260617.md`
- Code re-review, AgentDS: `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-ds-20260617.md`
- Code re-review, AgentMiMo: `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-mimo-20260617.md`

## Accepted Files

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-ds-20260617.md`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-mimo-20260617.md`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-ds-20260617.md`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-mimo-20260617.md`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-controller-judgment-20260617.md`

## Decision

Accept the no-live implementation slice.

The implementation is accepted only as a candidate-only Docling specialized extractor that maps `CandidateRepresentationDocument` into analysis-template target-field candidates. It does not establish source truth, parser replacement, baseline qualification, production integration, release readiness, or PR readiness.

## Accepted Facts

- The implementation adds `DOCLING_TEMPLATE_FIELD_SCHEMA_VERSION = "docling_template_field_candidates.v1"`.
- The implementation exposes `extract_docling_template_fields(document, target_field_paths=...)`.
- The implementation consumes Docling `CandidateRepresentationDocument` objects directly.
- The implementation rejects non-Docling candidate source kinds.
- The implementation rejects candidate documents that cross the accepted `not_proven` / `not_authorized` boundary.
- The implementation emits exactly one candidate field per requested target field path.
- The implementation emits explicit `extraction_mode="missing"` records for unmatched or deferred target paths.
- Candidate field outputs remain `candidate_only=True` and `source_truth_status="not_proven"`.
- Candidate anchors reject notes that do not start with `candidate_only:`.
- The implementation does not import or emit production `EvidenceAnchor`.
- The implementation does not modify `FundDataExtractor`.
- The implementation does not integrate with production report generation, quality gates, renderer, Service, UI, Host, or Agent runtime.

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py -q
```

Result:

```text
10 passed in 0.72s
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

Command:

```text
git diff --check -- fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-ds-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-review-mimo-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-ds-20260617.md docs/reviews/docling-dedicated-extractor-template-field-mapping-code-rereview-mimo-20260617.md
```

Result: pass.

## Review Disposition

AgentDS verdict: `CODE_REVIEW_PASS_NOT_READY`.

AgentMiMo verdict: `CODE_REVIEW_PASS_NOT_READY`.

Post-review hardening:

- `CandidateTemplateFieldAnchor.__post_init__` now fail-closes on non-`candidate_only:` notes.
- Tests now cover invalid `target_field_paths`.
- Tests now cover text-label fallback.
- Tests now cover direct anchor note rejection.

AgentDS re-review verdict: `CODE_REREVIEW_PASS_NOT_READY`.

AgentMiMo re-review verdict: `CODE_REREVIEW_PASS_NOT_READY`.

No blocking finding remains for this implementation slice.

## Residual Risks

Assigned to next gate, `Docling Dedicated Extractor Candidate-field No-live Evidence Gate`:

- The extractor has not been run against accepted candidate representation artifacts.
- Field-level coverage on real candidate documents is not measured.
- Field values are not compared with production truth or independent source truth.
- Missing/deferred field distribution is not quantified.

Assigned to later integration planning gate:

- The extractor is not consumed by `FundDataExtractor` or report generation.
- Production projection to `ExtractedField` / `EvidenceAnchor` is not designed or authorized.
- Quality-gate semantics for candidate fields are not designed or authorized.

Accepted implementation residuals:

- Holdings extraction currently returns the first matching row per holding target path.
- `blocked_field_paths` is reserved by the output schema but has no production trigger.
- Numeric normalization, unit conversion, multi-year semantics, QDII/FOF specifics, and full CHAPTER_CONTRACT coverage remain unproven.
- Target field path schema is a candidate contract and may require stabilization before integration.

## Boundary

This judgment does not authorize:

- source-truth acceptance;
- Docling baseline promotion;
- parser replacement;
- production integration;
- report-generation usage;
- golden/readiness/release/PR readiness;
- live/network/provider/LLM/golden commands.

## Next Gate

Recommended next gate:

`Docling Dedicated Extractor Candidate-field No-live Evidence Gate`

Purpose:

- run the accepted extractor against accepted candidate representation artifacts only;
- produce field coverage, missing/deferred distribution, anchor availability, and blocker inventory;
- keep all outputs candidate-only and `NOT_READY`;
- decide whether an integration planning gate is justified.

VERDICT: `ACCEPT_IMPLEMENTATION_READY_FOR_CANDIDATE_FIELD_EVIDENCE_GATE_NOT_READY`
