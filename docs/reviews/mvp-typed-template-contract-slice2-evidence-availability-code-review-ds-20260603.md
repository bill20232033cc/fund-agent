# MVP typed template contract Slice 2 EvidenceAvailability code review (AgentDS)

## Worker Self-Check

- Role: AgentDS independent code reviewer only. Not controller, not implementation worker.
- Gate: `MVP typed template contract Slice 2 same-source EvidenceAvailability implementation gate`.
- Classification: `heavy`.
- Scope: review only; no implementation, no file edits, no commit, no push, no PR.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-controller-judgment-20260603.md`, `fund_agent/fund/chapter_facts.py`, `fund_agent/fund/template/typed_contracts.py`, `fund_agent/fund/evidence_availability.py`, `fund_agent/fund/__init__.py`, `fund_agent/fund/README.md`, `tests/fund/test_evidence_availability.py`, `tests/README.md`, `docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-implementation-evidence-20260603.md`.
- Controller validation rerun results accepted as evidence: `28 passed`, ruff pass, `git diff --check` pass, secret scan pass.

## Conclusion

**PASS-WITH-RISKS**

No blocking findings. Three non-blocking findings and four minor observations. The implementation correctly derives same-source `EvidenceAvailability` from `ChapterFactProjection`/`ChapterFactInput`, preserves distinct statuses, keeps Ch2 requirements under public chapter 2, represents cross-period absence as `unreviewed`, fails closed on unknown requirement ids, does not mutate or replace `ChapterFactProjection`, and has no forbidden imports or I/O paths.

## Material Findings

### Finding 1 (non-blocking): `derive_chapter_evidence_availability` fact_id parsing is fragile

**File:** `fund_agent/fund/evidence_availability.py:674-714`

`_fund_code_from_chapter()` and `_report_year_from_chapter()` parse `chapter.facts[0].fact_id` with format `chapter-fact:{fund_code}:{report_year}:ch{chapter_id}:{source_field_id}`. The format is an implementation detail of `chapter_facts._fact_id_for()` (`chapter_facts.py:1434-1453`). If the fact_id format changes, fund_code silently becomes `"unknown"` and report_year becomes `0`.

The convenience function is documented as secondary to the primary `derive_evidence_availability(projection)` path (`evidence_availability.py:289-316` docstring and implementation evidence residual risks section). The fail-soft behavior (returning `"unknown"`/`0` rather than crashing) is acceptable for a convenience path but the reconstruction has no validation that the parsed values are correct.

**Severity:** Low. The primary production path (`derive_evidence_availability`) receives explicit fund_code/report_year from the projection root. The convenience function's own docstring positions it as single-chapter convenience only. No test covers the empty-facts or malformed fact_id edge cases for this function.

**Recommendation:** Not blocking for Slice 2. Future gate should either add validation that reconstructed values match expected format or deprecate the convenience function in favor of always requiring a full projection.

### Finding 2 (non-blocking): `ch3.required_output.item_01` absent from `EvidenceRequirementId` closed set

**File:** `fund_agent/fund/evidence_availability.py:37-62`

The `EvidenceRequirementId` Literal covers all Ch2 typed requirement ids and most Ch3 ones, but `ch3.required_output.item_01` (基金经理基本信息) is missing. This item exists in the typed contract mapping (`typed_contracts.py:417`) and corresponds to `ch3.must_answer.item_01` (基金经理的基本信息: 从业年限、管理本基金时间、管理规模).

No `EvidencePredicate` or `ChapterInternalSubcontract` currently references `ch3.required_output.item_01`, so there is no functional impact. However, any future predicate or subcontract that references it would fail at `_validate_typed_requirement_ids()` (`evidence_availability.py:337-359`).

The item could be derived from `structured.basic_identity` (which has chapter 3 facts via the `_CHAPTER_FIELD_SPECS` entry at `chapter_facts.py:332-338`), but no `_CH3_REQUIREMENT_SPECS` entry maps it.

**Severity:** Low. No current functional impact. The Slice 2 plan explicitly scoped Ch3 requirements to "manager strategy text, turnover, holdings snapshot, cross-period style evidence, and manager alignment" — basic info was not in scope.

**Recommendation:** Add `ch3.required_output.item_01` in a future slice with the appropriate source field mapping (`structured.basic_identity`), or explicitly document why it's excluded from evidence availability tracking.

### Finding 3 (non-blocking): static import test is coarse-grained

**File:** `tests/fund/test_evidence_availability.py:149-183`

`test_derivation_does_not_call_document_repository` uses AST-level import name substring matching against a forbidden-fragment list. This approach:

- Only checks direct imports of `evidence_availability.py`, not transitive dependencies (by design — those modules have their own acceptance gates)
- Uses substring matching on module names, which could theoretically miss a forbidden import if aliased or false-positive on innocent names
- Does not verify that forbidden functions are never called at runtime

In practice, the test correctly verifies that `evidence_availability.py` imports only `chapter_facts` and `typed_contracts` — both accepted Fund-layer modules. The module's design (pure functions operating on frozen dataclass inputs, no I/O calls) makes runtime violations structurally impossible.

**Severity:** Low. The test is meaningful for its intended purpose (catching accidental forbidden imports) and the module's architecture provides defense-in-depth. Not blocking.

**Recommendation:** None required for Slice 2. Future hardening could add a runtime monkeypatch test that proves no `open()`, `Path.read_text()`, or `os.environ` calls occur during derivation, but the current static guard plus architectural constraints are sufficient.

## Per-Focus-Area Analysis

### 1. Correctness of additive Fund-layer EvidenceAvailability derivation

**Verdict: PASS**

`derive_evidence_availability()` (`evidence_availability.py:254-286`) consumes only:
- `ChapterFactProjection` (fact ids, source field ids, evidence anchor ids, fact statuses, missing reasons)
- `TypedTemplateContractManifest` (requirement ids from predicates and subcontracts)

The derivation chain is pure:
1. `_derive_from_spec()` reads matching facts by `source_field_id` and `chapter_id`
2. `_status_for_fact()` maps `ChapterFactStatus` → `AvailabilityStatus` with distinct mapping rules
3. `_combine_statuses()` takes the most conservative status across facts
4. `_derive_ch3_actual_behavior_requirements()` aggregates dependencies into derived requirements

No external state, no I/O, no mutation of inputs. The `derive_chapter_evidence_availability()` convenience wrapper reconstructs a synthetic single-chapter projection — see Finding 1.

### 2. Statuses remain distinct and conservatively combined

**Verdict: PASS**

Five statuses are defined in `AvailabilityStatus` (`evidence_availability.py:29-35`):
- `available` — fact is available with evidence anchors and no missing_reason
- `missing` — fact value/anchors missing
- `unavailable` — source unavailable (e.g., NAV data unavailable)
- `not_applicable` — field not applicable to fund type
- `unreviewed` — value exists but evidence not reviewed, or synthetic gap

Combination order (`_STATUS_ORDER`, `evidence_availability.py:67-73`): `unreviewed > unavailable > missing > not_applicable > available`. This is conservative — `unreviewed` is the safest (most restrictive) status, `available` the least restrictive. `_combine_statuses()` (`evidence_availability.py:546-564`) returns the first matching status in priority order.

`_status_for_fact()` (`evidence_availability.py:450-469`) correctly handles:
- `available` + anchors + no missing_reason → `available`
- `available` without anchors or with missing_reason → `unreviewed` (value exists but evidence incomplete)
- `missing`/`unavailable`/`not_applicable` → direct passthrough
- Any other status → `unreviewed` (fail-safe default)

The test `test_distinguishes_missing_unavailable_not_applicable_unreviewed` (`test_evidence_availability.py:57-88`) verifies all five statuses with distinct fixture configurations.

### 3. Ch2 requirements under public chapter_id=2; no public Ch2 split

**Verdict: PASS**

All 13 `_CH2_REQUIREMENT_SPECS` entries (`evidence_availability.py:179-193`) have `chapter_id=2` and `internal_subcontract_id` set to `"performance"`, `"attribution"`, or `"cost"`. No `chapter_id` values outside `{2, 3}` appear in any spec.

The test `test_ch2_subcontract_availability_stays_under_public_chapter_2` (`test_evidence_availability.py:120-146`) verifies:
- All `ch2.*` requirements have `chapter_id == 2`
- Internal subcontract ids are exactly `{"performance", "attribution", "cost"}`

The `ChapterInternalSubcontract.public_chapter_id` field defaults to `None` (`typed_contracts.py:163`) and validation rejects non-None values for Ch2 subcontracts (`typed_contracts.py:1184-1185`).

### 4. Ch3 requirements coverage and cross-period handling

**Verdict: PASS**

Ch3 requirement specs cover:
| Requirement ID | Source Field | Status |
|---|---|---|
| `ch3.requirement.manager_strategy_text_reviewed` | `structured.manager_strategy_text` | fact-derived |
| `ch3.requirement.turnover_rate_reviewed` | `structured.turnover_rate` | fact-derived |
| `ch3.requirement.holdings_snapshot_reviewed` | `structured.holdings_snapshot` | fact-derived |
| `ch3.requirement.cross_period_style_evidence_reviewed` | `synthetic.cross_period_comparison` | hardcoded `unreviewed` |
| `ch3.requirement.manager_alignment_reviewed` | `structured.manager_alignment` | fact-derived |
| `ch3.required_output.item_02` | `structured.manager_strategy_text` | fact-derived |
| `ch3.required_output.item_06` | `structured.manager_alignment` | fact-derived |
| `ch3.requirement.actual_behavior_reviewed` | derived from turnover+holdings+cross_period | derived aggregate |
| `ch3.required_output.item_03`/`04`/`05` | derived from actual_behavior | derived aggregate |

Cross-period style evidence (`ch3.requirement.cross_period_style_evidence_reviewed`) is hardcoded to `unreviewed` at `evidence_availability.py:442-443` with `source_kind="synthetic_gap"` and detail text explaining the single-year limitation. No document loading occurs.

`actual_behavior_reviewed` derives from three dependencies (`evidence_availability.py:247-251`), and the aggregate status propagates correctly to items 03/04/05. The test `test_ch3_actual_behavior_requirement_is_unreviewed_when_turnover_or_style_evidence_absent` (`test_evidence_availability.py:91-117`) confirms unreviewed propagation with source field coverage.

### 5. Unknown/malformed typed contract requirement ids fail closed

**Verdict: PASS**

The closed set is enforced at two levels:

1. **Type level:** `EvidenceRequirementId` is a `Literal` type alias (`evidence_availability.py:37-62`) enumerating all 24 valid requirement ids. `_KNOWN_REQUIREMENT_IDS` is derived from `get_args(EvidenceRequirementId)` (`evidence_availability.py:65`).

2. **Runtime validation:** `_validate_typed_requirement_ids()` (`evidence_availability.py:337-359`) checks that all `requirement_ids` referenced in:
   - `MustNotCoverClause.applies_when.requirement_ids` (from typed contract predicates)
   - `ChapterInternalSubcontract.requirement_ids` (from Ch2 subcontracts)
   
   are members of `_KNOWN_REQUIREMENT_IDS`. Unknown ids raise `ValueError`.

The test `test_unknown_requirement_id_fails_closed` (`test_evidence_availability.py:186-222`) constructs a manifest with `ch3.requirement.unknown_reviewed` and verifies `ValueError` with message `"未知 EvidenceRequirementId"`.

**Coverage completeness note:** The validation covers the two sources of requirement id references in the typed contract (predicates and subcontracts). No other typed contract fields reference `EvidenceRequirementId` values. The cross-module dependency (typed_contracts defines predicates with requirement_id strings that must match the EvidenceRequirementId Literal) is correct but fragile — see Observation 2 below.

### 6. EvidenceAvailability does not replace or mutate ChapterFactProjection

**Verdict: PASS**

All dataclasses are `frozen=True, slots=True`. `derive_evidence_availability()` takes `ChapterFactProjection` as input and returns a new `EvidenceAvailability` instance. The input projection is never modified.

The module docstring (`evidence_availability.py:1-8`) explicitly states "该视图也不替代 `ChapterFactProjection`". The README (`fund_agent/fund/README.md:125-131`) describes `EvidenceAvailability` as additive and same-source, not a replacement.

### 7. No forbidden imports or I/O reads

**Verdict: PASS**

Direct imports of `evidence_availability.py`:
- `fund_agent.fund.chapter_facts` — accepted Fund-layer module
- `fund_agent.fund.template.typed_contracts` — accepted Fund-layer module
- `hashlib` — standard library (for gap id digest)
- `dataclasses` — standard library
- `typing` — standard library

No `documents`, `repository`, `cache`, `pdf`, `source` (module), `downloader`, `parser`, `service`, `host`, `provider`, `retained`, `filesystem`, `pathlib`, `os`, `dayu`, `openai`, or `llm` imports.

The static import test (`test_evidence_availability.py:149-183`) verifies this with AST-level substring matching. See Finding 3 for limitations.

Runtime behavior: all functions are pure transformations of frozen dataclass inputs. No `open()`, `Path.read_text()`, `os.environ`, network calls, or file system access.

### 8. No provider/runtime/default/budget/endpoint or other prohibited concepts

**Verdict: PASS**

The module contains zero references to: provider, runtime, default, budget, endpoint, PASS-only, live probe, score, golden, readiness, quality gate, deterministic fallback, stdout partial report, or `extra_payload`. All parameters are explicitly typed dataclass fields.

### 9. derive_chapter_evidence_availability convenience path safety

**Verdict: PASS-WITH-RISKS (see Finding 1)**

`derive_chapter_evidence_availability()` (`evidence_availability.py:289-316`) is a legitimate convenience for callers that have a single `ChapterFactInput` rather than a full projection. The reconstruction of fund_code/year from fact_ids is documented, fails softly to `"unknown"`/`0`, and the function's docstring positions it as secondary to `derive_evidence_availability(projection)`.

The function does not introduce any new I/O, does not bypass validation, and delegates entirely to `derive_evidence_availability()`. Acceptable as convenience-only. Should not be promoted to the primary production path without hardening (see Finding 1).

### 10. Tests/README/evidence sufficiency

**Verdict: PASS**

Test coverage (7 tests):
- `test_derives_available_requirements_from_fact_ids_and_anchor_ids` — happy path for Ch2 and Ch3
- `test_distinguishes_missing_unavailable_not_applicable_unreviewed` — all 5 statuses
- `test_ch3_actual_behavior_requirement_is_unreviewed_when_turnover_or_style_evidence_absent` — aggregate derivation
- `test_ch2_subcontract_availability_stays_under_public_chapter_2` — no public Ch2 split
- `test_derivation_does_not_call_document_repository` — static import guard
- `test_unknown_requirement_id_fails_closed` — fail-closed validation
- `test_available_status_type_closed` — type-level smoke test

Gaps (non-blocking):
- `derive_chapter_evidence_availability()` has no dedicated test
- `EvidenceAvailability.require()` ValueError path untested
- `_validate_projection_chapters()` duplicate-chapter path untested
- `_combine_statuses()` empty-input ValueError untested
- `_fund_code_from_chapter()` / `_report_year_from_chapter()` edge cases (empty facts, malformed fact_id) untested

README (`fund_agent/fund/README.md:125-131`) accurately describes the module's capability, constraints, and non-goals. Tests README (`tests/README.md:21`) has a one-line entry accurately scoping the test file. The implementation evidence artifact is detailed and honest about residual risks.

## Observations

### Observation 1: `_validate_typed_requirement_ids` does not check `EvidencePredicate` defined at module level

`typed_contracts.py:571-579` defines `_CH3_STYLE_EVIDENCE_UNREVIEWED` as a module-level `EvidencePredicate`. Its `requirement_ids` (`ch3.requirement.turnover_rate_reviewed`, `ch3.requirement.cross_period_style_evidence_reviewed`) are validated only when the predicate is wired into a `MustNotCoverClause` (which happens for `ch3.must_not_cover.item_04`). The module-level predicate itself is not independently validated against `_KNOWN_REQUIREMENT_IDS`. If a future developer adds a new module-level predicate with unknown requirement ids but forgets to wire it into a clause, the invalid ids would not be caught at load time. Not blocking — currently all module-level predicates are wired into clauses.

### Observation 2: Cross-module requirement id contract is implicit

`EvidenceRequirementId` is defined in `evidence_availability.py` as a `Literal` type alias. `typed_contracts.py` defines `EvidencePredicate.requirement_ids` as `tuple[str, ...]` — plain strings, not `tuple[EvidenceRequirementId, ...]`. This means the type checker cannot catch mismatches between predicate requirement_ids and the closed set. The runtime check (`_validate_typed_requirement_ids`) catches mismatches, but only at derivation time, not at typed contract construction time. Not blocking — the fail-closed runtime behavior is correct.

### Observation 3: Ch3 required_output items 03/04/05 share identical availability

`_derive_ch3_actual_behavior_requirements()` (`evidence_availability.py:472-520`) gives `ch3.required_output.item_03` (实际投资行为), `item_04` (言行一致性判断), and `item_05` (风格稳定性判断) the same `RequirementAvailability` as `actual_behavior_reviewed`. This is semantically correct for the current gate — all three depend on the same evidence base — but means a consumer cannot distinguish "we have turnover data but not cross-period data" at the individual required-output level. Future slices may want finer granularity.

### Observation 4: `fund_agent/fund/__init__.py` re-exports omit `AvailabilityStatus` and `EvidenceRequirementId`

`fund_agent/fund/__init__.py:7-23` re-exports `EVIDENCE_AVAILABILITY_SCHEMA_VERSION`, `EvidenceAvailability`, `EvidenceGapReference`, `RequirementAvailability`, and both derive functions. `AvailabilityStatus` and `EvidenceRequirementId` (type aliases) are not re-exported. Callers must import them from `fund_agent.fund.evidence_availability` directly. Inconsistency with how other type aliases are handled elsewhere; not blocking.

## Validation

Controller validation (independently rerun, accepted as evidence):
- `uv run pytest tests/fund/test_evidence_availability.py tests/fund/test_chapter_facts.py tests/fund/template/test_typed_contracts.py` → 28 passed
- `uv run ruff check fund_agent/fund tests/fund` → All checks passed
- `git diff --check` over touched files → exit 0
- Secret scan → only existing README safety text, no secrets

Reviewer did not independently rerun validation; controller results are accepted.

## Non-Goals Verified

The implementation does not:
- Replace `ChapterFactProjection`
- Change `contracts.py`, renderer, auditor, deterministic `analyze/checklist`, or `--use-llm` behavior
- Edit `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, or `docs/fund-analysis-template-draft.md`
- Add repository/PDF/cache/source-helper/Service/Host/provider/retained-report/filesystem/env/dayu/Agent runtime/tool-loop access
- Pass business parameters through `extra_payload`, `**kwargs`, or untyped payload bags
- Implement multi-year annual evidence runtime loading
- Change score-loop, golden/readiness/promotion, quality gate, final judgment, or provider endpoint/default/budget

