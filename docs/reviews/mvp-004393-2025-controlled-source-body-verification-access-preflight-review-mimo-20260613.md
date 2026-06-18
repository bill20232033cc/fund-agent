# MiMo Review: 004393 / 2025 Controlled Source-body Verification Access Preflight

Date: 2026-06-13

Reviewer: MiMo (access-preflight reviewer)

Reviewed target: `docs/reviews/mvp-004393-2025-controlled-source-body-verification-access-preflight-20260613.md`

Gate: `004393 / 2025 Controlled Source-body Verification Gate`

## 1. Review Scope

Review the access preflight artifact for correctness against four lenses:

1. Is the preflight correct that public repository load is not cache-only and may fall through to fetch_pdf/fetch_pdf_path?
2. Is it correct to block source-body verification without no-new-live proof or separate live authorization?
3. Does the artifact preserve repository boundary and avoid direct filesystem/PDF proof?
4. Are recommended next entries correct and not overbroad?

## 2. Source of Truth

- `AGENTS.md`: repository-boundary rule (line 76-77), annual-report source policy
- `docs/implementation-control.md`: current gate classification and access-preflight requirement
- `docs/current-startup-packet.md`: current gate scope and non-goal boundaries
- `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-controller-judgment-20260613.md`: controller verdict requiring source-body verification first

## 3. Code Facts Verified

| Fact | Source | Finding |
|---|---|---|
| `load_annual_report(force_refresh=False)` fall-through chain | `repository.py:350-398` | parsed cache → PDF cache → `fetch_pdf()`/`fetch_pdf_path()` |
| EID single-source policy check location | `repository.py:354`, `:372` | Repository layer, not cache layer; `_is_current_eid_single_source_metadata()` |
| Cache without EID policy is rejected | `test_repository.py:912-954` | `test_repository_rejects_parsed_cache_without_current_eid_policy` confirms fall-through on stale cache |
| Force refresh bypasses all cache | `test_repository.py:630-671` | `test_repository_force_refresh_bypasses_cached_pdf_and_parsed_report` |
| Cache-miss triggers fetch | `test_repository.py:590-627` | First load calls `fetch_pdf`, second load hits parsed cache |
| Public repository API surface | `repository.py:294-418` | Only `load_annual_report()` is public; cache methods are internal |
| Cache `load_parsed_report()` has no EID policy check | `cache.py:434-492` | Checks schema version and `is_parsed_annual_report_cache_usable()` only |

## 4. Assumptions Tested

| Assumption | Verdict | Evidence |
|---|---|---|
| Public `load_annual_report()` may trigger network fetch | CONFIRMED | `repository.py:378-393`: when PDF cache is absent or fails EID policy check, `fetch_pdf()` or `fetch_pdf_path()` is called |
| No public no-new-live/cache-only method exists on `FundDocumentRepository` | CONFIRMED | `repository.py:294-418`: class exposes only `load_annual_report()` |
| Cache layer alone cannot prove no-new-live availability | CONFIRMED | `cache.py:434-492`: `load_parsed_report()` does not enforce EID single-source policy; policy enforcement is in repository layer |
| Repository boundary is the correct proof boundary | CONFIRMED | `AGENTS.md:76-77`: "生产年报 PDF 访问必须经过 FundDocumentRepository" |

## 5. Findings

No material findings.

The preflight correctly identifies:

- PF1: Repository load is not cache-only; fall-through to fetch is real and test-confirmed.
- PF2: No public no-new-live method exists; cache methods are internal and lack EID policy enforcement.
- PF3: Internal cache returns full `ParsedAnnualReport`, not an availability-only signal.
- PF4: Tests confirm cache hit/miss/fresh-fetch behavior.
- PF5: Current control truth requires repository-bounded no-new-live or separate live authorization.

The blocking logic is sound: no no-new-live path → cannot prove no-new-live → must not proceed without live authorization.

The repository boundary is preserved: artifact uses static code analysis only, no `load_annual_report()` call, no PDF directory inspection, no filesystem proof.

## 6. Open Questions

None.

## 7. Residual Risks

| Residual | Tracking |
|---|---|
| EID single-source policy enforcement is repository-layer-only; if a future caller bypasses repository and uses cache directly, policy would not be enforced | Low risk currently; `AGENTS.md:76` mandates repository boundary for production access |
| `is_parsed_annual_report_cache_usable()` checks raw text length and section IDs but not source provenance | By design; provenance check is repository-layer responsibility |

## 8. Next Entry Recommendation

The preflight's three recommended next paths are correctly scoped and aligned with the controller judgment:

1. **Controlled live EID sub-slice**: Requires explicit user authorization; must keep repository boundary; must verify only the seven accepted candidate rows. Correct.
2. **Repository cache-only contract gate**: Would be a separate reviewed implementation gate adding a public no-new-live method. Correct.
3. **Data-source artifact authorization gate**: Explicitly notes reconciliation with `AGENTS.md` repository-boundary rule before use. Correct and not overbroad.

Path 1 is the recommended mainline per the controller judgment's "first perform a planning/access-preflight step" directive.

## 9. Verdict

**PASS**

The access preflight is correct on all four review lenses. No material findings. The artifact preserves repository boundary, correctly identifies the fall-through risk, correctly blocks source-body verification without live authorization, and recommends appropriately scoped next entries.
