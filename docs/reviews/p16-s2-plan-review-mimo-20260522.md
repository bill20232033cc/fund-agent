# P16-S2 Index Profile Benchmark-context Golden Implementation Plan Review（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

## Review Scope

Review target: `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md`

Review inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md`
- `docs/reviews/p16-s1-code-review-controller-judgment-20260522.md`
- current code facts under `fund_agent/fund/`, `docs/golden-answer-template.md`, `reports/golden-answers/`, and `tests/`

Excluded inputs: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`, excluded audit inputs.

## First-principles Decision Review

Plan correctly concludes that golden rows are useful for enhanced-index `index_profile` benchmark-context coverage. The reasoning is sound:

- P14 made `index_profile` a conditional P1 quality field for `index_fund` / `enhanced_index`.
- Without selected-fund enhanced-index production golden rows, correctness coverage relies on `001548` index-fund rows and deterministic fixtures.
- P16-S1 already proved five selected-fund annual reports expose accepted benchmark-context evidence through the production repository/extractor path.
- Adding production rows improves the quality denominator direction.

**Verified**: Current `COMPARABLE_SUB_FIELDS_BY_FIELD["index_profile"]` in `fund_agent/fund/extraction_snapshot.py:59-67` exactly matches the plan's listed 7 subfields: `benchmark_text`, `benchmark_identity_status`, `benchmark_index_name`, `benchmark_index_code`, `methodology_availability`, `constituents_availability`, `source_tier`.

## Composite Benchmark Handling Review

Plan correctly identifies that composite benchmarks with `benchmark_index_name=null` require explicit handling. The first-principles reasoning is sound:

- `benchmark_index_name=null` for these five funds is the extractor's fail-closed representation for composite benchmarks such as `指数收益率 * 95% + 存款利率 * 5%`.
- The annual report directly supports the full benchmark text and composite identity, but does not directly support a single canonical `benchmark_index_name`.
- Deferring solely because `benchmark_index_name` is null would weaken the quality denominator and incentivize worse implementations.

**Verified**: `fund_agent/fund/golden_answer.py:_validate_active_row` (line 608-609) explicitly rejects empty `expected_value`. Null cannot be represented as an active strict golden row. Plan's decision to not add `benchmark_index_name` rows is correct.

## Current Comparable / Golden Path Constraint Review

Plan correctly identifies the constraint that current comparable extraction deliberately drops `None`, tuple/list, dict and set values. Therefore:

- `benchmark_component_text` cannot be production-goldened through current correctness.
- `benchmark_index_name=null` cannot be represented as an active strict golden row.
- A future implementation preserves null semantics by not adding `benchmark_index_name` rows and adding regression tests.

**Verified**: `fund_agent/fund/extraction_score.py:_compare_golden_record` (line 1885-1898) treats `None` actual values as `CORRECTNESS_MISMATCH` if golden expects the field. If a key is absent entirely from `actual_index`, it is `CORRECTNESS_UNAVAILABLE` (line 1870-1883) and excluded from the denominator. Since no `benchmark_index_name` golden row is proposed, the composite benchmark null actual value will be `CORRECTNESS_UNAVAILABLE` — excluded from denominator, not treated as mismatch. This is safe behavior.

## Proposed Production Rows Review

### Row Correctness

All 25 proposed rows (5 funds × 5 subfields) verified against P16-S1 evidence artifact:

| Fund | benchmark_text | benchmark_identity_status | methodology_availability | constituents_availability | source_tier | Anchor |
|---|---|---|---|---|---|---|
| `004194` | MATCH (×95%+（税后）×) | composite | benchmark_only | benchmark_only | benchmark_context | §2 page-5 page-5-table-1 |
| `005313` | MATCH (*95%＋（税后）*) | composite | benchmark_only | benchmark_only | benchmark_context | §2 page-5 page-5-table-1 |
| `017644` | MATCH (×95%+(税后)×) | composite | benchmark_only | benchmark_only | benchmark_context | §2 page-6 page-6-table-0 |
| `019918` | MATCH (*95%+（税后）*) | composite | benchmark_only | benchmark_only | benchmark_context | §2 page-5 page-5-table-1 |
| `019923` | MATCH (×95%＋×) | composite | benchmark_only | benchmark_only | benchmark_context | §2 page-6 page-6-table-0 |

All benchmark_text strings preserve exact punctuation from P16-S1 anchors (mixed `×`/`*`, mixed `（）`/`()`). All anchors match P16-S1 evidence. All `source_tier=benchmark_context`. All `confidence=high`.

### Excluded Subfields Review

Plan's "Do not add rows" table is correct:

| Subfield | Decision | Verified reason |
|---|---|---|
| `benchmark_index_name` | do not add | current value is `null`; strict Markdown requires non-empty expected value — verified in `golden_answer.py:608-609` |
| `benchmark_index_code` | do not add | current value is `null`; no accepted direct evidence |
| `benchmark_component_text` | do not add | tuple/list excluded by `_comparable_scalar()` — not in comparable whitelist |
| methodology/constituents summaries | do not add | extraction is out of scope |
| `missing_reasons` | do not add | tuple/list and not user-facing correctness denominator |
| any `tracking_error.*` | prohibited | P16-S1 blocked all five; verified in evidence artifact |

## Tracking Error Prohibition Review

Plan correctly prohibits all `tracking_error` rows. P16-S1 evidence confirms all five candidates are `blocked_no_direct_tracking_error`:

- `004194`: target/limit text + strategy narrative only
- `005313`: target/limit text only
- `017644`: strategy narrative without value
- `019918`: target/limit text + strategy narrative only
- `019923`: target/limit text + strategy narrative only