## Reviewer Checklist

- [x] Does derivation consume only `ChapterFactProjection`/`ChapterFactInput` and typed contract requirement ids? Yes.
- [x] Are all 5 statuses distinct and conservatively combined? Yes (`unreviewed > unavailable > missing > not_applicable > available`).
- [x] Do Ch2 requirements stay under public chapter_id=2? Yes; all have `chapter_id=2` and `internal_subcontract_id` set.
- [x] Do Ch3 requirements cover strategy, turnover, holdings, cross-period, alignment, actual behavior? Yes, plus required_output items.
- [x] Is cross-period absence unreviewed without loading documents? Yes; hardcoded `unreviewed` with `synthetic_gap` source_kind.
- [x] Do unknown requirement ids fail closed? Yes; `_validate_typed_requirement_ids` checks against `_KNOWN_REQUIREMENT_IDS`.
- [x] Does `EvidenceAvailability` avoid replacing or mutating `ChapterFactProjection`? Yes; frozen dataclasses, pure functions.
- [x] Are forbidden imports absent? Yes; only `chapter_facts` and `typed_contracts` imported.
- [x] Are provider/runtime/default/budget/endpoint/score/golden/readiness/quality-gate/fallback/stdout/extra_payload absent? Yes.
- [x] Is `derive_chapter_evidence_availability` safe enough as convenience? Yes, with residual risk noted (Finding 1).
- [x] Are tests/README/evidence sufficient and not overclaiming? Yes, with minor gaps noted.

## Secret Safety

This review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
