# MVP typed template contract Slice 2 EvidenceAvailability code review — MiMo

## Reviewer Self-Check

- Role: AgentMiMo independent code reviewer only; not controller and not implementation worker.
- Gate: `MVP typed template contract Slice 2 same-source EvidenceAvailability implementation gate`.
- Classification: `heavy`.
- Scope: uncommitted diff only for Slice 2 implementation.
- Files reviewed: `fund_agent/fund/evidence_availability.py`, `fund_agent/fund/__init__.py`, `fund_agent/fund/README.md`, `tests/fund/test_evidence_availability.py`, `tests/README.md`, `docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-implementation-evidence-20260603.md`.
- Source of truth read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`, `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-controller-judgment-20260603.md`, `fund_agent/fund/chapter_facts.py`, `fund_agent/fund/template/typed_contracts.py`.
- Actions intentionally not taken: no source code edit, no commit, no push, no PR.

## Conclusion

**PASS WITH RISKS.**

No blocking findings. Two non-blocking residual findings that should be tracked for controller judgment.

## Material Findings

### Finding 1 (Non-Blocking): `ch3.required_output.item_01` and `ch3.required_output.item_04` have no explicit `_RequirementSpec` or `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` coverage

**Location**: `fund_agent/fund/evidence_availability.py` — `_CH3_REQUIREMENT_SPECS` and `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`

**Evidence**: The `EvidenceRequirementId` Literal type includes `ch3.required_output.item_02` through `ch3.required_output.item_06`, but not `ch3.required_output.item_01` ("基金经理基本信息") or `ch3.required_output.item_04` ("言行一致性判断"). The typed contract `typed_contracts.py:417-422` defines all six Ch3 required outputs.

**Impact**: For `item_01`, `_facts_for_spec` will raise a `KeyError` when checking `fact.source_field_id in spec.source_field_ids` because no spec exists. Actually — on closer inspection, `_derive_from_spec` is only called for specs in `_CH2_REQUIREMENT_SPECS + _CH3_REQUIREMENT_SPECS`, so `item_01` and `item_04` are simply never derived. They will not appear in `EvidenceAvailability.requirements`. Calling `availability.require("ch3.required_output.item_01")` will raise `ValueError("未知 EvidenceAvailability requirement_id")`.

For `item_04`, the semantic gap is mitigated: the aggregate `ch3.requirement.actual_behavior_reviewed` and `ch3.required_output.item_03` / `item_05` all derive from the same turnover/holdings/cross-period dependencies, so the behavioral evidence gate for consistency judgment is effectively covered through the actual-behavior aggregate path. But the specific output id `item_04` is not in the availability view.

**Assessment**: This is a conservative omission that fails safe — downstream code querying `item_04` availability will get a ValueError, not a false "available". The semantic intent (言行一致性判断 blocked when actual behavior is unreviewed) is preserved through `actual_behavior_reviewed`. However, the missing output ids mean that future Slice 3/4 wiring for required output degrade behavior (`when_evidence_missing`) will need to either add explicit specs for `item_01` / `item_04` or document that these are intentionally out of the availability view.

**Recommendation**: Non-blocking for Slice 2 acceptance. Track as residual: Slice 3/4 should decide whether `item_01` / `item_04` need explicit `_RequirementSpec` entries or should be documented as intentionally derived-only-through-aggregate.

### Finding 2 (Non-Blocking): `derive_chapter_evidence_availability()` reconstructs fund_code/year from fact ids

**Location**: `fund_agent/fund/evidence_availability.py:674-714` — `_fund_code_from_chapter()` and `_report_year_from_chapter()`

**Evidence**: The convenience function splits `chapter.facts[0].fact_id` by `:` to extract fund code (index 1) and report year (index 2). When `chapter.facts` is empty, it returns `"unknown"` / `0`.

**Assessment**: The fact id format is `chapter-fact:{fund_code}:{report_year}:ch{chapter_id}:{source_field_id}` (established in `chapter_facts.py:1453`). The reconstruction is format-coupled but stable since the format is controlled by the same codebase. The evidence artifact (`docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-implementation-evidence-20260603.md:114`) explicitly documents this as a convenience path and recommends preferring `derive_evidence_availability(projection)` for production-grade use.

**Recommendation**: Non-blocking. Acceptable as convenience-only given the explicit documentation and the fact that the format is internally controlled.

## Review Checklist

### 1. Correctness of additive Fund-layer EvidenceAvailability derivation from ChapterFactProjection/ChapterFactInput only

PASS. `derive_evidence_availability()` consumes only `ChapterFactProjection` and `TypedTemplateContractManifest`. No repository/PDF/cache/source helper/Service/Host/provider/retained report/filesystem/env/dayu reads. `ChapterFactProjection` is not mutated (frozen dataclass, read-only iteration). The output `EvidenceAvailability` is a new additive view with its own schema version.

### 2. Statuses available/missing/unavailable/not_applicable/unreviewed remain distinct and conservatively combined

PASS. Five statuses are defined as `AvailabilityStatus` Literal (`evidence_availability.py:29-35`). `_status_for_fact()` maps each `ChapterFactStatus` to a distinct `AvailabilityStatus` without collapsing. `_combine_statuses()` uses strict priority order `unreviewed > unavailable > missing > not_applicable > available` (`evidence_availability.py:67-73`). Test `test_distinguishes_missing_unavailable_not_applicable_unreviewed` proves all four non-available states are independently observable.

### 3. Ch2 requirements stay under public chapter_id=2/internal subcontracts; no public Ch2 split

PASS. All `_CH2_REQUIREMENT_SPECS` have `chapter_id=2` and `internal_subcontract_id` set to `performance` / `attribution` / `cost`. No requirement creates a chapter_id outside 0-7. Test `test_ch2_subcontract_availability_stays_under_public_chapter_2` asserts `{2}` as the only chapter_id set and all three subcontract ids present.

### 4. Ch3 requirements cover manager strategy, turnover, holdings snapshot, cross-period style evidence, manager alignment, actual behavior

PASS. `_CH3_REQUIREMENT_SPECS` covers: `manager_strategy_text_reviewed`, `turnover_rate_reviewed`, `holdings_snapshot_reviewed`, `cross_period_style_evidence_reviewed`, `manager_alignment_reviewed`, `required_output.item_02`, `required_output.item_06`. `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID` and `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` cover `actual_behavior_reviewed`, `required_output.item_03`, `item_04` (言行一致性), `item_05` (风格稳定性). Cross-period absence in single-year projection is explicitly `"unreviewed"` without loading documents (`evidence_availability.py:442-443`). Test `test_ch3_actual_behavior_requirement_is_unreviewed_when_turnover_or_style_evidence_absent` validates this.

### 5. Unknown/malformed typed contract requirement ids fail closed

PASS. `_validate_typed_requirement_ids()` collects all requirement ids from `must_not_cover.applies_when.requirement_ids` and `internal_subcontracts.requirement_ids` across the manifest, then checks each against `_KNOWN_REQUIREMENT_IDS` (frozenset from `EvidenceRequirementId` Literal args). Unknown ids raise `ValueError`. Test `test_unknown_requirement_id_fails_closed` constructs a manifest with `ch3.requirement.unknown_reviewed` and asserts the ValueError. Validation covers all typed contract requirement id sources required by Slice 2: Ch2 subcontract requirement ids and Ch3 must_not_cover predicate requirement ids.

### 6. EvidenceAvailability does not replace ChapterFactProjection and does not mutate it

PASS. `ChapterFactProjection` is a frozen dataclass. `derive_evidence_availability()` iterates over projection chapters/facts read-only. The output is a separate `EvidenceAvailability` with its own schema version. The module docstring and evidence artifact explicitly state non-replacement.

### 7. No repository/PDF/cache/source-helper/Service/Host/provider/retained-report/filesystem/env/dayu/Agent runtime/tool-loop imports or reads; static import test meaningful

PASS. Module imports are: `hashlib`, `dataclasses`, `typing`, `fund_agent.fund.chapter_facts`, `fund_agent.fund.template.typed_contracts` — all within Slice 2 scope. Test `test_derivation_does_not_call_document_repository` uses AST parsing to verify no forbidden module fragments appear in the import set. The test is meaningful: it catches regressions if a forbidden import is added. Forbidden fragments cover `documents`, `repository`, `cache`, `pdf`, `source`, `downloader`, `parser`, `service`, `host`, `provider`, `retained`, `filesystem`, `pathlib`, `os`, `dayu`, `openai`, `llm`.

### 8. No provider/runtime/default/budget/endpoint, PASS-only live probe, score/golden/readiness, quality gate, deterministic fallback, stdout partial report, or extra_payload business params

PASS. The diff contains no provider config, runtime defaults, budget, endpoint, score-loop, golden, readiness, quality gate, deterministic fallback, stdout partial report, or `extra_payload` code. All new dataclasses are frozen with explicit typed fields.

### 9. `derive_chapter_evidence_availability()` convenience — safe enough or should be blocked

NON-BLOCKING RISK. The convenience function reconstructs fund_code/year from fact id format `chapter-fact:{fund_code}:{report_year}:...`. This is format-coupled but the format is internally controlled (`chapter_facts.py:1453`). When facts are empty, returns `"unknown"`/`0`. The evidence artifact explicitly documents this as convenience-only and recommends the projection-based path for production. Acceptable for Slice 2; the recommendation to prefer `derive_evidence_availability(projection)` is documented.

### 10. Tests/README/evidence sufficient and not overclaiming

PASS. Tests cover all six planned test cases plus a closed-set smoke. README accurately describes the new capability without overclaiming. The evidence artifact is honest about residual risks (Ch2 horizon completeness, cross-period unreviewed, convenience function format coupling).

## Validation

Controller independently reran:

```bash
uv run pytest tests/fund/test_evidence_availability.py tests/fund/test_chapter_facts.py tests/fund/template/test_typed_contracts.py
uv run ruff check fund_agent/fund tests/fund
```

Results:

- `28 passed in 0.67s`
- `All checks passed!`

## Residual Risks For Controller

| Finding | Severity | Disposition |
|---|---|---|
| `ch3.required_output.item_01` / `item_04` not in `_RequirementSpec` or `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` | Non-blocking | Track for Slice 3/4: decide whether to add explicit specs or document intentional omission |
| `derive_chapter_evidence_availability()` format-coupled fund_code/year reconstruction | Non-blocking | Acceptable as convenience-only; documented |

## Secret Safety

This review artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text or raw parsed annual-report text.
