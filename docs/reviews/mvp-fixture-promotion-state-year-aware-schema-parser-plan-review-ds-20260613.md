# Plan Review: Fixture Promotion State Year-aware Schema / Parser Planning Gate

Date: 2026-06-13

Gate: `Fixture Promotion State Year-aware Schema / Parser Plan Review Gate`

Role: plan review worker (AgentDS), not controller

Reviewed artifact: `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-20260613.md`

Verdict: `PASS_WITH_AMENDMENTS`

Readiness: remains `NOT_READY` (unchanged; this is a plan review, not readiness gate)

## 1. Review Scope

This review checks whether the plan artifact is fit to route to an implementation gate.
This review does not implement code, does not modify source/tests/runtime/golden/fixture/control/design
docs, and does not claim release/readiness.

## 2. Evidence Basis

| Source | Relevance |
|---|---|
| `AGENTS.md` | Execution rules, gate classification, module boundaries, docs trigger rules |
| `docs/current-startup-packet.md` | Current gate definition, scope boundary, accepted facts |
| `docs/implementation-control.md` | Control truth, current gate state, non-goal reminder, residual tracking |
| Controller judgment `mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md` | Accepted evidence facts: strict golden is year-aware; fixture promotion is fund-code-only and blocks year-specific proof |
| `fund_agent/fund/golden_readiness_preflight.py` | Current implementation: `_load_fixture_promotion_states()` returns `dict[str, PromotionState]`, `_derive_fixture_promotion_state()` does fund-code-only lookup, `_build_readiness_row()` signature, `_PromotionStateSummary` shape |
| `tests/fund/test_golden_readiness_preflight.py` | Current test coverage: year-aware strict golden tests present, fixture promotion absence test present, no year-aware fixture promotion tests |

