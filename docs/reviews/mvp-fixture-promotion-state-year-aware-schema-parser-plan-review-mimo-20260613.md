# Plan Review: Fixture Promotion State Year-aware Schema / Parser Planning Gate

Date: 2026-06-13

Reviewer: AgentMiMo (plan review worker)

Reviewed artifact: `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-20260613.md`

## Verdict

`PASS`

## Review Scope

7 review focus areas from controller directive, plus evidence-based cross-check
against source code, tests, control docs and accepted controller judgment.

## Findings

| # | Finding | Severity | Evidence | Recommendation |
|---|---------|----------|----------|----------------|
| F1 | Plan correctly scopes itself as planning-only with explicit non-goals in §2. | info | §2 non-goals; §11 stop conditions; §14 worker self-check. | No change. |
| F2 | Implementation-needed decision correctly distinguishes strict golden coverage (already year-aware) from fixture promotion (fund-code-only residual). | info | Source: `StrictGoldenCoverage.fund_years` at line 57; `_load_fixture_promotion_states` returns `dict[str, PromotionState]` at line 1222; controller judgment §2/§5. | No change. |
| F3 | Schema contract §6.1 is small, explicit and fail-closed: unknown top-level and entry keys are rejected, duplicate `(fund_code, report_year)` raises `ValueError`. | info | §6.1 required/allowed fields; §6.1 invariants. | No change. |
| F4 | `FixturePromotionStates` dataclass §6.2 makes identity scope explicit. No external caller depends on the old `dict[str, PromotionState]` return type — CLI and service pass `fixture_promotion_state_path: Path | None` only. | info | Grep: `_load_fixture_promotion_states` callers are internal to `golden_readiness_preflight.py` (lines 577, 585); CLI line 1409 passes path only. | No change. |
| F5 | Row derivation contract §6.3 correctly returns `fixture_promotion_legacy_fund_only` blocker for legacy-only state and does not treat legacy `promoted_fixture` as year-specific proof. | info | §6.3 step 7; §7 rejected behavior. | No change. |
| F6 | Legacy fund-code-only manifest handling §7 is fail-closed: legacy state goes to `legacy_fund_states`, never satisfies year-specific proof, no automatic `DEFAULT_REPORT_YEAR` mapping. | info | §7 legacy behavior; §7 rejected behavior. | No change. |
| F7 | Implementation slices are appropriately narrow. Slice 1 targets only parser and derivation; Slice 2 targets only tests; Slice 3 targets only README sync with stop condition. | info | §8 Slice 1/2/3 allowed files and stop conditions. | No change. |
| F8 | Tests §8 Slice 2 are value-level assertions covering all 5 required scenarios: matching year, wrong year, legacy fund-code-only, duplicate identity, unknown field. | info | §8 Slice 2 test descriptions and assert specifications. | No change. |
| F9 | Docs trigger §10 correctly follows repo rules: `fund_agent/fund/` change triggers Fund README; `tests/` change triggers tests README; control/design docs remain untouched. | info | §10; AGENTS.md docs trigger rules. | No change. |
| F10 | `promotion_identity` field is required with only one allowed value `"fund_year"`. This is a forward-compatible extension point — correct for v1 slice. | info | §6.1 entry fields. | No change. |
| F11 | Plan §4 explicitly allows controller to defer implementation if the next readiness path excludes fixture promotion proof. This preserves the defer option correctly. | info | §4 allowed defer condition. | No change. |
| F12 | Stop condition §11 for implementation worker correctly identifies the public contract risk: if callers outside `run_golden_readiness_preflight()` depend on the old dict shape, stop and route as public contract expansion. Verified: no external callers consume the parsed dict. | info | §11 stop conditions; grep result. | No change. |

## Evidence Cross-check

| Check | Result | Basis |
|---|---|---|
| Strict golden coverage is already year-aware. | Confirmed | `StrictGoldenCoverage.fund_years: frozenset[tuple[str, int]]` at line 57; `_load_strict_golden_coverage` populates `covered_fund_years` at line 1215; tests `test_preflight_blocks_strict_golden_absence_and_fund_miss` and `test_preflight_accepts_strict_golden_matching_year_and_reserves_partial_code` pass. |
| Current fixture promotion parser is fund-code-only. | Confirmed | `_load_fixture_promotion_states` returns `dict[str, PromotionState]` at line 1222; `_derive_fixture_promotion_state` uses `fixture_states.get(artifact.fund_code)` at line 1851. |
| Current fund-code-only parser cannot prove `004393 / 2025`-specific promotion. | Confirmed | Controller judgment §2/§5 accepted at `aaf7922`. |
| No tracked fixture promotion manifest exists in codebase (tests pass `fixture_promotion_state_path=None`). | Confirmed | All existing tests pass `None`; no fixture manifest migration needed. |
| `run_golden_readiness_preflight` is the sole consumer of `_load_fixture_promotion_states` return value. | Confirmed | Grep shows internal-only usage. |

## Accepted Items

| Item | Disposition |
|---|---|
| Plan is planning-only and does not implement. | ACCEPT |
| Implementation-needed decision for year-specific promotion proof. | ACCEPT |
| Strict golden coverage does not need new implementation. | ACCEPT |
| Schema contract §6.1 with `(fund_code, report_year)` identity. | ACCEPT |
| Internal parser shape `FixturePromotionStates` §6.2. | ACCEPT |
| Row derivation contract §6.3 with legacy fail-closed. | ACCEPT |
| Legacy manifest handling §7 as diagnostic-only. | ACCEPT |
| Implementation slices §8 with allowed files and stop conditions. | ACCEPT |
| Test specifications §8 Slice 2 with 5 value-level tests. | ACCEPT |
| Docs decision §10 following repo trigger rules. | ACCEPT |
| Next gate recommendation §13 as implementation gate after plan acceptance. | ACCEPT |

## Rejected Items

None.

## Deferred Items

None — all plan decisions are within the planning gate scope.

## Amendment Requirements

None. Plan does not require amendments.

## Gate Classification Assessment

Plan correctly identifies this as `standard` gate classification. The scope is
narrow (one module, two files plus READMEs), the contract change is
well-bounded, and the implementation slices are small. No upgrade to `heavy`
is needed because:
- No public contract is exported beyond `run_golden_readiness_preflight()`.
- No fixture/golden content is modified.
- No release/readiness state changes.

## Next Gate

Recommended next gate: `Fixture Promotion State Year-aware Schema / Parser Implementation Gate`

The implementation gate should target exactly the files listed in §5:
- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`
- `fund_agent/fund/README.md` (if triggered)
- `tests/README.md` (if triggered)

## Self-check

- Role: plan review worker, not controller.
- Source of truth: AGENTS.md, docs/current-startup-packet.md, docs/implementation-control.md, controller judgment, target source and target tests were read.
- Scope: only this review artifact is written.
- No source/test/runtime/golden/fixture/design/control docs modified.
- No live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release commands run.
