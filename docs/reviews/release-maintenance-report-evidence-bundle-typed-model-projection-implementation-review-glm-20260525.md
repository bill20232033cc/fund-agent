# Release Maintenance ReportEvidenceBundle Typed Model / Projection Implementation Review (GLM)

> Date: 2026-05-25
> Reviewer: AgentGLM (independent code review)
> Gate: `typed ReportEvidenceBundle model/projection implementation`
> Scope: `fund_agent/fund/report_evidence.py`, `tests/fund/test_report_evidence.py`, `fund_agent/fund/README.md` minimal sync
> Truth sources: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, implementation plan `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md`

## Conclusion: PASS_WITH_FINDINGS

Implementation faithfully follows the accepted plan. All 13 stop conditions respected. Literal domains, frozen slotted dataclasses, deterministic IDs, preferred_lens projection, nav_data exclusion, DerivedCalculation shape-only, accepted_baseline non-derivation, and boundary compliance are all correct. Tests achieve 93% coverage (above 80% target). Two low-severity findings and no blocking issues.

---

## Verification Results

| Check | Result |
|---|---|
| pytest (23 tests, 3 parametrized) | 23 passed |
| Line coverage | 93% (615 stmts, 44 miss) |
| ruff check | All checks passed |
| Boundary rg (repo/PDF/cache/dayu/extra_payload) | Clean — only negative-test assertions |
| git diff --check | No whitespace errors |
| Concurrent test run (lens_application + extraction_snapshot) | Passed (0.37s) |

---

## Findings

### F1 (MEDIUM): Duplicate classified_fund_type gap loses fact reference

**Files**: `fund_agent/fund/report_evidence.py:1082-1091`, `1522-1532`

When `classified_fund_type` is missing from `basic_identity.value`, two independent code paths create a gap with identical `gap_id`:

1. `_read_classified_fund_type()` (line 1082) creates gap with `related_fact_id=None`
2. `_project_classified_fund_type_fact()` (line 1522) creates gap with `related_fact_id="fact:fund_type.classified_fund_type"`

`_deduplicate_gaps()` at line 767 keeps the first occurrence (no fact reference), silently discarding the second (which carries the explicit fact reference). The fact→gap link survives via `_gap_matches_fact` field_path matching (line 1844), but the gap→fact link (`related_fact_id`) is lost. This creates an asymmetric bidirectional reference: the fact references the gap, but the gap does not reference the fact.

**Impact**: Downstream consumers that walk from gaps to facts via `related_fact_id` will miss this link. Not a scoring or review-status correctness issue — `_attach_gap_refs_to_facts` compensates via field_path matching.

**Recommendation**: Either (a) remove the redundant gap creation in `_project_classified_fund_type_fact` when `classified_fund_type == "unknown"` and rely on the earlier gap from `_read_classified_fund_type`, or (b) let the later gap (with the fact reference) override the earlier one by reversing the dedup precedence, or (c) merge the two paths so only one gap is created with the fact reference.

### F2 (LOW): Uncovered validation branches in `_validate_projection_context`

**File**: `fund_agent/fund/report_evidence.py:957-971`

Seven `ValueError` guard paths are untested:

| Line | Condition |
|---|---|
| 957 | `run_id` empty or whitespace |
| 959 | `corpus_id` empty or whitespace |
| 961 | `corpus_id` malformed (not `ad_hoc` or `corpus:name:version`) |
| 963 | `fund_type_slot` not in supported types |
| 965 | `fallback_used=True` with `source_failure_category="none"` |
| 967 | `fallback_used=True` with fail-closed category |
| 969 | `source_boundary="external_official"` |

These guards prevent malformed contexts from reaching projection logic. Without tests, a future refactor could silently weaken these protections.

**Recommendation**: Add at least a parametrized test covering each ValueError path. Each test should assert the exact `ValueError` message matches.

### F3 (LOW): Uncovered review status fallback states

**File**: `fund_agent/fund/report_evidence.py:873-877`

Three review status states lack direct test coverage:

- `fact_prefill_generated` (line 874): reached when facts exist but `fact_review_status != "reviewed"`
- `repository_verified` (line 876): reached when no facts but document is verified
- `candidate` (line 877): the terminal fallback

All tests use `fact_review_status="reviewed"` and always produce facts, so these branches are never exercised. These are real states in the `ReviewStatus` lifecycle that consumers may encounter.

**Recommendation**: Add one test per uncovered state with appropriate context (e.g., `fact_review_status="not_reviewed"`, empty facts with verified document, empty facts with unverified document).

### F4 (LOW): Uncovered `_coerce_extraction_mode` fallback

**File**: `fund_agent/fund/report_evidence.py:1569`

When `extracted_field.extraction_mode` is not in the `ReportExtractionMode` Literal domain, the function silently returns `"missing"`. This is a conservative default but untested. A future upstream change introducing a new extraction mode string could silently suppress facts.

**Recommendation**: Add a test with an unknown extraction mode string and assert the fact's `extraction_mode` is `"missing"` and appropriate gaps/rejection behavior follows.

---

## Residual Risks (non-blocking)