## 3. Findings

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| F1 | Plan is genuinely planning-only. Non-goals (§2), stop conditions (§11), worker self-check (§14) all correctly gate implementation. | `OK` | §2: "Do not implement source, test, runtime, golden, fixture, parser, schema or README changes"; §11: stop conditions explicitly forbid implementation | No action |
| F2 | Implementation-needed decision correctly separates strict golden (year-aware already, no work needed) from fixture promotion (fund-code-only, work required before year-specific proof). Matches controller judgment §4 exactly. | `OK` | Plan §4: "Strict golden coverage already checks exact `(fund_code, report_year)`" vs "Fixture promotion currently collapses entries to `fund_code`"; controller judgment rejects strict-golden implementation as `UNNEEDED_NOW` and routes fixture promotion to separate planning gate | No action |
| F3 | `promotion_identity` required field with exactly `"fund_year"` value is redundant as a schema-level guard. The identity contract is already enforced by: (a) `schema_version` discriminator, (b) `(fund_code, report_year)` parser keying, (c) unknown-field rejection, (d) duplicate-key rejection. Adding `promotion_identity` creates maintenance burden without adding independent protection. | `MODERATE` | Plan §6.1: "Required entry fields: promotion_identity: exactly `fund_year`"; the field asserts what is already true from the schema version and key structure | **Amendment A**: Controller decides: (a) keep `promotion_identity` as optional or required field with explicit rationale in plan §6.1, OR (b) remove it from the first slice and defer to a later schema evolution gate. If kept, the implementation must reject unknown values (already specified) and the test must cover a wrong-identity rejection case. |
| F4 | Row derivation contract (§6.3) defines blocker codes for each step but does not define the `state` output string (the `_PromotionStateSummary.state` field that becomes `FundReadinessRow.fixture_promotion_state`). For step 7 (legacy-fund-only-found), the output `state` must not be `"promoted_fixture"` or ambiguous; the plan §7 recommends `"unknown"` but this is stated in the legacy section, not in the contract steps. Implementation ambiguity risk. | `MODERATE` | Plan §6.3 steps 7-8 define blocker codes (`fixture_promotion_legacy_fund_only`, `fixture_promotion_unknown`) but the `state` output for each step is not explicit; plan §7 says "Output `promotion_state` should be `unknown` for legacy-only" but this is separate from the contract | **Amendment B**: Add an explicit `state` column to the §6.3 contract table or steps, mapping each step to its output `state` string. Recommended: step 4 → `"promoted_fixture"`, step 5 → `"not_promoted"`, step 6 → `"unknown"`, step 7 → `"legacy_fund_only"`, step 8 → `"unknown"`. The `_PromotionStateSummary.state` field must be populated accordingly. |
| F5 | Slice 1 Step 7 (§8.1) says "Keep strict golden coverage code unchanged except type references needed for the new parser shape." The type references are not enumerated. The affected call chain is: `run_golden_readiness_preflight()` line 577 `fixture_states = _load_fixture_promotion_states(...)` → `_build_readiness_row()` signature `fixture_states: dict[str, PromotionState] | None` → `_derive_fixture_promotion_state()` signature `fixture_states: dict[str, PromotionState] | None`. All three sites need explicit type change when `FixturePromotionStates` replaces `dict[str, PromotionState]`. | `MINOR` | Source code: `golden_readiness_preflight.py` lines 577, 1269, 1817; plan §8.1 step 7 | **Amendment C**: Replace "Keep strict golden coverage code unchanged except type references" with an explicit list: (a) `run_golden_readiness_preflight()` local variable `fixture_states` type annotation, (b) `_build_readiness_row()` parameter `fixture_states` type annotation, (c) `_derive_fixture_promotion_state()` parameter `fixture_states` type annotation and internal lookup logic. No other strict golden coverage code changes. |
| F6 | Schema contract (§6.1) is small, fail-closed, and correctly prevents legacy misuse. Unknown top-level and entry keys are rejected. Duplicate `(fund_code, report_year)` entries raise `ValueError`. No optional fields in first slice. Legacy manifest handling (§7) explicitly refuses silent migration, DEFAULT_REPORT_YEAR mapping, and year-specific proof from legacy state. | `OK` | Plan §6.1 invariants, §7 rejected behavior; consistent with existing `_reject_unknown_keys` pattern in the codebase | No action |
| F7 | Allowed implementation files (§5) match AGENTS.md docs trigger rules: `fund_agent/fund/` → `fund_agent/fund/README.md`, `tests/` → `tests/README.md`. Control/design docs correctly excluded. | `OK` | Plan §5; `AGENTS.md` §文档同步 trigger rules | No action |
| F8 | Planned tests (§8.2) are value-level assertions covering matching-year pass, wrong-year block, legacy fail-closed, duplicate rejection, and unknown-field rejection. Test helper `_write_fixture_promotion_state()` follows the existing `_write_golden()` pattern. | `OK` | Plan §8.2 tests 1-5; existing test helper patterns in `test_golden_readiness_preflight.py` | No action. If Amendment A keeps `promotion_identity`, add a test for wrong-identity rejection. |
| F9 | No overdesign detected. The `FixturePromotionStates` dataclass (§6.2) is minimal (two fields, both mappings), the schema has zero optional fields in first slice, and implementation is scoped to one source file plus tests. The `legacy_fund_states` field is justified by §7's diagnostic-only semantics. | `OK` | Plan §6.2, §7, §8 | No action |
| F10 | Public contract risk is acknowledged and routed. §8.1 stop condition: "If existing callers outside `run_golden_readiness_preflight()` depend on the old dict shape, stop and route as public contract expansion." The underscore-prefixed function names (`_load_fixture_promotion_states`, `_derive_fixture_promotion_state`) are internal convention, but the plan correctly gates on actual external usage. | `OK` | Plan §8.1 stop conditions; grep of codebase would confirm no external callers at implementation time | No action for plan; implementation worker must verify before changing |
| F11 | `DEFAULT_REPORT_YEAR` misuse is correctly rejected. Plan §7 explicitly refuses to map legacy fund-code-only entries to `(fund_code, DEFAULT_REPORT_YEAR)` and states "fund-code-only state is not year-aware even for 2024." However, the current static manifest (§3 of source) uses `DEFAULT_REPORT_YEAR = 2024` for all entries via `_entry()`. The plan does not address whether the new year-aware fixture promotion parser interacts with the static disposition manifest's use of `DEFAULT_REPORT_YEAR`. | `MINOR` | Plan §7 rejected behavior; source code `_entry()` always passes `report_year=DEFAULT_REPORT_YEAR`; `_complete_fund_artifacts()` uses `(entry.fund_code, entry.report_year)` as key | No amendment needed for plan, but implementation must ensure fixture promotion derivation for `004393 / 2025` does not inadvertently match a manifest entry keyed on `report_year=2024`. This is already prevented by the exact `(fund_code, report_year)` lookup contract. |
| F12 | Next gate recommendation (§13) correctly routes to plan review (this gate), then to narrow implementation gate. Implementation gate scope is correctly bounded: no fixture promotion, no golden content edits, no live/readiness/release commands. | `OK` | Plan §13; controller judgment §7 | No action |

## 4. Accepted / Rejected / Deferred

