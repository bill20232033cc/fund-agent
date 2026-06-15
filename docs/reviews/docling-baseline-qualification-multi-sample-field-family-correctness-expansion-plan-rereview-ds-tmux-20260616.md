# Docling Multi-sample Field-family Correctness Expansion Plan Re-Review (DS, A1 Only) - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Expansion Plan Review Gate` (re-review, A1 only)
Role: AgentDS targeted re-review worker
Release/readiness: `NOT_READY`

## 1. Scope

Targeted re-review of finding A1 from the DS review artifact `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-review-ds-tmux-20260615.md`.

A1 identified ambiguity in the plan's reference-load availability check: "available without live" was not defined, and the DS review's originally suggested fix (check cached PDF at expected cache path) would have violated AGENTS.md hard constraint "对基金文档的存取，都应该只通过统一的文档仓库接口，禁止直接操作文件系统" (AGENTS.md:75).

Controller rewrite direction: the fix must close the ambiguity through a no-live same-source reference route — accepted same-source reference artifact OR `FundDocumentRepository` with no-refresh/no-live intent and `force_refresh=False` — without requiring direct cache path/PDF/source-helper inspection. If neither route is available, mark `blocked_reference_unavailable` with reason `no_no_live_reference_proof`.

This re-review assesses only whether the current plan text closes A1 through the correct repository-boundary-respecting route. No other findings are re-evaluated.

## 2. Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` (lines 75-77) | Hard constraint: fund document access through repository interface only, no direct filesystem |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` | Plan under review (current amended state) |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-review-ds-tmux-20260615.md` | Original DS review containing A1 |

## 3. A1 Closure Assessment

### A1 Recap

Original finding: the plan used ambiguous language "Required if reference load is available without live" (§3 table) and "If this would require live/network acquisition not already authorized, mark that sample `blocked_reference_unavailable`" (§9 step 7). These statements did not define what "available without live" means — cached PDF on disk? repository load attempt without network? — creating risk that the evidence worker either skips valid cached samples or attempts unauthorized live acquisition.

Original DS suggested fix: pre-check cached PDF existence at expected cache path before repository load. This suggested fix is now rejected by controller because inspecting cache paths violates the `FundDocumentRepository` boundary (AGENTS.md:75-77).

### Current Plan Assessment

The plan has been amended. Four locations now address reference availability:

**Location 1 — §3 preamble paragraph:**

> "Before evidence review, the future evidence worker must establish a no-live same-source reference route for each sample: either an accepted same-source reference artifact is available, or `FundDocumentRepository` can provide repository metadata/reference access with explicit no-refresh/no-live intent and `force_refresh=False`. If this cannot be proven from repository metadata or an accepted same-source reference artifact, mark the sample `blocked_reference_unavailable` with reason `no_no_live_reference_proof` and stop before selecting or reviewing facts for that sample."

**Location 2 — §5 reference availability paragraph:**

> "Reference availability must be clarified before evidence review. The future evidence worker must first prefer an accepted same-source reference artifact if one exists for the exact `(fund_code, document_year, report_type)`. If no such artifact exists, the worker may use only `FundDocumentRepository` with no-refresh/no-live intent and `force_refresh=False`, and must rely on repository metadata to prove the reference was available without live acquisition. The worker must not call source helpers, cache internals, direct PDF paths, `force_refresh=True`, or any operation that inspects or mutates source/cache implementation details. If no-live availability cannot be proven from repository metadata or an accepted same-source reference artifact, the sample must be marked `blocked_reference_unavailable` with reason `no_no_live_reference_proof`."

**Location 3 — §9 step 6:**

> "Clarify no-live same-source reference availability for each sample before fact selection. Use an accepted same-source reference artifact if available; otherwise use only `FundDocumentRepository` with no-refresh/no-live intent and `force_refresh=False`. Do not call source helpers, cache internals, direct PDF paths, `force_refresh=True`, live/EID acquisition, or any source/cache implementation detail. If no-live availability cannot be proven from repository metadata or an accepted same-source reference artifact, mark the sample `blocked_reference_unavailable` with reason `no_no_live_reference_proof` and stop fact selection for that sample."

**Location 4 — §10 stop conditions:**

> "no-live same-source reference availability cannot be proven from repository metadata or an accepted same-source reference artifact; in that case mark the sample `blocked_reference_unavailable` with reason `no_no_live_reference_proof` and stop before fact selection/review;"

**Schema alignment — §7 `samples[]` item:**

> `repository_load.no_live_reference_proof`: `"accepted_same_source_reference_artifact | repository_metadata_no_refresh | null"`
> `repository_load.reference_blocker_reason_or_null`: `"no_no_live_reference_proof | null"`

### Assessment

The ambiguity is resolved. All four locations consistently define:

1. **Two valid no-live routes**: accepted same-source reference artifact (preferred), or `FundDocumentRepository` with `force_refresh=False` relying on repository metadata.
2. **Explicit prohibitions**: "must not call source helpers, cache internals, direct PDF paths, `force_refresh=True`, or any operation that inspects or mutates source/cache implementation details" — this directly enforces the AGENTS.md repository boundary constraint.
3. **Standardized blocker reason**: `no_no_live_reference_proof` — used consistently across §3, §5, §9, §10, and the §7 schema.
4. **Sample matrix table** now reads "Required if no-live reference proof exists" instead of the original ambiguous "Required if reference load is available without live."

The fix respects the repository boundary. It does not require direct cache path inspection, source helper calls, or PDF path access. The evidence worker interacts only with `FundDocumentRepository` (with `force_refresh=False`) and accepted same-source reference artifacts. If neither route succeeds, the sample is correctly blocked.

**A1 is closed.**

## 4. Residuals

| Risk | Classification | Rationale |
|---|---|---|
| "Repository metadata" proof mechanism is abstract | Accepted residual | The plan requires the worker to "rely on repository metadata to prove the reference was available without live acquisition" but does not enumerate which repository metadata fields constitute proof. This is a reasonable abstraction — `FundDocumentRepository` owns its metadata contract, and enumerating fields in the plan would couple the plan to repository internals. The evidence worker will need to document which metadata fields were checked in the evidence artifact. |
| `force_refresh=False` behavior depends on repository implementation | Accepted residual | If `FundDocumentRepository` with `force_refresh=False` triggers a network call due to a cache miss, the evidence worker would have violated the no-live constraint through no fault of the plan. This is a repository implementation concern, not a plan defect. The plan correctly constrains what the worker may call. |

No amendment required. Both residuals are inherent to the repository abstraction and belong to repository implementation scope, not plan scope.

## 5. Verdict

`A1_CLOSED_READY_FOR_CONTROLLER_ACCEPTANCE_NOT_READY`

The plan's current text at §3, §5, §9 step 6, §10, and §7 schema consistently defines the no-live same-source reference route through the correct repository boundary. The original ambiguity is resolved without cache path inspection. No further plan amendments are needed for A1.
