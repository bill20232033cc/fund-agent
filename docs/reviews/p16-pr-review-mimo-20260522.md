# P16 PR Review — AgentMiMo（2026-05-22）

## Verdict

**PASS**

## PR Metadata

| Field | Value |
|---|---|
| PR URL | https://github.com/bill20232033cc/fund-agent/pull/10 |
| Title | P16 enhanced index profile golden rows |
| Base | main |
| Head | docs/post-p14-follow-up-planning |
| Draft | true |
| Merge State | CLEAN |
| CI | test — SUCCESS |
| Commits | 19 |
| Files Changed | 62 |

## Scope Alignment: PR Diff vs P16 Aggregate Accepted Scope

### P16-S1 Evidence Acquisition

PR diff includes `docs/implementation-control.md` (+93/-11) and `docs/design.md` (+552/-170) updates that record P16-S1 enhanced index evidence acceptance for `004194`, `005313`, `017644`, `019918`, and `019923`. No production code changes in this slice — correct, as P16-S1 was evidence-gating only.

**Aligned: YES**

### P16-S2.1 Newline Normalization

Commit `974615e` adds 138 lines to `fund_agent/fund/extractors/profile.py`:

- `_BENCHMARK_NEWLINE_RUN_PATTERN` matches PDF table visual newlines: `[ \t\f\v]*(?:\r\n|\r|\n)+[ \t\f\v]*`
- `_benchmark_newline_replacement` inserts space only between adjacent ASCII word chars; deletes otherwise
- `_normalize_benchmark_text` applies normalization with context-aware replacement
- `_normalize_benchmark_matched_field` synchronizes both `value` and `matched_line` (anchor note)
- Called only from `_build_benchmark`, scoped to benchmark path only

Normalization preserves composite semantics: `中证1000指数收益率×95%+同期银行活期存款利\n率(税后)×5%` → `中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%` (newline deleted, no space inserted between Chinese and Chinese).

**Aligned: YES**

### P16-S2 Golden Rows

Commit `121ad1f` adds:
- 25 `index_profile` scalar golden rows across 5 funds in `golden-answer.json`
- Strict JSON: `fund_count=11`, `record_count=150` (verified)
- 5 scalar sub-fields per fund: `benchmark_text`, `benchmark_identity_status`, `methodology_availability`, `constituents_availability`, `source_tier`
- `001548` preserved with 4 existing rows (verified: `benchmark_text`, `benchmark_identity_status`, `benchmark_index_name`, `source_tier`)
- No `tracking_error` golden rows added (verified: zero forbidden rows)
- No `benchmark_index_name`, `benchmark_index_code`, `benchmark_component_text` for composite funds (verified: no synthesis)
- No embedded `\n` or `\r` in any `expected_value` (verified: `newline_count=0`)

**Aligned: YES**

### Test Coverage

| Test file | Lines added | Key coverage |
|---|---|---|
| `tests/fund/extractors/test_profile.py` | +90 | 5 parametrized newline normalization cases, composite semantics preservation |
| `tests/fund/test_golden_answer.py` | +106 | 25 P16-S2 rows validated (scalar-only, composite no-synthesis, `001548` preservation) |
| `tests/fund/test_extraction_score.py` | +165/-1 | Composite index profile scalar match/mismatch correctness tests |
| `tests/fund/test_extraction_snapshot.py` | +82 | Composite comparable_values omits null/tuple fields |
| `tests/fund/test_quality_gate.py` | +56 | FQ1 blocking for composite index_profile scalar mismatch |

**Aligned: YES**

## PR-Only Issues

### 1. Bundled P15 Scope (Info)

PR title says "P16" but includes 10 P15 commits (tracking error evidence blocker, acquisition plan, acquisition). This is expected for a planning branch that accumulates phase work sequentially, and P15 was already aggregate-review accepted. Not a blocking issue, but the PR title could more precisely read "P15-P16 follow-up" for reviewers unfamiliar with the branch history.

**Severity: INFO**

### 2. Local Untracked Artifacts (Info)

Three untracked files exist locally but are NOT in the PR diff:
- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`

These are excluded inputs per the aggregate judgment and do not affect the PR. No action required.

**Severity: INFO**

### 3. Review Artifact Volume (Info)

55 of 62 changed files are `docs/reviews/` artifacts. This is expected for the phaseflow review protocol but creates a large diff. No code review concern — all artifacts are additive.

**Severity: INFO**

## Correctness / Stability / Maintainability

### Correctness

- Newline normalization is context-aware: ASCII word boundary detection prevents incorrect space insertion between Chinese characters
- Normalization is idempotent (only triggers when newlines are present)
- `_normalize_benchmark_matched_field` synchronizes value and anchor note — no drift possible
- Golden rows match production extractor output for all 5 enhanced-index candidates
- Composite `benchmark_index_name=null` is correctly maintained (no synthesis from benchmark text)

**No findings.**

### Stability

- Newline normalization is narrow: only `_build_benchmark` path, only benchmark text field
- No changes to `_extract_field`, `_extract_field_from_section_two_tables`, or any non-benchmark extraction path
- Pattern `_BENCHMARK_NEWLINE_RUN_PATTERN` handles `\r\n`, `\r`, `\n` with optional surrounding whitespace
- Edge case: if a future benchmark text has meaningful newlines between non-ASCII chars, normalization deletes them. Current production candidates have no such case. Accepted as low risk per aggregate judgment (GLM F3).

**No findings.**

### Maintainability

- All new functions are private (`_` prefix), module-scoped
- Helper functions (`_previous_non_space_char`, `_next_non_space_char`, `_is_ascii_word_char`) are generic and well-typed
- `test_profile.py` parametrization covers all 5 production candidates with exact expected values

**No findings.**

## External Side Effects

| Check | Result |
|---|---|
| README drift | None (no README changes) |
| GitHub issue/PR comment mutation | None |
| Forbidden golden rows (`tracking_error`) | None (verified: zero) |
| External dependencies added | None |
| Production contract changes | None |
| `extra_payload` pattern | None |
| Dayu runtime / Host / Engine | None |

## Residual Risks (Inherited from Aggregate Judgment)

| Risk | Status |
|---|---|
| `tracking_error` golden rows blocked for 001548 + 5 P16 candidates | Unchanged — no direct observed disclosure evidence |
| Composite `benchmark_index_name=null` / `benchmark_component_text` tuple semantics outside strict golden denominator | Unchanged — intentionally excluded from P16 |
| Future methodology/constituents extraction may need nuanced `missing_reasons` | Unchanged — current hardcoded values accepted |

## Validation Summary

| Check | Result |
|---|---|
| `gh pr checks 10` | test — SUCCESS |
| `gh pr diff 10 --name-only` | 62 files, all expected |
| `mergeStateStatus` | CLEAN |
| `golden-answer.json` fund_count | 11 |
| `golden-answer.json` record_count | 150 |
| `golden-answer.json` newline_count | 0 |
| Forbidden golden rows | 0 |
| Untracked files in PR | 0 |

## Next Gate

P16 PR review passed. PR is ready for draft PR authorization (merge to main).