| Risk | Notes |
|---|---|
| 7% uncovered lines (44 stmts) | Mostly validation guards, fallback statuses, and anchor-source edge cases. Acceptable for first slice; should be addressed before downstream gates depend on these paths. |
| `_is_blocking_gap` is maximally conservative | Line 2110: any gap with `gap_kind != "not_applicable"` AND `failure_category != "not_applicable"` is blocking. This may over-block when `not_reviewed` gaps with `not_reviewed_in_current_slice` are introduced at scale. Not a current problem; revisit when corpus coverage grows. |
| `taxonomy_pending` hardcoded to QDII-in-FOF | Line 1131: only `fund_type_slot == "fof_fund" and classified_fund_type == "qdii_fund"` triggers `taxonomy_pending`. Future fund-type additions (e.g., REITs, commodities) may need more generic taxonomy resolution. |
| Anchor section sanitization ASCII-only | Line 2227: only ASCII uppercase is lowered. Acceptable given current section IDs are `§N` format, but would miss non-ASCII uppercase in hypothetical future section identifiers. |

---

## Boundary Compliance

| Stop condition (plan §Boundaries) | Status |
|---|---|
| No direct PDF/cache/source/filesystem access | Clean |
| No `FundDocumentRepository` call | Clean |
| No parallel extraction path | Clean |
| No `extra_payload`/kwargs/free dict | Clean |
| No renderer changes | Clean |
| No FQ0-FQ6 changes | Clean |
| No fixture promotion | Clean |
| No `accepted_baseline` derivation | Clean — `ValueError` at line 971 |
| No `nav_data` facts | Clean — absent from `_FIELD_SPECS` |
| No `fund_agent/host` or `fund_agent/agent` | Clean |
| No `dayu.host` / `dayu.engine` | Clean |
| Fail-closed not treated as fallback-eligible | Clean — lines 221-223, 2008 |
| No automatic turnover/style-stability extraction | Clean |

## README Scope

README update is minimal and factual. Lines 89-97 describe `project_report_evidence_bundle()` accurately. Line 377 adds internal layer entry. Line 401 adds current boundary entry. No scope creep detected — no claims about future features, no renderer/FQ integration, no durable baseline promises.

## Imports Audit

Production imports in `report_evidence.py`:

- `fund_agent.fund.data_extractor.StructuredFundDataBundle` — legitimate consumption ✓
- `fund_agent.fund.extractors.EvidenceAnchor, ExtractedField` — legitimate consumption ✓
- `fund_agent.fund.fund_type.FundType` — legitimate consumption ✓
- `fund_agent.fund.template.contracts.LensKey` — legitimate consumption ✓
- `fund_agent.fund.template.lens_application.build_lens_application_plan` — legitimate consumption ✓
- Standard library only (`hashlib`, `json`, `re`, `unicodedata`, `collections`, `dataclasses`, `decimal`, `typing`) ✓

No imports of: FundDocumentRepository, PDF adapter, cache, source helpers, dayu, renderer, quality gate, Host, Agent runtime.

## ID Format Consistency

| ID type | Format | Deterministic |
|---|---|---|
| bundle_id | `reb:{fund_code}:{year}:{schema_version}:{run_id}` | Yes |
| document_id | `doc:{fund_code}:{year}:annual_report` | Yes |
| fact_id | `fact:{category}.{field_path}` | Yes |
| gap_id | `gap:{fund_code}:{year}:{gap_kind}:{field_path}:{reason_code}` | Yes |
| anchor_id | `anchor:{fund_code}:{year}:{source_kind}:{section}:{hash}[-N]` | Yes (collision suffix deterministic) |
| score_issue_id | `issue:{run_id}:{fund_code}:{year}:{chapter}:{dimension}:{hash8}` | Yes |

All ID builders produce stable output for identical inputs. Collision handling in anchor IDs uses sorted locator JSON for suffix ordering.

## State Machine Correctness

`derive_report_evidence_review_status` priority order is correct:

1. `rejected` (hard validation failure, mismatch, fail-closed source)
2. `expired` (schema revision)
3. `deferred` (unknown type, type gap, unknown/probe boundary, blocking gaps, partially reviewed, quality block)
4. `scoring_ready` (all preconditions met)
5. `fact_prefill_reviewed` (facts + reviewed)
6. `fact_prefill_generated` (facts + not reviewed)
7. `repository_verified` (no facts + verified document)
8. `candidate` (fallback)

No reachable state is skipped. `accepted_baseline` is excluded from derivation path and blocked at context validation. `scoring_ready` correctly requires all eight chapter refs, non-ad_hoc corpus, verified document, matching slot, reviewed facts, no blocking gaps, and no blocking score issues.

## Cross-Reference Integrity

- `_attach_gap_refs_to_facts`: matches via `related_fact_id` OR `field_path` OR qualified suffix. All three paths are correct.
- `_attach_score_issue_refs_to_facts`: matches via `field_path` or category-qualified path. Correct.
- `_attach_score_issue_refs_to_gaps`: matches via `gap_id in issue.data_gap_refs`. Correct.
- `_validate_score_issue_links`: validates gap refs exist, anchor refs exist, severity required for issue/blocked, pass vs blocking gap conflict, N/A semantics, chapter_summary semantics. All rules match the plan.

---

*GLM independent review completed 2026-05-25. No files modified, no commits made.*
