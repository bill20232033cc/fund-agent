# Docling Field Correctness Anchor Coverage No-live Implementation Plan Review (DS) - 2026-06-16

Gate: `Docling Field Correctness Anchor Coverage No-live Implementation Planning Gate`
Role: AgentDS review worker
Release/readiness: `NOT_READY`

## Scope Reviewed

- Plan artifact: `docs/reviews/docling-field-correctness-anchor-coverage-no-live-implementation-plan-20260616.md`
- Controller judgment: `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-controller-judgment-20260616.md`
- Root-cause evidence: `docs/reviews/docling-field-correctness-anchor-coverage-root-cause-evidence-20260616.md`, `anchor_coverage_root_cause_matrix.json`
- Current code: `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` (verified: `_duplicate_sections`, `_unindexed_section_boundary_pages`, `_section_spans`, `_build_section_index`, `section_for_pages` all exist)
- Current tests: `tests/fund/documents/test_docling_evidence_anchor_mapping.py` (28 test functions, verified)

## Review Criteria Assessment

### 1. 72/72 justified only as local blocker closure, not readiness

**PASS.** Plan Section 2 explicitly states `72 / 72` is not release-readiness proof. Required invariants include `candidate_field_correctness_status=not_proven`, `source_truth_status=not_proven`. Section 6 Slice C mandates `candidate_only=True`. Section 8 evidence JSON requires all four negative guard flags. The existing `CandidateEvidenceAnchorMapping.__post_init__` at lines 137-145 already enforces these at object level — the plan preserves these checks.

### 2. Partial >44/72 correctly treated as residual, not full closure

**PASS.** Three-tier targeting: strong `72/72`, minimum `>44/72` with mandatory closed residual classification, and regression stop at `<44` or S5 `<17`. Section 8 requires `PARTIAL_IMPROVEMENT_NOT_READY` with exact residual routing if strong target not met. Section 10 stop condition prevents unclassified residual rows from being silently accepted.

### 3. Exact write set is bounded

**PASS.** Two implementation files (`evidence_anchor_mapping.py`, `test_docling_evidence_anchor_mapping.py`), two evidence files, one conditional doc file (`fund_agent/fund/README.md` only if behavior changes). No edits to `representation_projection.py`, `representation_models.py`, source policy, EvidenceAnchor schema, or any other module. Section 4 non-goals explicitly exclude all external boundaries.

### 4. Both duplicate_section_heading=16 and missing_section_context=12 addressed

**PASS.**

Slice A (16 rows): six-condition deterministic duplicate classification replacing binary block. Same-page duplicates remain blocked (condition 5), non-monotonic cases remain blocked (condition 3), competing sections on same page remain blocked (condition 6). Defaults to blocked on any condition failure.

Slice B (12 rows): six-condition span boundary adjustment. Unindexed boundaries only close spans when classified as hard unsupported top-level boundaries (condition 2). Unknown/unparseable nodes inside stable spans must not block in-report tables (condition 3). Multi-page crossing and outside-all-spans cases remain blocked (conditions 5, 6).

Both slices preserve existing fail-closed behavior for genuinely ambiguous cases.

### 5. S6-F041 caution handled fail-closed

**PASS.** Plan Section 2: S6-F041 may stay in target only after validating the reference-side `benchmark` assignment is intentional. If not validated, it must become a scope exception. Section 10 stop condition: implementation stops if S6-F041 cannot be validated and no reduced-scope controller decision exists. Default is fail-closed.

### 6. Candidate-only boundaries remain

**PASS.** Section 6 Slice C mandates `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"`, no production `EvidenceAnchor` construction. These are enforced by `__post_init__` which is unchanged. Proposed changes affect only internal section index logic — which cells map vs block, not what a mapping result looks like.

### 7. Tests and validation are sufficient

**PASS.** Eight test cases covering Slice A positive/negative, Slice B positive/negative, and Slice C boundary regression. Plan correctly instructs updating old test assertions with comments where old behavior was the accepted root cause, while preserving fail-closed tests that remain valid. Validation commands are the standard three: pytest, json.tool, git diff --check.

### 8. No live/source/parser/release boundary crossed

**PASS.** Section 4 non-goals and Section 9 forbidden commands comprehensively exclude live/network/PDF/FDR/Docling/provider/LLM/readiness/release/PR, plus production EvidenceAnchor schema change, source policy change, and parser replacement. Implementation evidence regenerated from accepted local envelopes only.

### 9. Controller Judgment Compliance

**PASS.** All four explicit controller asks are addressed:

| Controller ask | Plan response |
| --- | --- |
| S6-F041 target inclusion | Validation-required, else scope exception |
| 72/72 vs narrower target | Strong target with minimum >44/72 and residuals |
| S5 positive-control protection | Must preserve 17/17, regression = stop condition |
| Broader blocked population scope | Implicitly out of scope (plan targets 28 reviewed facts) |

## Findings

| # | Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- | --- |
| F1 | INFO | Broader blocked candidate-cell population not explicitly scoped as out-of-scope or follow-up. Controller judgment asked for this decision. Plan implicitly limits scope to 28 reviewed-fact rows but does not state it. | Plan references only 28 rows; Section 3 write set unchanged | None for plan acceptance. Controller may add explicit scope statement. |
| F2 | INFO | No dedicated unit test named for S5 positive-control regression (17/17). The after-matrix evidence (Section 8) and stop condition (Section 10) provide detection, but a focused test would add deterministic protection. | Section 7 lists 8 test cases, none explicitly named for S5 regression | Optional. Evidence matrix + stop condition are sufficient for this gate. |
| F3 | INFO | Slice B hard-vs-soft boundary classification criteria deferred to implementer. Conditions 1-6 constrain the implementation, but the exact mechanism distinguishing "hard unsupported top-level boundary" from "unknown/unparseable section node inside stable span" is not specified. | Section 6 Slice B condition 2 | Implementation gate should verify classification is deterministic and testable. |

## Verdict

```text
REVIEW_PASS_NOT_READY
```

Summary: plan correctly bounds `72/72` as local blocker closure, treats partial improvement as residual requiring closed classification, limits write set to two source files, addresses both blocked reasons with dedicated slices, handles S6-F041 fail-closed, preserves candidate-only invariants, specifies sufficient tests, and crosses no live/source/parser/release boundary. Three INFO findings, none blocking.