None satisfies the direct observed disclosure contract. Plan's rejection criteria and stop conditions correctly cover tracking-error pressure.

## File Ownership Review

Plan's file ownership is correctly scoped:

- `reports/golden-answers/golden-answer-prefill-reviewed.md` — append reviewed rows. **Verified**: no entries exist for the 5 fund codes currently.
- `reports/golden-answers/golden-answer.json` — rebuild through existing `golden-build` path.
- `docs/golden-answer-template.md` — optional scaffolding only.
- Source file changes allowed only if existing path cannot safely represent planned rows.
- Test files correctly scoped to composite benchmark semantics and correctness matching.

## Stop Conditions Review

Plan's 8 stop conditions are comprehensive and correctly cover:

- Extractor output divergence from P16-S1 values
- Identity/metadata reconciliation failures
- Comparable path representation limitations
- Active null/tuple golden assertion requirements
- `golden-build` rejection
- Correctness `no_comparable_fields`
- Direct PDF/cache access pressure
- Tracking-error / methodology / constituents / inferred identity pressure

**Verified**: Stop condition 3 ("current golden/comparable path cannot represent scalar index_profile rows without source changes beyond this plan") aligns with code fact that `_validate_active_row` rejects empty `expected_value`.

## Rejection Criteria Review

Plan's 10 rejection criteria are comprehensive. All correctly prevent the identified failure modes. Notably:

- Criterion 3 ("infers `benchmark_index_name` from product names, CSV names, benchmark family, or external sources") prevents the worst failure mode.
- Criterion 7 ("changes source/adapters, PDF cache, repository fallback behavior, Service/UI/Engine/renderer boundaries, or quality-gate severity to make golden rows pass") preserves module boundaries per AGENTS.md.

## Boundary Compliance Review

- Plan does not propose design.md or implementation-control.md edits. Correct.
- Plan does not propose source CSV or RR-13 edits. Correct.
- Plan does not propose commits, branches, PRs, or external state. Correct.
- Plan does not introduce Dayu runtime, Host, Engine, tool loop, LLM audit, or Evidence Confirm. Correct.
- Plan does not propose external index adapters, methodology extraction, or constituents extraction. Correct.
- README sync triggers correctly deferred to post-implementation. Correct.

## Test Coverage Gap

Plan correctly identifies that current tests lack composite benchmark scenarios. `tests/fund/test_golden_prefill.py` tests `index_profile` with `benchmark_index_name="测试指数"` (single benchmark). `tests/fund/test_extraction_score.py` correctness test verifies `benchmark_index_name="沪深300指数"` (single benchmark). Neither covers composite benchmarks with `benchmark_index_name=null`.

Plan's proposed test coverage is appropriate:

- `test_golden_answer.py` — strict Markdown/JSON accepts added rows
- `test_golden_prefill.py` — composite fixture should not synthesize `benchmark_index_name`
- `test_extraction_snapshot.py` — composite `IndexProfileValue` serializes comparable scalar fields, omits null/tuple
- `test_extraction_score.py` — correctness for five rows matches; `benchmark_index_name` absent for composite not treated as matchable
- `test_quality_gate.py` / `test_quality_gate_integration.py` — coverage stays non-blocking for absent null/tuple rows

## Residuals Review

Plan's 7 residuals are appropriate and correctly scoped:

- Full dataclass tuple/null production golden semantics — correctly deferred
- `tracking_error` production golden — correctly deferred to future evidence gate
- Index methodology / constituents extraction — correctly deferred to future source-contract phase
- Extractor semantics for composite benchmarks — correctly deferred
- Evidence Confirm / E1-E3 — correctly deferred
- RR-13 duplicate `016492` — correctly preserved as user-owned

## Findings

### F1: Untracked file validation gap in targeted validation commands

**Severity**: LOW

**Evidence**: Plan's "Targeted Validation Commands" section lists `git diff --check HEAD` but does not include whitespace or conflict-marker checks for the new untracked files that will be created (`reports/golden-answers/golden-answer-prefill-reviewed.md` edit, new test files, implementation artifact). P16-S1 code review (controller judgment) required explicit `git diff --no-index --check /dev/null <artifact>` and conflict-marker grep for untracked artifacts.

**Impact**: If implementation creates new files with trailing whitespace or conflict markers, `git diff --check HEAD` will not detect them. This is a validation gap inherited from P16-S1 pattern, not a plan design error.

**Required disposition**: Implementation artifact should include explicit whitespace and conflict-marker checks for all new/modified untracked files, matching the P16-S1 controller validation pattern. No plan revision required — this is an implementation-time validation enhancement.

### F2: Handoff prompt does not restate file ownership scope

**Severity**: INFO

**Evidence**: Plan's "Handoff Prompt For Future Implementation" says "Edit only the owned files required by the P16-S2 plan" but does not restate the exact file list from "File Ownership For Future Implementation." The file ownership table is clear and authoritative, but the handoff prompt relies on the implementer reading the full plan.

**Impact**: Minimal — the file ownership table is unambiguous and the handoff prompt references the plan document. An implementer who reads the plan will see the table.

**Required disposition**: No revision required. The handoff prompt correctly references the plan document as context.

## Conclusion

P16-S2 plan is well-structured, correctly grounded in P16-S1 evidence, and appropriately constrained. The first-principles decision to golden current `index_profile` benchmark-context scalar rows is sound. Composite benchmark handling with `benchmark_identity_status=composite` and `benchmark_index_name=null` is correctly reasoned. The proposed 25 rows exactly match P16-S1 accepted evidence. Stop conditions, rejection criteria, and residuals are comprehensive. One LOW finding on untracked file validation and one INFO finding on handoff prompt scope — neither requires plan revision.

Verdict: `PASS_WITH_FINDINGS`.
