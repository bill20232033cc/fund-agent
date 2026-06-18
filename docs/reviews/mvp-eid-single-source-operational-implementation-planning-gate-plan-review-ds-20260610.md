# EID Single Source Operational Implementation Planning Gate — Plan Review (AgentDS)

Date: 2026-06-10

Gate: `EID Single Source Operational Implementation Planning Gate`

Reviewer: AgentDS

Role: independent plan reviewer (no source/test/README/control/design changes, no live EID/network/PDF/FDR/fallback/provider, no stage/commit/push/PR)

## Review Input

- `docs/reviews/mvp-eid-single-source-operational-implementation-planning-gate-startup-judgment-20260610.md`
- `docs/reviews/mvp-eid-single-source-operational-implementation-planning-gate-plan-20260610.md`
- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/repo-review-20260609-165959.md`
- Tracked source: `fund_agent/fund/documents/sources.py`, `repository.py`, `models.py`

## Checklist Result

### 1. Single-source EID with fallback_enabled=false

**PASS.** The plan explicitly targets `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`. Slice 1 changes `AnnualReportSourceOrchestrator(None)` default from `(EidAnnualReportSource, EastmoneyAnnualReportSource)` to exactly one `EidAnnualReportSource`. The metadata schema (§7) adds explicit source policy markers (`selected_source`, `source_mode`, `fallback_enabled`). Cache admissibility (§8/Slice 3) gates all reused entries on EID-only policy compliance.

Direct evidence confirmed: current default at `sources.py:590-593` is indeed `(EidAnnualReportSource, EastmoneyAnnualReportSource)`. The change to single-source is unambiguous in the plan.

**Minor concern on Slice 1 ambiguity:** The plan says "either reject `sources` tuples with length other than 1, or introduce an explicit test-only/migration-only helper that cannot be reached by default production adapter." The first approach (reject multi-source entirely) is simpler and has a smaller residual surface. The second approach opens a risk that the test-only helper leaks into production. The plan already has a stop condition for this (`§12 Slice 1 stop condition`), requiring controller decision before acceptance. **Not blocking.**

**Minor concern on Eastmoney class retention:** The plan says "Keep `EastmoneyAnnualReportSource` only as an unused deferred candidate if deletion is too broad; it must not be reachable from default production adapter." If the class stays, it should carry an explicit docstring or module-level comment stating it is a deferred future candidate, not current production. Without that marker, a future developer could easily wire it back. **Not blocking for planning; recommend adding a docstring constraint to the implementation slice.**

### 2. No Eastmoney/CNINFO/fund-company website modeled as current production fallback

**PASS.** §2 non-goals states "No Eastmoney, fund-company website/CDN, CNINFO or multi-source fallback production behavior." The plan removes Eastmoney from the production default tuple. Multiple sections reinforce that these are deferred candidates / historical evidence-intake routes only. §17 residual risk table explicitly lists "Eastmoney wrapper integrity bug remains in code if class is retained" as "Deferred future source-candidate/fallback risk only; not production-reachable under EID-only default." §19 optional live smoke gate also explicitly forbids fallback invocation.

### 3. FundDocumentRepository remains sole production annual-report access boundary

**PASS.** §3 inventory confirms `FundDocumentRepository.load_annual_report()` returns `ParsedAnnualReport` and is the public boundary. §8 states "FundDocumentRepository remains the only production annual-report read boundary." §6 identity validation contract states "No caller outside `fund_agent/fund/documents` may override identity status." §11 forbidden files lists `fund_agent/ui/`, `fund_agent/services/`, `fund_agent/host/`, `fund_agent/agent/` as forbidden for source/cache/parser access. §8 item 6 states "The repository must not expose local PDF paths to UI/Service/Host/renderer/quality gate beyond existing internal metadata."

### 4. No direct source/downloader/cache/parser calls from UI/Service/Host/renderer/quality gate

**PASS.** §11 forbidden files explicitly lists `fund_agent/ui/`, `fund_agent/services/`, `fund_agent/host/`, `fund_agent/fund/extractors/`, `fund_agent/fund/pdf/parser.py`, `fund_agent/fund/pdf/downloader.py`, `render/`. §11 forbidden actions include "invoking `FundDocumentRepository.load_annual_report()` against real sources" and "live EID/network/PDF/FDR/fallback/provider/curl/DNS/socket/probe/smoke." The allowed files (§10) are restricted to `fund_agent/fund/documents/` and tests.

**Minor concern on downloader.py carve-out:** The plan says `fund_agent/fund/pdf/downloader.py` is forbidden "unless controller explicitly accepts a separate Eastmoney/downloader integrity gate." This is correct, but the plan could be strengthened by noting that the Eastmoney integrity misclassification finding from the repo review (P1 finding) exists in that file and must NOT be fixed in this gate — doing so would be scope drift into Eastmoney source behavior. **Recommend adding this note to Slice 1 or forbidden files section.**

### 5. Failure classification: fail-closed for schema_drift/identity_mismatch/integrity_error; terminal not_found/unavailable in single-source mode

**PASS.** §9 failure category matrix is explicit:

| Failure | Terminal? | Fallback? |
|---|---|---|
| `not_found` | Yes | No |
| `unavailable` | Yes | No |
| `schema_drift` | Yes | No |
| `identity_mismatch` | Yes | No |
| `integrity_error` | Yes | No |

The plan correctly identifies that in single-source mode with exactly one source and no multi-source construction allowed, `not_found` and `unavailable` become terminal by construction — there is nowhere to fall back to. §6 EID PDF integrity contract correctly distinguishes `unavailable` (HTTP 5xx, timeout, transport error) from `integrity_error` (200 OK with non-PDF content).

Confirmed: current `_FALLBACK_ELIGIBLE_CATEGORIES` at `sources.py:40` allows `not_found`/`unavailable` for fallback. The plan's approach of rejecting multi-source construction is the correct way to terminalize these without changing the category definitions themselves.

**Finding:** The `_can_fallback_after_failure()` function may still exist post-implementation even though it can never be reached by the single-source production path. Recommend either removing it or adding an assert/guard that confirms single-source invariant before checking eligibility. **Not blocking for planning; implementation detail.**

### 6. No-live validation matrix completeness; no live smoke as acceptance

**PASS.** §14 has a comprehensive no-live validation matrix:

- Source policy tests (pytest with `httpx.MockTransport`)
- Repository/cache tests (temp cache only)
- Boundary regression tests
- Broader local regression
- Lint (ruff check)
- Whitespace (git diff --check)
- Forbidden path audit (git diff --name-only)
- Docs grep for fallback wording

§14 forbidden validation section explicitly bans live acquisition, curl/DNS/socket/browser/network/PDF smoke, fallback invocation, and provider/LLM commands. §19 optional live EID smoke gate is explicitly designated as "not part of implementation acceptance" requiring separate user authorization.

**One gap:** The validation matrix does not include a check that `git diff --name-only` does NOT include `fund_agent/fund/pdf/downloader.py` (which is listed as forbidden unless controller accepts a separate gate). This is covered by the broader forbidden path audit, but could be made explicit. **Minor.**

### 7. Allowed/forbidden files reasonableness; scope drift / over-design

**PASS with findings.** The allowed files (§10) are correctly scoped to the documents layer:

- `fund_agent/fund/documents/models.py` — metadata schema
- `fund_agent/fund/documents/sources.py` — source orchestration
- `fund_agent/fund/documents/repository.py` — cache admissibility
- `fund_agent/fund/documents/adapters/annual_report_pdf.py` — wording only
- `fund_agent/fund/documents/cache.py` — additive serialization only
- Tests and docs

The forbidden files (§11) correctly exclude extractors, parser, downloader, UI, Service, Host, agent, render, golden/readiness/residual artifacts.

**Finding 1 (cache.py scope):** Slice 3 allows `fund_agent/fund/documents/cache.py` "only if helper placement requires it." The constraint ("no SQLite table migration expected") is correct, but this permission should be tightened: cache.py changes in this gate must be strictly additive serialization helpers and must not touch storage schema, cache eviction, or cache file layout. **Not blocking.**

**Finding 2 (discovery_contract_version):** The `discovery_contract_version` metadata field (§7) is a forward-looking versioning field. It's harmless as an additive string and may be useful for future EID contract evolution, but the plan could note that it's optional future-proofing. **Minor, not blocking.**

**Finding 3 (no scope drift detected):** The plan correctly excludes tool-loop, provider, renderer, golden/readiness, multi-year, and other unrelated scope. Slice 5 documentation sync is properly sequenced to happen only after implementation and review acceptance, not before.

### 8. Correct handling of fund_agent/tools/ and scripts/claude_mimo_simple.py residue

**PASS.** §2 non-goals: "No use of `fund_agent/tools/` or `scripts/claude_mimo_simple.py` as architecture truth, implementation input, validation input or evidence." §11 forbidden files explicitly lists both paths. §14 validation matrix includes `git diff --name-only` check that must not include these paths. The direct evidence matrix (§15) references the startup judgment ignore boundary.

No plan section references or depends on these paths. Confirmed: neither path appears in allowed files, implementation slices, or validation commands.

## Direct Evidence Cross-check

| Plan claim | Evidence verified? |
|---|---|
| Default sources are EID + Eastmoney | Yes — `sources.py:590-593` |
| fallback eligible categories allow not_found/unavailable | Yes — `sources.py:40` |
| Repository caches parsed/PDF without source policy check | Yes — `repository.py:322-385` |
| Source metadata lacks selected_source/source_mode/fallback_enabled | Yes — `models.py:24-129` |
| Eastmoney wrapper masks PDF integrity as unavailable | Yes — repo review P1 finding confirmed |
| EID source has discovery/identity/PDF integrity primitives | Yes — plan maps to `sources.py:31-39,356-412,940-1174` |

All key evidence claims in the plan's direct evidence matrix (§15) are verifiable against current tracked source. No evidence fabrication detected.

## Constructive Challenge: Adversarial Scenarios

1. **What if a future developer reads the `_can_fallback_after_failure` function and assumes fallback is supported?** Mitigation: single-source invariant enforced at construction; function becomes unreachable dead code. Recommendation: remove or guard the function in implementation.

2. **What if stale legacy Eastmoney cache has the same fund/year as a new EID request, and the cache key collides?** The plan addresses this: cache admissibility checks source metadata, not just key matching. A legacy Eastmoney cache hit would have `source != "eid"` or `fallback_used=True` and would be rejected.

3. **What if EID `validate_fund.do` returns `isSuccess=True` but `fundId` is an empty string?** §4 step 3 handles this: missing/non-object/non-JSON/invalid `fundId` → `schema_drift`. Good.

4. **What if EID search returns one candidate that matches fund code but has `reportDesp != "年度报告"`?** §5 identity validation table: `reportDesp` must be `年度报告`, mismatch → `identity_mismatch`. Correct.

5. **What if EID PDF download returns 200 with `Content-Type: text/html`?** §6: normalized media type must equal `application/pdf`; otherwise `integrity_error`. Correct.

6. **What if a test accidentally uses the real `EidAnnualReportSource` instead of a fake?** §13/§14 validation commands use `httpx.MockTransport` explicitly. The plan's no-live tests per slice (§13) specify test files and assertion types. Good.

## Reviewer Checklist Summary

| # | Item | Verdict |
|---|---|---|
| 1 | Single-source EID, fallback_enabled=false | PASS |
| 2 | No Eastmoney/CNINFO/fund-company as production fallback | PASS |
| 3 | FundDocumentRepository sole annual-report boundary | PASS |
| 4 | No direct source/downloader/cache/parser from upper layers | PASS |
| 5 | schema_drift/identity_mismatch/integrity_error fail-closed; not_found/unavailable terminal | PASS |
| 6 | No-live validation matrix complete; no live smoke as acceptance | PASS |
| 7 | Allowed/forbidden files reasonable; no scope drift or over-design | PASS (with minor findings) |
| 8 | fund_agent/tools/ and scripts/claude_mimo_simple.py correctly ignored | PASS |

## Findings

All findings are non-blocking; the plan is code-generation-ready.

### F1 (Minor) — Slice 1 multi-source ambiguity

The plan offers two approaches for enforcing single-source invariant: reject multi-source tuples, or provide a test-only helper. The reject approach is simpler and safer. The plan already has a stop condition requiring controller decision before Slice 1 acceptance.

**Recommendation:** Default to rejecting multi-source construction. If a test-only injection path must exist, add an explicit `_TEST_ONLY` naming convention and a runtime guard that asserts it cannot be reached from `AnnualReportPdfAdapter()` default.

### F2 (Minor) — Eastmoney class survival documentation

If `EastmoneyAnnualReportSource` is retained as "unused deferred candidate," it should carry an explicit docstring: "Deferred future fallback candidate; not production-reachable under current EID single-source policy." Without this, future developers may wire it back.

**Recommendation:** Add this constraint to the Slice 1 implementation requirements.

### F3 (Minor) — downloader.py forbidden carve-out language

The plan says `fund_agent/fund/pdf/downloader.py` is forbidden "unless controller explicitly accepts a separate Eastmoney/downloader integrity gate." This could be strengthened by noting that the repo review P1 finding exists in that file and must NOT be addressed in this gate — Eastmoney integrity hardening is a separate deferred risk.

**Recommendation:** Add a note to §11 or Slice 1 acknowledging the repo review P1 finding and explicitly prohibiting its fix in this gate.

### F4 (Minor) — Cache.py scope constraint

Slice 3's allowance of `cache.py` changes could be tightened to explicitly forbid storage schema changes, cache eviction logic, or cache file layout changes. Only additive serialization helpers should be permitted.

**Recommendation:** Tighten the Slice 3 allowed-files constraint for cache.py.

### F5 (Trivial) — discovery_contract_version field

The `discovery_contract_version` metadata field is future-proofing. It is harmless as an additive string field.

**Recommendation:** None required; accept as is.

## Residual Risk Assessment

The plan's residual risk table (§17) is complete and honest:

| Plan residual | Reviewer assessment |
|---|---|
| No live EID proof | Correctly deferred to separate live gate |
| Legacy cache ignored → first run re-fetches | Acceptable operational consequence |
| Share-class codes may not match | Correctly deferred to EID identity follow-up |
| Eastmoney integrity bug in retained class | Deferred risk; not production-reachable |
| Exception naming mentioning fallback | Legacy naming acceptable if no fallback exists |
| Metadata schema additive / cache JSON-tolerant | Policy admissibility is the security boundary, correct |

No additional residual risks identified beyond those in the plan.

## Verdict

**PASS_WITH_FINDINGS**

The plan is code-generation-ready. All 8 review items pass. Five non-blocking findings (F1-F5) are documented above. The plan correctly implements the startup judgment's single-source discipline, maintains `FundDocumentRepository` as the sole boundary, prohibits fallback, requires fail-closed failure classification, uses only no-live validation, has reasonable scope boundaries, and correctly ignores the residue paths. No implementation, source change, test change, live acquisition, or commit/push/PR action is authorized by this review.
