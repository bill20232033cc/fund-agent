# P16-S2 Plan Review — AgentGLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Plan `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` is accepted with findings described below. No findings require plan revision before controller judgment.

## Review Scope

| Item | Source |
|---|---|
| Plan under review | `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` |
| Agent execution rules | `AGENTS.md` |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| P16-S1 evidence artifact | `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` |
| P16-S1 controller judgment | `docs/reviews/p16-s1-code-review-controller-judgment-20260522.md` |
| Excluded inputs | `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md` — neither read nor cited |

## Findings

### F1 — INFO: proposed rows exactly match P16-S1 accepted evidence

**Severity**: info
**Evidence**: Cross-checked all 25 proposed rows (5 funds × 5 subfields) against P16-S1 candidate records.

| Fund | `benchmark_text` | `benchmark_identity_status` | `methodology_availability` | `constituents_availability` | `source_tier` | Anchor |
|---|---|---|---|---|---|---|
| `004194` | `中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%` | `composite` | `benchmark_only` | `benchmark_only` | `benchmark_context` | §2 page-5 page-5-table-1 ✅ |
| `005313` | `中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%` | `composite` | `benchmark_only` | `benchmark_only` | `benchmark_context` | §2 page-5 page-5-table-1 ✅ |
| `017644` | `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` | `composite` | `benchmark_only` | `benchmark_only` | `benchmark_context` | §2 page-6 page-6-table-0 ✅ |
| `019918` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%` | `composite` | `benchmark_only` | `benchmark_only` | `benchmark_context` | §2 page-5 page-5-table-1 ✅ |
| `019923` | `中证2000指数收益率×95%＋人民币活期存款税后利率×5%` | `composite` | `benchmark_only` | `benchmark_only` | `benchmark_context` | §2 page-6 page-6-table-0 ✅ |

All values match the P16-S1 evidence artifact exactly, including the distinct bracket styles `（税后）`, `(税后)`, `×`, `*`, `＋` that reflect actual extractor output from different fund annual reports. Source anchors in the plan use the golden-answer Markdown convention (`年报2024 §2 page-5 page-5-table-1 benchmark`) which aligns with existing entries in `reports/golden-answers/golden-answer-prefill-reviewed.md`.

**Impact**: Confirms plan's proposed rows are evidence-grounded and correctly preserve extractor-output fidelity.
**Disposition**: No action required.

### F2 — INFO: `benchmark_index_name` exclusion is consistent with golden-path constraints

**Severity**: info
**Evidence**: Verified from code:

- `IndexProfileValue.benchmark_index_name` is `str | None` (`fund_agent/fund/extractors/models.py:91`).
- All five candidates have `benchmark_index_name=None` per P16-S1 evidence.
- `_comparable_scalar()` returns `None` for `None` values (`fund_agent/fund/extraction_snapshot.py:1067`), so null values do not enter the comparable extraction.
- Strict golden Markdown validation requires non-empty `expected_value` (`fund_agent/fund/golden_answer.py:608-609`: `if not expected_value: errors.append(...)`).
- Therefore `benchmark_index_name=null` cannot be represented as an active strict golden row through current code.

The plan's decision not to add `benchmark_index_name` rows is the only path that does not require either:
(a) changing strict golden validation to accept null expected values, or
(b) inferring a single index name from product name or benchmark text — which would violate the AGENTS.md rule "禁止使用间接证据" and the plan's own fail-closed composite benchmark semantics.

**Impact**: Confirms the exclusion is safe and code-consistent.
**Disposition**: No action required.

### F3 — LOW: future implementation should add explicit existing-row regression check to success signals

**Severity**: low
**Evidence**: The plan's "Expected future success signals" list (plan lines 296-303) focuses on verifying new rows and absence of prohibited rows. It does not include an explicit check that `golden-build` preserves all pre-existing golden records unchanged.

The stop conditions (plan lines 307-316) include: "`golden-build` rejects planned rows or changes unrelated existing records unexpectedly." This provides stop protection, but the success-signal section should symmetrically verify existing records are intact after the rebuild.

Current comparable sub-fields for `index_profile` include `benchmark_index_name` and `benchmark_index_code` (verified: `fund_agent/fund/extraction_snapshot.py:59-67`). For `001548` (existing index-fund golden entry added in P14-S1), `benchmark_index_name` has a non-null value and is already in the golden set. Future implementation must confirm this existing row is not altered when five new fund sections are appended.

**Impact**: Low. Stop conditions already cover unexpected changes. Adding a positive success signal for existing-row stability would make the validation more complete.
**Required disposition**: Future implementation should add a success signal: "pre-existing golden records (including `001548 index_profile` rows) are unchanged in rebuilt JSON." Controller may accept the plan as-is and fold this into implementation constraints.

### F4 — INFO: `benchmark_component_text` exclusion is correct and tuple representation is properly deferred

**Severity**: info
**Evidence**: `IndexProfileValue.benchmark_component_text` is `tuple[str, ...]` (`fund_agent/fund/extractors/models.py:93`). `_comparable_scalar()` returns `None` for `tuple` values (`fund_agent/fund/extraction_snapshot.py:1068`). `benchmark_component_text` is not in `COMPARABLE_SUB_FIELDS_BY_FIELD["index_profile"]` (verified: `extraction_snapshot.py:59-67` lists only 7 scalar subfields). Therefore `benchmark_component_text` cannot enter the comparable extraction or correctness comparison through current code.

The plan correctly defers full tuple/null golden semantics to a "future golden/comparable schema phase" (Residuals table). The plan does not force `benchmark_component_text` into the golden path, which would require changing the comparable extraction to support nested values — a scope change that should be a separate reviewed gate.

**Impact**: Confirms plan stays within current golden/comparable semantics.
**Disposition**: No action required.

### F5 — INFO: `tracking_error` prohibition is aligned with all truth sources

**Severity**: info
**Evidence**: Cross-checked against:

- P16-S1 controller judgment: "No `tracking_error` golden gate may open from P16-S1 results."
- P16-S1 evidence: all five candidates are `blocked_no_direct_tracking_error`.
- `docs/design.md` §7.4: "`tracking_error` 生产 golden rows 只有在 reviewed direct observed disclosure evidence 被接受后才能添加."
- `docs/implementation-control.md` Active Residuals: "P16-S1 blocked all five enhanced-index candidates for `tracking_error`; do not add `tracking_error` golden rows from target/limit text, manager narrative, benchmark-only text, or incomplete anchors."
- P15-S1A: `001548` also blocked as `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`.

The plan's tracking_error prohibition (plan lines 17-21, 132-133, 207, 274, 326-327) is consistent with all truth sources. The Review Rejection Criteria (plan lines 322-333) correctly include "adds `tracking_error` rows for any P16-S1 candidate" as a rejection trigger.

**Impact**: Confirms tracking_error prohibition is watertight.
**Disposition**: No action required.

## First-principles Decision Assessment

### Why golden these rows is correct

1. **P14 quality denominator**: P14 made `index_profile` a conditional P1 quality field for `enhanced_index` funds. Without production golden rows for these five funds, the correctness denominator for enhanced-index `index_profile` relies solely on `001548` (index fund) and fixtures. The plan correctly identifies this gap and fills it with evidence-backed production rows.

2. **Evidence chain**: P16-S1 → evidence acquisition → controller judgment → this plan. Each step preserved `FundDocumentRepository` / `FundDataExtractor` boundaries, verified `fallback_used=False`, confirmed `enhanced_index` classification, and recorded EID source metadata. The chain is intact.

3. **Composite semantics preserved**: The plan does not flatten composite benchmarks into a single index name. `benchmark_identity_status=composite` is the golden target, not `identified` with an inferred name. This is the fail-closed position: the extractor currently cannot resolve a composite benchmark to a single canonical index, and the golden rows reflect that reality.

### Why the scalar-only approach is the safe path

Current golden/comparable code has explicit constraints:

- `_comparable_scalar()`: rejects `None`, `tuple`, `list`, `dict`, `set` (`extraction_snapshot.py:1067-1068`).
- Strict golden validation: rejects empty `expected_value` (`golden_answer.py:608`).
- `COMPARABLE_SUB_FIELDS_BY_FIELD["index_profile"]`: only 7 scalar subfields (`extraction_snapshot.py:59-67`).

The plan's proposed 5 subfields per fund are a strict subset of the 7 comparable subfields, excluding only the two that are `null` for all five candidates. This is the maximum coverage achievable without changing golden/comparable semantics.

If a reviewer or controller requires golden coverage for `benchmark_component_text` or `benchmark_index_name=null`, the plan's stop condition (line 311) correctly triggers: "reviewer/controller requires active golden assertions for `benchmark_component_text` tuple or `benchmark_index_name=null`." At that point, a new gate must design null/tuple golden semantics before any rows are added. This is the correct architectural boundary.

### Stop conditions are sufficient

The plan's 8 stop conditions (lines 307-316) cover:
- Extractor output divergence from P16-S1 values
- Anchor provenance reconciliation failure
- Golden/comparable path incompatibility
- Null/tuple golden requirement
- golden-build rejection or unexpected mutation
- No comparable fields
- Out-of-boundary source access
- Scope pressure (tracking_error, methodology, constituents, inferred identity)

These are comprehensive and conservative. The "stop without golden edits" requirement (line 317) prevents partial updates.

### Review rejection criteria are appropriate

The 10 rejection criteria (lines 322-333) are all grounded in truth-source constraints. No criterion is over-restrictive or under-restrictive. The "fails `git diff --check HEAD`" criterion ensures no trailing whitespace or conflict markers, consistent with prior gate validation standards.

## Scope Boundary Check

| Boundary | Plan compliance |
|---|---|
| This gate creates only the plan artifact | ✅ Plan gate validation section confirms single file output |
| No source/test/golden edits in this gate | ✅ Explicitly stated in Scope section |
| No design.md or implementation-control.md edits | ✅ Explicitly excluded |
| No CSV/RR-13 edits | ✅ Explicitly excluded |
| No commits, branches, PRs | ✅ Explicitly excluded |
| No Dayu runtime, LLM, external adapters | ✅ Out of scope for future implementation |
| No tracking_error golden rows | ✅ Prohibited with multiple safeguards |
| Excluded inputs not read or cited | ✅ Explicitly excluded in Current Truth Inputs section |
| `FundDocumentRepository` / `FundDataExtractor` boundaries preserved | ✅ Future implementation preserves these boundaries |
| AGENTS.md module boundaries respected | ✅ Plan stays within Fund Capability golden/correctness scope |

## Over-scope Assessment

No over-scope detected. The plan:
- Does not propose extractor changes (only allows conditional source changes if current path is blocked).
- Does not propose quality gate rule changes.
- Does not propose comparable whitelist changes.
- Does not propose design truth changes.
- Does not propose Dayu/LLM/external-adapter integration.
- Correctly defers tuple/null golden semantics, tracking_error evidence, methodology/constituents extraction, and E1-E3 to future phases with explicit residual owners.

## Test Coverage Assessment

The plan specifies 5 test files with targeted coverage:

| Test file | Required coverage | Assessment |
|---|---|---|
| `test_golden_answer.py` | Strict Markdown/JSON accepts new rows | ✅ Directly validates golden-build output |
| `test_golden_prefill.py` | Dataclass prefill resolves scalar fields; composite fixture does not synthesize `benchmark_index_name` | ✅ Tests the critical "no synthesis" invariant |
| `test_extraction_snapshot.py` | Composite `IndexProfileValue` serializes comparable scalar fields and omits null/tuple fields | ✅ Validates comparable extraction path |
| `test_extraction_score.py` | Correctness for new rows is comparable and matched; `benchmark_index_name` absent for composite rows is not treated as matchable expected data | ✅ Validates correctness comparison semantics |
| `test_quality_gate.py` or `test_quality_gate_integration.py` | Coverage stays non-blocking for absent non-comparable null/tuple rows; catches mismatches on scalar rows | ✅ Validates quality gate behavior |

Coverage is sufficient for the planned scope. The "no synthesis" and "no matchable null" invariants are the most important tests, and the plan correctly identifies them.

## Handoff Prompt Assessment

The handoff prompt (plan lines 349-360) is well-structured and self-contained. It:
- Preserves all constraints from the plan.
- References the correct truth inputs.
- Excludes the correct excluded inputs.
- Specifies the exact scope (5 funds, scalar index_profile only).
- Includes stop conditions inline.
- Specifies validation requirements.

A future implementation agent could execute from this prompt alone, which is the correct handoff quality standard.

## Summary

The plan is a thorough, evidence-grounded implementation plan that correctly:

1. Identifies the quality-denominator gap for enhanced-index `index_profile` golden coverage.
2. Proposes exactly the rows that current comparable/golden semantics can safely represent.
3. Preserves composite benchmark semantics without inferring single index names.
4. Prohibits tracking_error golden rows in alignment with all truth sources.
5. Defines comprehensive stop conditions and rejection criteria.
6. Stays within scope and does not touch design truth, control truth, source code, tests, or golden files in this gate.

Four findings: F1 and F2 confirm evidence accuracy, F3 suggests a minor success-signal addition for existing-row stability, F4 confirms tuple/null deferral. None require plan revision.

**Verdict: PASS_WITH_FINDINGS**
