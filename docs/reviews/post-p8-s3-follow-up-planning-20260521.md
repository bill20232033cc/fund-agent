# Post-P8-S3 Follow-up Planning（2026-05-21）

## Current State

P8-S3 `source fallback policy` implementation is complete and committed at `93ae6ea`.

Accepted P8 commits:

- `f3bbfc9`：P8-S1 must_answer audit contract design plan/review
- `5f5a7a6`：P8-S1 must_answer audit contract implementation
- `f55ef76`：P8-S2 renderer preferred_lens application plan/review
- `6dbf6ca`：P8-S2 renderer preferred_lens application implementation
- `9b38a4d`：P8-S3 source fallback policy plan/review
- `93ae6ea`：P8-S3 source fallback policy implementation

Latest verified baseline:

```text
targeted -> 35 passed (sources), 52 passed (documents focused)
pytest -> 347 passed
ruff check -> passed
git diff --check -> passed
```

## P8 Scope Closure

P8 was defined as "模板契约与来源策略加固（must_answer audit / preferred_lens / source fallback）". All three named deliverables are now complete:

| Deliverable | Slice | Status |
|---|---|---|
| must_answer audit contract routing | P8-S1 | ✅ closed |
| renderer preferred_lens deterministic application | P8-S2 | ✅ closed |
| source fallback taxonomy and fail-closed policy | P8-S3 | ✅ closed |

## Residual Reconciliation

### Closed by P8-S1

- `R1. must_answer Audit Consumption` closed for deterministic contract-routing.
- `ContractAuditCoverageManifest` covers all 45 `must_answer` with explicit per-route classification.
- C2 marker granularity folded into P8-S1; no standalone blocker unless concrete audit weakness emerges.

### Closed by P8-S2

- `R2. Renderer preferred_lens Application` closed for deterministic renderer output.
- `LensApplicationPlan` is Capability-owned, renderer only applies normalized labels in Chapter 0/1 deterministic slots.
- Raw `TemplateLensRule.statements` are not rendered into final Markdown.

### Closed by P8-S3

- `R3. EID Schema Error Fallback Policy` closed.
- Five-category source failure taxonomy with table-driven fallback eligibility.
- `AnnualReportSourceFallbackBlockedError` provides structured provenance for fail-closed decisions.
- `AnnualReportSourceIntegrityError` separates PDF content failures from JSON/schema failures.

## Remaining Items After P8

### R4. Preflight Quality Gate Optimization（P8-S4）

Status: performance optimization, not correctness blocker.

Current fact:

- `analyze` currently performs extraction before single-fund quality gate.
- Some not-run/block outcomes could be detected from selected pool membership before extraction.
- Reordering can affect UX and artifact availability.

Assessment:

- P8-S4 is not named in the P8 phase definition.
- It is a Service-layer performance optimization that does not change audit semantics, source policy, or template contracts.
- It can proceed as a separate post-P8 optimization slice without blocking P8 closure.

Recommendation: defer to post-P8 planning as a P9-S1 candidate.

### R5. C2 Marker Granularity

Status: folded into P8-S1; no standalone blocker.

Current fact:

- P8-S1 `ContractAuditCoverageManifest` already classifies 45 `must_answer` into explicit routes.
- Only 0 `programmatic_marker` routes currently exist; 44 are `covered_by_required_item`, 1 is `narrative_guidance`.
- Granularity hardening should only happen when a concrete audit weakness is identified.

Recommendation: keep deferred unless concrete audit miss triggers re-evaluation.

### Open Repo Review Findings

From `docs/reviews/repo-review-mimo-20260520-235926.md`, remaining open items:

- 003: QDII/FOF shadows enhanced index classification → medium, fund_type classification refinement
- 005: quality gate CSV error silently swallowed → medium, error message clarity
- 006: alpha nature judgment receives empty holdings tuple → medium, Service-layer data wiring
- 008: non-atomic cache write → low, disk leak only
- 009: concurrent cache race → low, single-user CLI scenario
- 010: Service imports Capability constant → low, compile-time coupling

Assessment:

- These are cross-cutting concerns that span P5-P8 boundaries.
- None block P8 closure.
- 003 and 006 are medium-severity items suitable for a post-P8 maintenance slice.

## Controller Decision

P8 has delivered all three named objectives. Recommend:

1. **Close P8** with aggregate readiness reconciliation.
2. **P8-S4 preflight quality gate** becomes a P9-S1 candidate in post-P8 planning.
3. **Open repo findings** (003, 005, 006) become post-P8 maintenance slice candidates.
4. No P8 aggregate deepreview needed because P8-S1/S2/S3 each passed controller code review independently and the phase has no cross-slice integration surface beyond what individual reviews already covered.

## Verification Baseline

```bash
pytest
ruff check
git diff --check
```

Expected current baseline:

```text
347 passed
ruff passed
tracked worktree: P8-S3 related files committed; parallel slice files (fund_type.py, audit_programmatic.py, fund_analysis_service.py) remain in working tree
```

## Next Gate

```text
P8 aggregate readiness reconciliation -> P8 closed
```