| Item | Disposition | Basis |
|---|---|---|
| Plan is planning-only, no implementation authorized | `ACCEPT` | F1 |
| Implementation-needed decision (strict golden: no work; fixture promotion: work required) | `ACCEPT` | F2 |
| Schema/parser contract scope and fail-closed design | `ACCEPT` | F6 |
| Allowed implementation files and docs trigger rules | `ACCEPT` | F7 |
| Test design (value-level assertions, five scenarios) | `ACCEPT` | F8 |
| Public contract risk acknowledgment and stop condition | `ACCEPT` | F10 |
| Next gate routing | `ACCEPT` | F12 |
| `DEFAULT_REPORT_YEAR` rejection in fixture promotion context | `ACCEPT` | F11 |
| `promotion_identity` field as redundant schema guard | `NEEDS_AMENDMENT` | F3; see Amendment A |
| Row derivation contract missing `state` output values | `NEEDS_AMENDMENT` | F4; see Amendment B |
| Vague "type references" in Slice 1 Step 7 | `NEEDS_AMENDMENT` | F5; see Amendment C |
| Overdesign claim | `REJECT` | F9; plan is appropriately minimal |
| Strict golden coverage implementation | `REJECT` (already in plan) | F2; plan correctly marks as not needed |
| Direct fixture promotion or golden content edit | `REJECT` (already in plan) | Plan non-goals §2 |
| Readiness/release/live/PR commands | `REJECT` (already in plan) | Plan non-goals §2 |
| Markdown dual-surface parity for fixture promotion | `DEFER` | Controller judgment §3 already deferred this for strict golden; not needed for fixture promotion schema/parser either |
| Historical fixture manifest runtime-consumability re-evidence | `DEFER` | Controller judgment §3 already deferred; plan §7 correctly handles legacy manifests without re-evidence |

## 5. Required Amendments (Controller-Adjudicable)

### Amendment A: `promotion_identity` field disposition

**Finding**: F3. The `promotion_identity` required field with exactly `"fund_year"` value is redundant because identity is already enforced by `schema_version`, `(fund_code, report_year)` keying, and unknown-field rejection.

**Required rewrite** (choose one, controller adjudicates):

Option A1 (keep): Add to plan §6.1 after the `promotion_identity` spec:

```markdown
Rationale for promotion_identity: schema_version alone does not prevent a
future manifest author from accidentally writing fund-code-only entries under
the year-aware schema version. Requiring promotion_identity == "fund_year" on
every entry makes identity intent explicit per-entry and fails closed on any
mismatch.
```

If A1 is chosen, also add a test: `test_preflight_rejects_year_aware_fixture_promotion_wrong_identity` — build manifest with `promotion_identity: "fund_code_only"` and assert `ValueError`.

Option A2 (remove): Delete `promotion_identity` from the required entry fields list in §6.1, from the schema JSON example, and from §8.1 step 4 parser validation steps.

### Amendment B: Explicit `state` output values in row derivation contract

**Finding**: F4. §6.3 defines blocker codes per step but not the `state` string that populates `FundReadinessRow.fixture_promotion_state`.

**Required rewrite**: In plan §6.3, replace steps 4-8 with a table or annotated steps that include both `blocker` and `state` outputs:

| Step | Condition | `state` output | `promotion_state` output | Blocker code |
|---|---|---|---|---|
| 4 | exact key is `promoted_fixture` | `"promoted_fixture"` | `promoted_fixture` | none |
| 5 | exact key is `not_promoted` | `"not_promoted"` | `not_promoted` | `fixture_promotion_absent` |
| 6 | exact key is `unknown` | `"unknown"` | `unknown` | `fixture_promotion_unknown` |
| 7 | exact key missing, legacy fund-code state exists | `"legacy_fund_only"` | `unknown` | `fixture_promotion_legacy_fund_only` |
| 8 | exact key missing, no legacy state | `"unknown"` | `unknown` | `fixture_promotion_unknown` |

### Amendment C: Explicit type reference changes in Slice 1 Step 7

**Finding**: F5. "type references needed for the new parser shape" is vague.

**Required rewrite**: Replace plan §8.1 step 7 with:

```markdown
7. Update type annotations at exactly three call sites to use
   `FixturePromotionStates | None` in place of `dict[str, PromotionState] | None`:
   a. `run_golden_readiness_preflight()` local variable `fixture_states`
      (line ~577).
   b. `_build_readiness_row()` parameter `fixture_states` (line ~1269).
   c. `_derive_fixture_promotion_state()` parameter `fixture_states`
      (line ~1817) and its internal lookup logic.
   No other strict golden coverage code, no other functions, no
   `_derive_strict_golden_coverage()` changes.
```

## 6. Review Self-Check

- Role: plan review worker (AgentDS), not controller. This review does not authorize implementation.
- Source of truth: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, controller judgment, target source and test files were all read.
- Scope boundary: only this review artifact is written. No source/test/runtime/golden/fixture/control/design docs modified.
- Stop conditions: no blocking question remains for this review. Three amendments (A, B, C) require controller adjudication before the plan can route to implementation.
- Evidence and validation: no runtime validation was run. All findings are based on static analysis of plan text against source code and control docs.
- Next action: stop after reporting artifact path and verdict. Controller must adjudicate amendments A-C, then either route amended plan to implementation gate or request plan amendment rework.

Self-check: pass
